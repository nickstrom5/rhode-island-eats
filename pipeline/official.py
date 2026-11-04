"""Official records for Rhode Island -> one table of licensed food businesses (playbook/12-sources.md).

Rhode Island has one inspector, RIDOH's Center for Food Protection, and no official grade. Its current lists are out of reach for a
script: health.ri.gov ("Download Food Service Lists") answers every automated request with a Cloudflare challenge, which we never
solve or work around, and the inspection site (ri.healthinspections.us) and license lookup (healthri.mylicense.com) are search-only.
What we can read:
- "rigis": RIGIS "Licensed Food Markets (2025)" (ArcGIS item e3f9a20ca91d4098b2220f186910baaa; RI Division of Statewide Planning from
           RIDOH's license list, "as is"; acknowledge RIGIS). 471 market licenses (MRK numbers): grocery stores, convenience
           stores, specialty and non-profit markets, with address and status but no point. Used to flag grocery counters.
- "l2k":   RIDOH's own "L2K Food Facilities" layer (services1.arcgis.com/dkWT1XL4nglP5MLP, owner RIDOHGIS, public): its licensing
           system's export of February 2018, last edited August 2020. 27,316 licenses (5,201 food service licenses then active).
           Eight years old, so calibration only (calibrate.py): never shown as current, never used to keep or add a place. The layer
           also carries owners' and managers' names, emails and phones: the download asks for none of them.

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype.
kind: food (seated food service) | truck | market | other.
"""
import os, re, json, datetime
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads: 'US HIGHWAY 1' = 'US-1' = 'ROUTE 1' = 'RT 1'; 'RI-138' = 'STATE ROUTE 138' = 'RTE 138'
    (Rhode Island numbers its state routes apart from the US routes, so every numbered route is one 'SH n'); 'I-95'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|RI|SR|SH|RT|CR|I|IH)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|RHODE ISLAND (?:HIGHWAY|HWY|ROUTE|RTE)|RI (?:HIGHWAY|HWY|ROUTE|RTE)|RI|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out





LIST_DATE = None   # set by load(): the date of the market list RIGIS published
MARKETS_FILE = os.path.join(OFF, "rigis", "food_markets_2025.geojson")
MARKETS_ITEM = "https://www.arcgis.com/home/item.html?id=e3f9a20ca91d4098b2220f186910baaa"
MARKETS_DATE = "2025"   # the layer's own title ("Licensed Food Markets (2025)"); RIGIS last edited it 2026-04-29
L2K_FILE = os.path.join(OFF, "ridoh_l2k", "l2k_food_facilities_2018.geojson")
L2K_ITEM = "https://www.arcgis.com/home/item.html?id=35234eeb5ce948c1a91842a5446d2a5b"
INSPECTIONS_URL = "https://ri.healthinspections.us/ri/"
LTYPE = {"Seats -  Less than 50": "Food service, under 50 seats", "Seats - 50 or More": "Food service, 50 seats or more",
         "Mobile Food Service": "Mobile food service", "Caterer or Commissary": "Caterer or commissary",
         "Food Service (Non-Profit)": "Food service (non-profit)"}


