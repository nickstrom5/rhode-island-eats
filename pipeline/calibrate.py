"""How often is a map listing a real food or drink business? Measured against Rhode Island's official lists -> data/ri/calibration*.json

Adapted from ga-eats/pipeline/calibrate.py (co-eats -> tx-eats -> az-eats -> tn-eats -> ga-eats). Rhode Island's current food
service list is behind a bot check, so the one license list to measure against is RIDOH's own: the L2K export of February 2018
(food service licenses with seats that were active then; official.load_l2k()). It covers every kind of sit-down kitchen in every
town, but it is eight years old, so it favors listings of places that have been around; shares are for comparing kinds of listings
with each other, not rates of real restaurants. Statewide, the share Google's Sep 2021 snapshot showed open is the second check
(Idaho's and Hawaii's method). A match is the same business name nearby, or the same street address with a distinctive name word in
common, inside one town (the RIGIS municipality: listings.py and geocode_official.py).
"""
import json
import numpy as np, pandas as pd
from shapely.geometry import shape, Point
from shapely import STRtree
from common import RI
from listings_util import official_match
import official

o = pd.read_pickle(f"{RI}/stage1.pkl")
F = pd.read_pickle(f"{RI}/official.pkl")
_CN = json.load(open(f"{RI}/ri_counties_detail.geojson"))
_NAMES = list(_CN)
_GEOMS = [shape(_CN[n]).buffer(0.0003) for n in _NAMES]
_TREE = STRtree(_GEOMS)


def county_of(la, lo):
    if la != la:
        return None
    p = Point(lo, la)
    for i in _TREE.query(p):
        if _GEOMS[i].contains(p):
            return _NAMES[i]
    return None


o["county"] = [county_of(la, lo) for la, lo in zip(o.lat, o.lon)]
F["county"] = [county_of(la, lo) for la, lo in zip(F.lat, F.lon)]
o.to_pickle(f"{RI}/stage1.pkl")
F.to_pickle(f"{RI}/official.pkl")
L2K = official.load_l2k()
L2K["county"] = [county_of(la, lo) for la, lo in zip(L2K.lat, L2K.lon)]
base = ~o.j_junk & ~o.j_outside
print("listings with a county:", int(o.county.notna().sum()), "of", len(o), "| licenses placed:", int(F.lat.notna().sum()), "of", len(F))


def groups(L, app=False):
    s = L.src.fillna("none")
    if app:
        conf = L.confidence.fillna(0)
        has_web = L.n_web.fillna(0).astype(int) > 0
        return np.select([L.ov_closed | L.j_closedname, (s == "meta") & (conf >= 0.95), (s == "meta") & (conf >= 0.9) & has_web,
                          (s == "meta") & (conf >= 0.9), s.isin(["AllThePlaces", "DAC"]), (s == "BrightQuery") & (conf >= 0.95), s == "meta"],
                         ["closed per Overture/name", "meta_high", "meta_mid_web", "meta_mid_noweb", "brand_feed", "bq_high", "meta_low"],
                         "other_sources")
    return np.select([L.closed21, L.ov_closed, (s == "meta") & L.in21, s == "meta", s.isin(["AllThePlaces", "DAC"]) & L.in21,
                      s.isin(["AllThePlaces", "DAC"]), L.in21, s == "Foursquare", s == "BrightQuery", s == "Microsoft"],
                     ["Google 2021 says closed", "Overture says closed", "Meta + open in Google 2021", "Meta only",
                      "brand feed + Google 2021", "brand feed only", "Foursquare/BrightQuery/Microsoft + Google 2021",
                      "Foursquare only", "BrightQuery only", "Microsoft only"], "other")


def measure(label, L, R, store_web, store_app, by_county=True):
    L = L.reset_index(drop=True)
    R = R.reset_index(drop=True)
    m = {}
    if by_county:   # "100 Main St" is in dozens of towns: match inside one county
        for cty, idx in L.groupby("county").groups.items():
            Rc = R[R.county == cty]
            if not len(Rc):
                continue
            Lc = L.loc[idx].reset_index()
            for i, j in official_match(Lc, Rc.reset_index(drop=True)).items():
                m[int(Lc.at[i, "index"])] = int(Rc.index[j])
    else:
        m = official_match(L, R)
    L["hit"] = L.index.map(lambda i: i in m)
    for mode, store in ((False, store_web), (True, store_app)):
        L["grp"] = groups(L, mode)
        t = L.groupby("grp").agg(n=("id", "size"), official=("hit", "mean"), open21=("in21", "mean")).sort_values("n", ascending=False)
        print(f"\n== {label} ({'app grouping' if mode else 'web grouping'}): {len(L)} listings, {len(R)} official records")
        print(t.assign(official=(t.official * 100).round(1), open21=(t.open21 * 100).round(1)).to_string())
        store[label] = {"listings": int(len(L)), "official_records": int(len(R)),
                        "groups": {g: {"n": int(r.n), "official": round(float(r.official), 3)} for g, r in t.iterrows()}}
    keepish = ~(L.ov_closed | L.j_closedname | L.closed21)
    got = set(R.biz.iloc[[m[i] for i in L.index[keepish] if i in m]])
    Rr = R[R.kind.eq("food")].drop_duplicates("biz")
    cover = float(np.mean([b in got for b in Rr.biz])) if len(Rr) else None
    print(f"{label}: official food businesses found among open map listings: {cover * 100:.1f}% of {len(Rr)}")
    store_web[label]["coverage"] = round(cover, 3)
    store_web[label]["official_food"] = int(len(Rr))


res, app = {}, {}
seated = L2K[L2K.kind.eq("food") & L2K.active & L2K.lat.notna() & L2K.county.notna()]
measure("Rhode Island (RIDOH food service licenses with seats, active in 2018)", o[base & o.county.notna()], seated, res, app)

# the share Google 2021 still showed open, statewide, per app group (a listing Google had in 2021 and didn't call closed)
L = o[base].copy()
L["grp"] = groups(L, True)
L["open21"] = L.in21 & ~L.closed21
g21 = L.groupby("grp").open21.agg(["size", "mean"])
print("\n== open in Google 2021 (statewide, app grouping)\n" + (g21.assign(mean=(g21["mean"] * 100).round(1))).to_string())
# the app ships no Google-derived number, so calibration_app.json leaves the 2021 share out (calibration.json, read only by the
# private leaderboard, keeps it), as in sc-eats

per = o[base & o.county.notna() & ~o.ov_closed & ~o.j_closedname].groupby("county").size()
print("\n== open, cleaned listings per county (top 15)\n" + per.sort_values(ascending=False).head(15).to_string())
json.dump({"areas": res, "per_county_listings": {c: int(n) for c, n in per.items()},
           "open_google_2021": {g: {"n": int(r["size"]), "share": round(float(r["mean"]), 3)} for g, r in g21.iterrows()}},
          open(f"{RI}/calibration.json", "w"), indent=1)
json.dump(app, open(f"{RI}/calibration_app.json", "w"), indent=1)
