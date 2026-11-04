"""Rhode Island's town and state outlines from RIGIS -> data/ri/ (run after fetch_overture.py, whose outlines these replace)

- ri_shapes.json             simplified state and town outlines for the map ("counties" holds the 39 cities and towns: Rhode Island's
                             counties have no government, so towns are the unit everywhere)
- ri_state_detail.geojson    the state's land at full detail, for the in-state test
- ri_counties_detail.geojson each town's land at full detail, for assigning a place to its town
- ri_town_county.json        town -> county (the five counties, for the record only)

Source: RIGIS "Municipalities (1997)" (BND_Municipalities_1997_spf, RI Division of Statewide Planning, "as is"; acknowledge RIGIS),
downloaded once to data/raw/official/rigis/ by hand-run curl (playbook/12-sources.md). Every polygon is land (LAND = 'Y'), and every
island is kept: Block Island (New Shoreham), Aquidneck (Newport, Middletown, Portsmouth), Conanicut (Jamestown), Prudence, Patience and
Hope (Portsmouth), Dutch Island and the rest. Overture's division areas and a coarse simplification drop the small ones, which put
island restaurants "outside the state" (the QA of 2026-10-29 found Monhegan, Maine and Treasure Island, California that way).
"""
import os, json, collections
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "data", "raw", "official", "rigis", "BND_Municipalities_1997_spf.geojson")
OUT = os.path.join(ROOT, "data", "ri")
os.makedirs(OUT, exist_ok=True)


def town_name(n):
    return " ".join(w.capitalize() for w in n.split())


feats = json.load(open(SRC))["features"]
by, county = collections.defaultdict(list), {}
for f in feats:
    p = f["properties"]
    if p.get("LAND") != "Y":
        continue
    t = town_name(p["NAME"])
    by[t].append(shape(f["geometry"]).buffer(0))
    county[t] = town_name(p["COUNTY"])
towns = {t: unary_union(g) for t, g in sorted(by.items())}
state = unary_union(list(towns.values()))
assert len(towns) == 39, len(towns)


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 4), round(y, 4)] for x, y in p.exterior.coords] for p in polys]


# keep islands down to about 2 ha (Rose Island, Dutch Island, Hope Island all stay); the map draws the state at ~40 m detail
out = {"state": [[r] for r in rings(state, 0.0004, 0.000002)],
       "counties": [{"name": t, "c": rings(g, 0.0006, 0.000002)} for t, g in towns.items()]}
json.dump(out, open(f"{OUT}/ri_shapes.json", "w"), separators=(",", ":"))
json.dump(mapping(state.simplify(0.0001, preserve_topology=True)), open(f"{OUT}/ri_state_detail.geojson", "w"))
json.dump({t: mapping(g.simplify(0.0001, preserve_topology=True)) for t, g in towns.items()}, open(f"{OUT}/ri_counties_detail.geojson", "w"))
json.dump(county, open(f"{OUT}/ri_town_county.json", "w"), indent=1)
isl = {t: len(getattr(g, "geoms", [g])) for t, g in towns.items() if t in ("New Shoreham", "Jamestown", "Portsmouth", "Newport", "Middletown")}
print("towns", len(towns), "| state rings", len(out["state"]), "| island towns' polygons", isl,
      "| shapes", round(os.path.getsize(f"{OUT}/ri_shapes.json") / 1024), "KB")
