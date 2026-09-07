#!/usr/bin/env python3
"""Fetch real flight-bank windows per airport via the Gemini API (with Google
Search grounding) and write data/signals.json.

Surge itself is not published anywhere — this does NOT fetch surge. What it
fetches is real, citable structure: when each airport's flights actually
depart and arrive, by weekday vs weekend. The app already assumes generic
04:00-10:00 morning / 17:00-23:00 evening banks and a hand-written
day-of-week prior (app/template.html: dowFactor); this replaces the generic
assumption with the airport's real schedule wherever Gemini can find one,
and leaves the generic model untouched wherever it can't.

Requires GEMINI_API_KEY in the environment. Get one at
https://aistudio.google.com/apikey — it's free for this volume of calls.

Usage:
    GEMINI_API_KEY=... python3 scripts/fetch_signals.py
    GEMINI_API_KEY=... python3 scripts/fetch_signals.py --airports TPA,PIE
    python3 scripts/fetch_signals.py --dry-run TPA   # print prompt, call nothing

Run via `python3 scripts/build.py` afterward to fold the result into the app.
"""
import argparse, csv, json, os, re, sys, time, urllib.error, urllib.request, pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIGNALS_PATH = ROOT / "data" / "signals.json"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
MAX_AGE_DAYS = 45          # older entries are dropped rather than trusted stale
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

PROMPT_TMPL = """You are researching REAL, current airline schedule data for one airport, \
using web search. Airport: {name} ({iata}), {city}, Florida, USA.

I need typical DEPARTURE bank windows (when outbound flights cluster — this is \
when hotel guests near the airport need a ride TO the terminal) and typical \
ARRIVAL bank windows (when inbound flights cluster — this is when guests need \
a ride FROM the terminal or later that evening), separately for a TYPICAL \
WEEKDAY and a TYPICAL WEEKEND day. Use real published airline schedules \
(airline sites, FlightAware, FlightRadar24, the airport's own flight board) \
for the current season, not guesses.

If this airport has very few scheduled flights (a handful of departures a \
day, or none), say so honestly in "notes" and give your best single window \
rather than inventing multiple banks.

Respond with ONLY a single fenced ```json code block containing exactly this \
shape, times as 24-hour "HH:MM" strings, at most 4 windows per list:

```json
{{
  "iata": "{iata}",
  "as_of": "YYYY-MM-DD",
  "confidence": "high|medium|low",
  "weekday": {{"departure_banks": [["HH:MM","HH:MM"]], "arrival_banks": [["HH:MM","HH:MM"]]}},
  "weekend": {{"departure_banks": [["HH:MM","HH:MM"]], "arrival_banks": [["HH:MM","HH:MM"]]}},
  "notes": "one or two sentences, cite what kind of source you used"
}}
```
"""

