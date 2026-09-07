#!/usr/bin/env python3
"""Validate hotels.csv/airports.csv and emit map/data.js for the surge map."""
import csv, json, sys, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
VALID_TIER = {"A", "B", "C"}
VALID_SHUTTLE = {"none", "free", "limited_hours"}
VALID_CONF = {"high", "medium", "low"}

def load(name):
    with open(ROOT / "data" / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def nav_url(name, city):
    """Navigate by NAME + city, not by our stored street address.

    Street addresses here are partly from memory and unverified; brand hotel
    names near an airport are unambiguous and resolve correctly in Maps. This
    keeps a wrong digit in an address from ever sending the driver astray.
    """
    q = urllib.parse.quote_plus(f"{name}, {city}, FL")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

def main():
    airports = load("airports.csv")
    hotels = load("hotels.csv")
    codes = {a["iata"] for a in airports}
    errs = []
    seen = set()

    for h in hotels:
        hid = h["id"]
        if hid in seen:
            errs.append(f"{hid}: duplicate id")
        seen.add(hid)
        if h["airport"] not in codes:
            errs.append(f"{hid}: unknown airport {h['airport']!r}")
        if h["surge_tier"] not in VALID_TIER:
            errs.append(f"{hid}: bad surge_tier {h['surge_tier']!r}")
        if h["shuttle"] not in VALID_SHUTTLE:
            errs.append(f"{hid}: bad shuttle {h['shuttle']!r}")
        if h["addr_confidence"] not in VALID_CONF:
            errs.append(f"{hid}: bad addr_confidence {h['addr_confidence']!r}")
        try:
            lat, lon = float(h["lat"]), float(h["lon"])
            # Southwest/Central Florida bounding box sanity check.
            if not (25.8 < lat < 28.3) or not (-82.9 < lon < -81.5):
                errs.append(f"{hid}: coords {lat},{lon} outside the SW Florida box")
        except ValueError:
            errs.append(f"{hid}: non-numeric coords")
        try:
            float(h["dist_mi"]); int(h["rooms_approx"])
        except ValueError:
            errs.append(f"{hid}: non-numeric dist_mi/rooms_approx")

    if errs:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        return 1

    for h in hotels:
        h["lat"] = float(h["lat"]); h["lon"] = float(h["lon"])
        h["dist_mi"] = float(h["dist_mi"]); h["rooms_approx"] = int(h["rooms_approx"])
        h["nav"] = nav_url(h["name"], h["city"])
    for a in airports:
        a["lat"] = float(a["lat"]); a["lon"] = float(a["lon"])
        a["daily_departures_approx"] = int(a["daily_departures_approx"])

    payload = {"airports": airports, "hotels": hotels}
    (ROOT / "data" / "hotels.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Guard against a "</script>" inside data prematurely closing the tag.
    blob = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    for page in ("map", "app"):
        tpl_path = ROOT / page / "template.html"
        if not tpl_path.exists():
            continue
        tpl = tpl_path.read_text(encoding="utf-8")
        if "/*__DATA__*/null" not in tpl:
            print(f"ERROR: {page}/template.html is missing the /*__DATA__*/null marker", file=sys.stderr)
            return 1
        (ROOT / page / "index.html").write_text(tpl.replace("/*__DATA__*/null", blob), encoding="utf-8")
        print(f"  rendered {page}/index.html")

    print(f"OK: {len(hotels)} hotels across {len(airports)} airports")
    for code in [a["iata"] for a in airports]:
        sub = [h for h in hotels if h["airport"] == code]
        tiers = "".join(sorted(h["surge_tier"] for h in sub))
        print(f"  {code}: {len(sub):2d} hotels  tiers={tiers}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
