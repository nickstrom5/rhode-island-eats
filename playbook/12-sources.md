# Rhode Island sources (checked 2026-11-03)

Every host below was robots-checked with `pipeline/check_sources.py` (ClaudeBot, Claude-User and anthropic-ai; RFC 9309 matcher) in
its own step, before any other request. User agent on every scripted request: `RhodeIslandEatsBuild/1.0 (+nick@eatsranked.com)`.
Raw files are in `data/raw/official/` (git-ignored, never public).

Rhode Island has one food inspector and no official grade, and its current food lists are out of reach for a script. The app is
built from open map listings, calibrated against the Department of Health's own (2018) license export, with RIGIS's 2025 market
list marking grocery counters and RIGIS town outlines giving each place its town.

## Inspections: one inspector, no grade (linked, never copied)

- **Who inspects:** the Rhode Island Department of Health (RIDOH), Center for Food Protection, statewide under the RI Food Code
  (216-RICR-50-10-1). No city or town runs its own program (the prompt's research, 2026-09-27; nothing found since says otherwise).
- **What a report says:** violations by FDA Food Code item, marked corrected on site or with a "correct by" date, and a count of
  foodborne-illness risk factors. **No score, grade or placard**, so the app and site compute none and copy none.
- **Where:** `ri.healthinspections.us/ri/` (Tyler Technologies' search app; robots: no file, usable). Search-only, no export, no
  reuse terms: **not harvested**. Every place links the search; the home page answers 200.
- **Bulk data:** none open. A records request under the Access to Public Records Act (R.I. Gen. Laws § 38-2) for a statewide
  extract is the clean route; drafting it is Nick's call (nothing sent).

## Official records

| Source | What | Terms | Status |
|---|---|---|---|
| **RIDOH "Download Food Service Lists"** (`health.ri.gov/lists/licensees/`) and "Find Licensed Restaurants" | The current food service license list (FSV numbers, seat-count types) | — | **blocked**: robots.txt allows, but every request (2026-11-03, one honest GET) answered `403` with a Cloudflare "Just a moment..." challenge. Never solved or worked around. **Nick could download the list by hand** into `data/raw/official/ridoh/`; `official.py` would then need a loader for its columns, and the export could mark places official. |
| `healthri.mylicense.com/verification/` | License lookup | — | search-only; not used |
| `data.ri.gov` | State open data portal | — | `403` bot check at robots.txt; not used |
| **RIGIS "Licensed Food Markets (2025)"** (ArcGIS item `e3f9a20ca91d4098b2220f186910baaa`; FeatureServer `services2.arcgis.com/S8zZg9pg23JUEexQ/.../FACILITY_Licenced_Food_Markets_2025`) | 471 market licenses (MRK numbers), all "Active": cash-register size or non-profit type, chain flag, physical address, town, ZIP. No point (X/Y are 0). Edited 2026-04-29. | RI Division of Statewide Planning, "as is"; "acknowledge both RIGIS and the primary producer" | **used**: placed by Overture address points (405) and the Census geocoder (54; 12 unplaced). A listing at a market's street address under the market's own name is hidden as a store (17 places: fish markets, candy shops, Latin and Indian groceries, Tony's Colonial). Hand-checked places stay shown. |
| **RIDOH "L2K Food Facilities"** (owner RIDOHGIS, `services1.arcgis.com/dkWT1XL4nglP5MLP/.../L2K_Food_Facilities_080520`) | RIDOH's licensing-system export of February 2018 (layer last edited 2020-08-05): 27,316 licenses; 23,227 food service and market rows, 3,317 seated food service licenses active then, 19,699 with a geocoded point. **Also carries owners' and managers' names, emails and phones: the download asked for none of those fields.** | Public layer, no terms stated | **calibration only** (8 years old): never shown, never used to keep, add or name a place |
| Providence "Active Business Licenses" (`data.providenceri.gov ui7z-kv69`) | City licenses with liquor flags | — | not used: the dataset says it's no longer updated (rows last changed December 2021) |
| DBR / town liquor licenses (`dbr.ri.gov`, `elicensing.ri.gov`) | Liquor licenses are issued by each city or town; DBR's lookup is search-only | — | not used: no statewide list. **"Serves alcohol" is "—" everywhere** (unknown, never "no"). |
| Property values | Towns assess on vendor sites | — | skipped (no building-value board) |

## Statewide base, outlines and towns

| Source | What | Terms | Rows |
|---|---|---|---|
| Overture Maps places `2026-10-21.0` (newest release on 2026-11-03) | Map listings | CDLA-Permissive-2.0 / Apache-2.0 + Foursquare NOTICE | 5,874 Rhode Island eating/drinking listings (333 marked closed) |
| Overture addresses `2026-10-21.0` | 391,461 Rhode Island address points (E-911 sites) | open address sources, docs.overturemaps.org/attribution | places the market list and researched addresses |
| **RIGIS "Municipalities (1997)"** (`BND_Municipalities_1997_spf`, 396 land polygons) | The 39 cities and towns, **every island kept**: Block Island (New Shoreham), Aquidneck (Newport, Middletown, Portsmouth), Conanicut (Jamestown), Prudence, Patience, Hope, Dutch Island | RIGIS, "as is" | `pipeline/fetch_rigis.py` writes the town and state outlines (`data/ri/ri_*`); each listing's town is the municipality its point falls in, and the listing's own locality, when it's a village (Wakefield, Galilee, Riverside, Chepachet, Block Island), is kept and searchable |
| US Census batch geocoder | Address to point | Public domain | 54 of the 66 markets the address points missed |
| UCSD Google Local 2021 (`meta-Rhode_Island.json.gz`, 3.5 MB) | 2021 ratings/reviews/price: **private web leaderboard only, never the app or site** | research dataset | 3,719 food listings (441 closed by 2021); 2,842 matched |
| BLS QCEW, private NAICS 722, 2025 (from the prompt) | 3,078 establishments | public | benchmark: the app keeps 2,828 restaurants |

## Calibration (2026-11-03, `data/ri/calibration*.json`)

Measured against RIDOH's 2018 seated food service licenses (2,895 placed), town by town. Old list, so the shares favor places that
have been around; they compare kinds of listing, not rates of real restaurants. The share Google 2021 still showed open is the
second check (web build only; the app ships no Google-derived number).

| Kind of listing (app grouping) | On a 2018 RIDOH seated license | Open in Google 2021 |
|---|---|---|
| Meta >= 0.95 | 44.8% of 2,413 | 69.2% |
| Meta 0.90-0.95 with a website | 28.0% of 489 | 50.3% |
| Meta 0.90-0.95, no website | 9.8% of 102 | 12.7% |
| Meta < 0.90 | 4.4% of 634 | 5.5% |
| Chain store lists (AllThePlaces, DAC) | 14.5% of 55 | 10.9% |
| BrightQuery >= 0.95 | 31.8% of 490 | 35.9% |
| Other sources (Foursquare, Microsoft, ...) | 28.4% of 1,341 | 29.8% |

Web grouping: Meta + open in Google 2021 56.4%, Meta only 8.2%, Foursquare only 11.7%, BrightQuery only 10.2%, Microsoft only 16.2%.
Same order as Georgia, Colorado, Texas and Idaho, so the same keep rules: **app** = Meta >= 0.95, Meta 0.90-0.95 with a website, chain
store lists, hand-checked (2,955 kept, 2,828 restaurants after merges and non-restaurant flags); **web** = Meta and chain store
lists minus what Google showed closed in 2021 (3,434 restaurants). Coverage the other way: open map listings hold 56.6% of the 2,895
placed 2018 licenses.

## Honors and guides

- **MICHELIN:** none. `guide.michelin.com/us/en/rhode-island/restaurants` answered 404 (read through Claude's fetcher, 2026-11-03).
- **James Beard** (`data/research/jbf.json`, written by `build_research.py`): America's Classics Aunt Carrie's (2007) and
  Olneyville New York System (2014) (Wikipedia's list of America's Classics); Gift Horse, Sky Haneul Kim, Best Chef: Northeast 2025
  (RI Monthly, Ocean State Media); Loma, Best New Bar 2026 (jamesbeard.org's 2026 winners); Nicks on Broadway, Derek Wagner, Best
  Chef: Northeast finalist 2026 (Ocean State Media, 2026-03-31); Al Forno, George Germon and Johanne Killeen, Best Chef: Northeast
  1993 (jamesbeard.org's obituary of Germon).
- **Hand-checked guides** (`pipeline/build_research.py`; every source dated 2025-26 on its face, robots-checked): hot wieners 6
  (RI Monthly 2026-07-15), clam shacks and stuffies 13 (South County Tourism 2025-08-06, Ocean State Media 2026-06-12, RI Monthly
  2026), Federal Hill Italian 7 (RI Monthly's 2026 summer list), pizza strips 3, Portuguese 3, frozen lemonade and creameries 26
  (Del's and Newport Creamery brand-wide from Ocean State Media 2026-06-12, plus 8 scoop shops), oldest 3 (White Horse Tavern 1673,
  Tasting Table 2025-09-23; Aunt Carrie's 1920; Olneyville 1946). Closed: the Old Canteen (RI Monthly 2025-05-23).
- Leads and blocked hosts: `data/research/app/LEADS.md` (diners, Cape Verdean kitchens and more need 2025-26 sources).
- Blocked or unusable: providencejournal.com, bostonglobe.com, boston.com, turnto10.com, wpri.com, saveur.com, theinfatuation.com
  (robots); rhodybeat.com, eastbayri.com, data.ri.gov, health.ri.gov (bot checks); golocalprov.com (403 to Claude's fetcher).
