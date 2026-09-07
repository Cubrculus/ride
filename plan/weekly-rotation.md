# Weekly Rotation Plan — SW/Central Florida Airport Hotel Reset Stations

## The core idea

A *reset station* is not where you wait for an airport ping. It is where you park
between airport queue cycles so that the odds of a ping finding you are as high as
possible, in a spot you can leave quickly toward the next likely trip.

That means the best reset stations are **not** the hotels closest to the terminal.
They are hotels that combine:

1. **No shuttle, or a shuttle with dead hours.** A hotel running a free 24/7 shuttle
   has already absorbed the airport run you wanted. The gold is a hotel whose shuttle
   stops at 22:00 and restarts at 05:00 — everything outside that window is yours.
2. **High room count.** Volume beats proximity. A 489-room DoubleTree two miles out
   generates more pings than a 94-room extended-stay next door.
3. **Full-service / restaurant-heavy.** Those guests take evening trips, not just
   morning airport runs, so the spot pays twice a day.
4. **A fast exit toward the airport.** Being able to reach the terminal in under
   ten minutes means you can accept an airport ping without dropping your position.

The dataset scores every hotel A/B/C on those four factors. `data/hotels.csv` is the
source of truth; the map renders it.

## Two demand clocks, not one

Airport hotel demand has two separate peaks, and they want different behavior:

| Clock | Window | What is happening | Where to be |
|---|---|---|---|
| **Morning outbound** | 04:00–07:30 | Guests leaving for departure banks | Parked at an A-tier hotel lot |
| **Evening dining** | 17:30–22:30 | Guests going to dinner / downtown | Parked at a full-service or resort hotel |

Between roughly 08:00 and 17:00, airport hotels are quiet. That midday gap is when
the airport queue itself, not the hotels, is the right place to be — or when you take
your break. **Do not spend midday sitting in a hotel lot.** That is the single most
common way drivers burn a shift in this region.

## Seasonality — this dominates everything south of Sarasota

Southwest Florida is the most seasonal rideshare market in the state.

- **Season (Jan–Apr):** RSW, APF and SRQ run hot. Naples and Marco fill up. RSW
  departure banks start brutally early — 04:00 hotel pickups are normal. This is when
  the southern zones out-earn Tampa.
- **Shoulder (Oct–Dec, May):** Mixed. Tampa steady, south ramping or fading.
- **Off (Jun–Sep):** The south largely empties out. Naples restaurants close for the
  summer. **Tampa and St. Pete carry the whole region.** Do not drive to Naples in
  July expecting hotel surge — it will not be there.

**Right now (September) you are at the bottom of the off-season.** Weight your week
heavily toward TPA/PIE, and treat the southern zones as familiarization runs rather
than earnings runs until roughly November.

## Zone geography

You cannot work Tampa and Naples in the same shift. The corridor is ~150 miles
end to end. Block your days by zone:

| Zone | Airports | Drive time between | Base for the day |
|---|---|---|---|
| **North** | TPA + PIE | ~25 min | Westshore, Tampa |
| **Central** | SRQ | — | University Pkwy, Sarasota |
| **South** | RSW + PGD | ~30 min | Chamberlin Pkwy, Fort Myers |
| **Far South** | APF | ~35 min from RSW | 5th Ave S, Naples |

TPA→SRQ is ~55 min. SRQ→RSW is ~70 min. Treat any zone change as a commit for
the whole day.

## Four-week familiarization ramp

You said you want to learn the area, not just chase surge. Learning one zone properly
beats skimming all six. Work it in this order — easiest and highest-volume first:

**Week 1 — TPA / Westshore only.** Do not leave the Westshore block. Learn every
approach: which lots you can legally sit in, which hotels have a covered porte-cochère
you can wait under, how to get from Cypress St to the terminal without the Boy Scout
Blvd backup. Westshore is the densest cluster in the region; mastering it is worth
more than knowing all six zones shallowly.