def _zip(z):
    z = re.sub(r"\D", "", str(int(z)) if isinstance(z, float) and z == z else str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def liq_kind(t):
    """Rhode Island has no statewide liquor list we can read: towns license, and DBR's lookup is search-only."""
    return None


OTHER = re.compile(r"\b(?:SCHOOL|ELEMENTARY|ACADEMY|HOSPITAL|JAIL|DETENTION|SENIOR|NURSING|FOOD TRUCK|CATERING|CATERER|COMMISSARY|"
                   r"CONCESSION|CHURCH|PARISH|CAMP|CORRECTION(?:AL)?|CAMPUS|WAREHOUSE|COLLEGE|UNIVERSITY|DISTRIBUT\w*|WHOLESALE)\b", re.I)


def _row(jur, lic, name, addr, city, z, la, lo, kind, active=True, ltype=None, holder=None):
    num, st = street_key(addr)
    if kind == "food" and OTHER.search(name or ""):
        kind = "other"
    return {"jur": jur, "lic": lic, "name": name, "dba": name, "holder": holder, "keys": _names(name), "addr": addr, "city": city,
            "zip": _zip(z), "num": num, "street": st, "lat": la, "lon": lo, "kind": kind, "active": active, "ltype": ltype}


def _addr(a):
    """'2790 POST ROAD STE 130' -> '2790 Post Road Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    return re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


def load_markets():
    """RIGIS's 2025 licensed food markets: one row per market license (no point: geocode_official.py places them)."""
    global LIST_DATE
    LIST_DATE = MARKETS_DATE
    rows = []
    for f in json.load(open(MARKETS_FILE))["features"]:
        p = f["properties"]
        if (p.get("USER_State") or "RI").strip() != "RI":
            continue
        x = _row("rigis", f"rigis-{p['USER_Licen']}", re.sub(r"\s+", " ", p.get("USER_Facil") or "").strip(), _addr(p.get("USER_Physi")),
                 _city(p.get("USER_City")), p.get("ZIP"), np.nan, np.nan, "market", active=(p.get("USER_Statu") or "").strip() == "Active",
                 ltype=(p.get("USER_Lic_1") or "").strip() or None)
        x["chain"] = (p.get("USER_Chain") or "").strip() == "Y"
        rows.append(x)
    return pd.DataFrame(rows)


def load_l2k():
    """RIDOH's 2018 L2K export: one row per food service license (calibration only; never shown). Seated licenses are kind "food";
    mobile units "truck"; caterers, non-profits and vending "other"; markets "market". active = the license was active in 2018."""
    rows = []
    for f in json.load(open(L2K_FILE))["features"]:
        p, g = f["properties"], f.get("geometry")
        prof, prim = (p.get("Professi_1") or "").strip(), (p.get("Primary__1") or "").strip()
        if prof not in ("Food Service", "Markets"):
            continue
        kind = "market" if prof == "Markets" else "food" if prim.startswith("Seats") else "truck" if prim.startswith("Mobile") else "other"
        la, lo = (g["coordinates"][1], g["coordinates"][0]) if g and g.get("coordinates") and (p.get("Score") or 0) >= 90 else (np.nan, np.nan)
        x = _row("l2k", f"l2k-{p.get('License_No')}", re.sub(r"\s+", " ", p.get("Full_Name") or "").strip(), _addr(p.get("License_Ad")),
                 _city(p.get("License_Ci")), p.get("License_ZI"), la, lo, kind, active=(p.get("Primary__3") or "").strip() == "Active",
                 ltype=LTYPE.get(prim, prim or None))
        x["issued"] = p.get("License_Is")
        rows.append(x)
    df = pd.DataFrame(rows)
    df["biz"] = np.arange(len(df)) + 10_000_000
    return df


def load():
    df = load_markets()
    # one business can hold several records (a market and a second license at one address under one name): same address, a name in common
    df["biz"] = np.arange(len(df))
    for num, g in df[df.num.notna() & df.street.notna()].groupby("num"):
        idx = list(g.index)
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                a, b = idx[x], idx[y]
                if not street_compat(df.at[a, "street"], df.at[b, "street"]) or df.at[a, "zip"] != df.at[b, "zip"]:
                    continue
                ka, kb = df.at[a, "keys"], df.at[b, "keys"]
                if ka and kb and any(name_sim(p, q) >= 85 or ((_stems(p) - GENERIC) & (_stems(q) - GENERIC)) for p in ka for q in kb):
                    df.loc[df.biz == df.at[b, "biz"], "biz"] = df.at[a, "biz"]
    df["county"] = None   # the town, set from the point (geocode_official.py, calibrate.py)
    return df
