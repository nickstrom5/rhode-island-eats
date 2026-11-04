# Rhode Island Eats (ri-eats) — notes for Claude Code sessions

Built 2026-11-03 by a side session while Nick was away, ported from `../ga-eats/` (the newest state) with the 10-29 all-states QA
P0/P1 fixes in from the start. Local only: no git repo, no remote, nothing published. Sources and calibration:
`playbook/12-sources.md`. Brand: `playbook/05-naming.md` — **provisional**, every choice waits for Nick ("Rhode Island Eats:
Restaurants", Home Screen "RI Eats", coffee-milk icon B on Hope blue, flag palette: Hope blue #1D3F73, bay teal #1C6670, anchor gold
#F2C14E fill only, sea-salt #F7F5EF; bay swells over a gold sand strip).

## Rhode Island is different
- **Towns, not counties.** RI's five counties have no government, so the 39 cities and towns are the unit everywhere ("counties" in
  the data files holds towns). `pipeline/fetch_rigis.py` writes the town and state outlines from RIGIS Municipalities (1997), every
  island kept (Block Island, Aquidneck, Conanicut, Prudence, Patience, Hope, Dutch). A listing's town is the polygon its point falls
  in; a village locality (Wakefield, Galilee, Chepachet, Block Island for New Shoreham) is kept as `village` and is searchable.
- **No current official food list a script may read.** health.ri.gov's lists answer a Cloudflare challenge (never worked around);
  Nick could download the food service list by hand into `data/raw/official/ridoh/` (then `official.py` needs a loader). Until then
  `on_an_official_list` is 0, "Serves alcohol" is "—" everywhere (liquor licenses are per town), and the keep rule is the
  calibrated map-data rule alone.
- RIDOH's 2018 L2K export (`official.load_l2k()`) is **calibration only**: never shown, never keeps or names a place. Its owner and
  manager fields were never requested.
- RIGIS Licensed Food Markets (2025) marks grocery counters: a listing at a market's street address under the market's own name is
  hidden as a store (`rhodeisland.py at_market()`), unless hand-checked.
- Inspections: RIDOH, statewide, no score or grade; every place links `ri.healthinspections.us/ri/`. Never harvested.
- MICHELIN has no Rhode Island page (404). James Beard: 6 (`data/research/jbf.json`).

## Rebuild
```bash
cd pipeline
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_rigis.py && ../.venv/bin/python fetch_extras.py
../.venv/bin/python listings.py && ../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py
../.venv/bin/python calibrate.py && ../.venv/bin/python build_research.py && ../.venv/bin/python rhodeisland.py
RI_APP=1 ../.venv/bin/python rhodeisland.py && cd .. && cp data/app/places.json data/app/detail-*.json RhodeIslandEats/Resources/
.venv/bin/python pipeline/check_websites.py --retry-transient   # link verification; re-export after
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
- Shared code copied as-is from the newest state: `tracking_params.py`, `publish_app_data.py`, `website_blocklist.json` (the union of
  every state's, minus "another business" entries), the widened adult-venue rule (OH + TX, 11-03) and the delivery-brand `STORE`
  rule (Burger Den, Banda Burrito, The Meltdown, Tenderfix, Pardon My Cheesesteak, Neighborhood Wings; anchored because
  `norm_name` drops a leading "THE").
- Guides (`build_research.py`, each entry with a dated 2025-26 source on a robots-allowed host): hot wieners, clam shacks and
  stuffies, Federal Hill, pizza strips, Portuguese, frozen lemonade and creameries, oldest. Misses and blocked hosts:
  `data/research/app/LEADS.md` (diners and Cape Verdean kitchens need 2025-26 sources).

## App, site, screenshots
- App: `RhodeIslandEats/` (XcodeGen `project.yml`, bundle `com.rhodeislandeats.ios`), tests in `RhodeIslandEatsTests/` (data guards:
  adult venues, blocklisted and multi-URL websites, bad and legal names, non-restaurants, listed twice, no Google data). Run tests:
  `DEVELOPER_DIR="/Applications/Xcode 1.app/Contents/Developer" xcodebuild test ... CODE_SIGNING_ALLOWED=NO` on a temporary simulator.
  Archive only with Xcode 1.app (27.1, 27A9275); Xcode.app is a beta.
- Site: `scripts/make-site.py` writes `docs/` (16 pages, CSP) and `playbook/site-numbers.json`; `scripts/explore.js` is the web app;
  `scripts/qa-site.py` the QA. Site URL for now: nickstrom5.github.io/rhode-island-eats (no CNAME).
- OTA data: `docs/data/app/` via `scripts/publish_app_data.py` (`../OTA-DATA.md`).
- Screenshots: `scripts/capture-screenshots.sh <sim>` (ScreenshotMode pins downtown Providence, Galilee for clams, Atwells Avenue
  for fedhill), then `scripts/site-images.sh`, then make-site + qa-site. App Store frames: `scripts/appstore-screenshots.py`.
  Rebuild the site before the unit tests: `ShareLinkTests` reads the web app's ids from `docs/`. Run `xcodegen generate` whenever
  the set of `Resources/*.json` files changes (the project lists only the files it found).
- Last run 2026-11-04: 48 unit tests passed (temporary iPhone 17 Pro Max, iOS 27.0, Xcode 1.app); screenshots from the same data.
- Not ported: the App Store listing writer (`make-listing.py`) and the private Google-2021 leaderboard (`make-leaderboard.py`).
  `site/` holds the leaderboard's data and is git-ignored with `data/`.

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.