**Week 2 — TPA + PIE.** Add the Ulmerton Rd corridor. Learn the Allegiant schedule at
PIE — it is only ~25 departures a day, so demand is entirely bank-driven. Note when
the banks are; the rest of the day PIE is dead.

**Week 3 — SRQ.** Small, walkable-scale zone. Learn the University Pkwy hotels and the
downtown Sarasota cluster ~3 mi south, and how the two feed each other (airport
arrivals in the afternoon, downtown dinner runs in the evening).

**Week 4 — RSW + Naples.** The longest drives and the most seasonal. Go now to learn
the roads while it is quiet, so you are fluent when season starts in January.

## Steady-state weekly template (off/shoulder season — use now)

| Day | Zone | 04:30–08:00 | Midday | 17:30–22:30 |
|---|---|---|---|---|
| **Mon** | North | Westshore A-tier (tpa-02, tpa-05, tpa-03) | Airport queue / break | Westshore full-service |
| **Tue** | North | Westshore A-tier | Airport queue / break | Westshore + Midtown |
| **Wed** | North | Westshore A-tier | Airport queue / break | Grand Hyatt / Renaissance |
| **Thu** | North | PIE Ulmerton corridor early bank | Airport queue / break | Carillon Park (pie-03) |
| **Fri** | Central | SRQ University Pkwy (srq-01, srq-02) | Break | Downtown Sarasota (srq-05, srq-06) |
| **Sat** | Central/North | SRQ morning | Reposition to TPA | Westshore evening |
| **Sun** | North | Westshore (heavy business fly-in evening) | Break | TPA arrivals queue |

Monday morning and Thursday/Friday evening are the two strongest slots in this
template. Sunday evening is the business-traveler fly-in — the airport queue beats
the hotels then.

## Season template (Jan–Apr — switch to this around January)

| Day | Zone | 04:00–07:30 | Evening |
|---|---|---|---|
| **Mon–Wed** | South | RSW Chamberlin cluster (rsw-01, rsw-02) | Naples 5th Ave S (apf-02, apf-03, apf-04) |
| **Thu** | South | RSW | Naples Grande / Hilton Naples |
| **Fri–Sat** | Central | SRQ + downtown Sarasota | Ritz-Carlton Sarasota (srq-06) |
| **Sun** | North | Back to Westshore | TPA arrivals |

In season, the Naples 5th Avenue South block (apf-02/03/04) is the highest
fare-per-trip cluster in the entire dataset. It is worth the deadhead from RSW on
any evening between January and April. It is worth nothing in August.

## Airport-specific cautions

- **APF (Naples Municipal) has no scheduled airline service.** It is a general
  aviation field. Private jet passengers overwhelmingly use pre-booked car services,
  not rideshare. Do not stage at the airfield expecting flight-driven demand — the
  value in the Naples zone is entirely the downtown hotel and restaurant cluster.
- **PGD (Punta Gorda) is Allegiant-only,** roughly eight departures a day. Demand is
  all-or-nothing around published bank times. Check the day's schedule before
  committing to the zone; outside the banks there is nothing.
- **RSW has no hotels inside 2 miles.** The airfield is isolated. The real cluster is
  Chamberlin Pkwy (~2.2 mi) and the Daniels Pkwy corridor (~3.6 mi). The dataset
  includes the Daniels properties despite being outside the 3-mile rule, because a
  strict 3-mile ring at RSW would return almost nothing.
- **TPA in-terminal Marriott (tpa-01)** never generates airport runs — guests walk.
  It is an evening dining spot only.

## How to use the data

- `data/hotels.csv` — source of truth, edit this.
- `python3 scripts/build.py` — validates and regenerates the map data.
- `map/index.html` — the interactive map; filter by airport and tier, tap to navigate.

Log what actually happens. The A/B/C tiers here are **inferred from structural
proxies** (room count, shuttle coverage, service class, distance), not from observed
surge data. Add a column for your own observed results and promote or demote spots
after a few weeks. Your log will beat this model quickly — that is the intent.