def load_airports():
    with open(ROOT / "data" / "airports.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def call_gemini(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.1},
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def extract_json(gemini_response):
    try:
        parts = gemini_response["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"unexpected Gemini response shape: {e}")
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not m:
        m = re.search(r"(\{.*\})", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON found in response: {text[:200]!r}")
    return json.loads(m.group(1))

def validate_banks(day):
    if not isinstance(day, dict):
        raise ValueError("day entry is not an object")
    for key in ("departure_banks", "arrival_banks"):
        wins = day.get(key, [])
        if not isinstance(wins, list) or len(wins) > 4:
            raise ValueError(f"{key}: expected a list of at most 4 windows")
        for w in wins:
            if not (isinstance(w, list) and len(w) == 2 and all(TIME_RE.match(str(x) or "") for x in w)):
                raise ValueError(f"{key}: bad window {w!r}")
    return {"departure_banks": day.get("departure_banks", []), "arrival_banks": day.get("arrival_banks", [])}

def validate_entry(entry, iata):
    if entry.get("iata") != iata:
        raise ValueError(f"iata mismatch: asked for {iata}, got {entry.get('iata')!r}")
    datetime.strptime(entry["as_of"], "%Y-%m-%d")  # raises if malformed
    if entry.get("confidence") not in ("high", "medium", "low"):
        raise ValueError(f"bad confidence {entry.get('confidence')!r}")
    return {
        "iata": iata,
        "as_of": entry["as_of"],
        "confidence": entry["confidence"],
        "weekday": validate_banks(entry["weekday"]),
        "weekend": validate_banks(entry["weekend"]),
        "notes": str(entry.get("notes", ""))[:400],
    }

def fetch_one(api_key, airport, retries=2):
    prompt = PROMPT_TMPL.format(name=airport["name"], iata=airport["iata"], city=airport["city"])
    last_err = None
    for attempt in range(retries + 1):
        try:
            raw = call_gemini(api_key, prompt)
            return validate_entry(extract_json(raw), airport["iata"])
        except (urllib.error.URLError, ValueError, KeyError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"{airport['iata']}: {last_err}")

def prune_stale(signals):
    cutoff = datetime.now(timezone.utc).date()
    kept = {}
    for iata, entry in signals.items():
        try:
            age = (cutoff - datetime.strptime(entry["as_of"], "%Y-%m-%d").date()).days
        except (KeyError, ValueError):
            continue
        if age <= MAX_AGE_DAYS:
            kept[iata] = entry
        else:
            print(f"  dropping stale {iata} (as_of {entry.get('as_of')}, {age}d old)")
    return kept

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--airports", help="comma-separated IATA codes to refresh (default: all)")
    ap.add_argument("--dry-run", metavar="IATA", help="print the prompt for one airport and exit, no API call")
    args = ap.parse_args()

    airports = load_airports()
    if args.dry_run:
        a = next((a for a in airports if a["iata"] == args.dry_run.upper()), None)
        if not a:
            sys.exit(f"unknown airport {args.dry_run!r}")
        print(PROMPT_TMPL.format(name=a["name"], iata=a["iata"], city=a["city"]))
        return 0

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "GEMINI_API_KEY is not set.\n"
            "Get a free key at https://aistudio.google.com/apikey, then:\n"
            "  export GEMINI_API_KEY=...\n"
            "  python3 scripts/fetch_signals.py\n"
            "(In CI this comes from the GEMINI_API_KEY repository secret — see\n"
            " .github/workflows/fetch-signals.yml.)"
        )

    wanted = {c.strip().upper() for c in args.airports.split(",")} if args.airports else None
    targets = [a for a in airports if not wanted or a["iata"] in wanted]
    if not targets:
        sys.exit(f"no matching airports for --airports {args.airports!r}")

    existing = {}
    if SIGNALS_PATH.exists():
        try:
            existing = json.loads(SIGNALS_PATH.read_text(encoding="utf-8")).get("airports", {})
        except json.JSONDecodeError:
            pass

    ok, failed = {}, []
    for a in targets:
        print(f"Fetching {a['iata']} ({a['name']})...")
        try:
            ok[a["iata"]] = fetch_one(api_key, a)
            print(f"  confidence={ok[a['iata']]['confidence']} as_of={ok[a['iata']]['as_of']}")
        except RuntimeError as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            failed.append(a["iata"])

    merged = {**existing, **ok}
    merged = prune_stale(merged)
    if not merged:
        sys.exit("no usable signals (all fetches failed or all entries stale) — nothing written")

    SIGNALS_PATH.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": MODEL,
        "source": "gemini-google-search-grounding",
        "airports": merged,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {SIGNALS_PATH.relative_to(ROOT)} ({len(merged)} airports).")
    if failed:
        print(f"Failed: {', '.join(failed)} (kept prior data if any, else omitted)", file=sys.stderr)
    print("Run `python3 scripts/build.py` to fold this into the app.")
    return 1 if failed and not ok else 0

if __name__ == "__main__":
    sys.exit(main())
