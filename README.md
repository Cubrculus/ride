# Reset Stations — SW/Central Florida Airport Hotels

A dataset, map and weekly plan for staging rideshare between airport queue cycles,
covering the I-75 corridor from Tampa to Naples.

## What's here

| Path | What it is |
|---|---|
| `data/airports.csv` | The six airports, with service type and realistic daily departure counts |
| `data/hotels.csv` | **Source of truth.** 59 hotels, scored A/B/C as reset stations |
| `data/hotels.json` | Generated. Same data plus resolved navigation links |
| `map/template.html` | The map's source (edit this, not `index.html`) |
| `map/index.html` | Generated. Self-contained interactive map |
| `plan/weekly-rotation.md` | Zone geography, demand clocks, seasonality, and a 4-week ramp |
| `scripts/build.py` | Validates the CSVs and regenerates the JSON + map |

## Regenerating

```
python3 scripts/build.py
```

Validates ids, airport codes, tiers, shuttle values, and that every coordinate falls
inside a Southwest Florida bounding box, then rewrites `data/hotels.json` and
`map/index.html`. It exits non-zero and prints every problem if the CSV is malformed,
so it is safe to run after hand-editing.

## Coverage

| Airport | City | Spots | Note |
|---|---|---|---|
| TPA | Tampa | 18 | Westshore — densest cluster in the region |
| PIE | Clearwater | 8 | Ulmerton Rd corridor |
| SRQ | Sarasota | 9 | University Pkwy + downtown |
| RSW | Fort Myers | 8 | Chamberlin Pkwy + Daniels corridor |
| PGD | Punta Gorda | 5 | Jones Loop Rd |
| APF | Naples | 11 | 5th Avenue South cluster |

Radius is 3 miles from the terminal, with deliberate exceptions noted per row —
RSW has no hotels inside 2 miles, and a few high-value properties just outside the
ring (Ritz-Carlton Sarasota, Naples Grande) earn their place on fare size.

## Honest limits — read this before trusting a row

**The A/B/C tiers are a model, not measurements.** They are inferred from four
structural proxies: room count, shuttle coverage, service class, and distance.
No live or historical surge data was used, because none is publicly available.
The reasoning behind each tier is written into the `notes` column so you can
disagree with it specifically rather than in general.

**Street addresses are partly unverified.** The environment this was built in could
not reach mapping or hotel APIs, so addresses come from search corroboration plus
prior knowledge. Rows carry an `addr_confidence` of high/medium/low, and the map
flags the low ones. To make this harmless in practice, **navigation links resolve by
hotel name + city, not by the stored street address** — brand hotel names near an
airport are unambiguous in Maps, so a wrong house number can never misroute you.

**Coordinates are approximate** and exist only to give the range-ring plot a bearing.
Each hotel's plotted radius comes from the `dist_mi` column, so the rings stay
consistent with the stated distances even where a coordinate is loose.

**Room counts are approximate** (`rooms_approx`), rounded to the nearest sensible
figure and used as a relative weight, not a fact.

The intent is that your own driving log replaces this model within a few weeks.
Add an observed-results column and re-rank; the structure is here to give you a
starting hypothesis and a route around the area, not a final answer.
