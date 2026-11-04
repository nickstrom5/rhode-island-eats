"""Writes data/research/app/*.json (hand-checked Rhode Island guides) and data/research/jbf.json from the compact lists below.
Ported from ga-eats/pipeline/build_research.py.

Each entry cites the 2025-26 page that names it (robots-checked host: check_sources.py). Every page below is dated on its face. The
address comes from the map listing we already hold for that name in that town (site/rhodeisland.json), never from memory; a name that
isn't found exactly once in its town (or at the street number given) is left out and listed in data/research/app/LEADS.md. A place
the map data lacks is added only when the dated page prints its street address (ADDR). Towns are the 39 municipalities (Wakefield is
South Kingstown, Galilee is Narragansett).
Usage: ../.venv/bin/python build_research.py   (then rhodeisland.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "rhodeisland.json")))
C, M = d["cols"], d["meta"]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", "").replace("’", ""))).strip()

# each dated on its face (read 2026-11-03)
RIM_WIENERS = "https://www.rimonthly.com/hot-dogs-and-wieners-in-rhode-island/"          # 2026-07-15
RIM_BEST26 = "https://www.rimonthly.com/2026-best-of-rhode-island-editors-picks/"        # 2026-08-24
RIM_BEST25 = "https://www.rimonthly.com/2025-best-of-rhode-island-editors-picks/"        # 2025-08-19
RIM_SUMMER26 = "https://www.rimonthly.com/summer-bucket-list-2026/"                      # 2026 (summer list; Federal Hill al fresco, clam cake crawl, ice cream)
OSM_GUIDE = "https://www.oceanstatemedia.org/food-drink/the-rhode-island-food-guide-no-tourist-should-miss"   # 2026-06-12
OSM_RIM = "https://www.oceanstatemedia.org/food-drink/2026-08-04/rhode-island-monthly-serves-up-its-latest-local-favorites"   # 2026-08-04
SC_SHACKS = "https://www.southcountyri.com/blog/post/south-county-clam-shacks-are-pure-rhode-island/"   # 2025-08-06
NE_2026 = "https://newengland.com/travel/rhode-island/2026-rhode-island-travel-guide/"  # 2026-04-23
TT_OLDEST = "https://www.tastingtable.com/1975409/oldest-restaurant-every-state-still-open/"   # 2025-09-23
TT_DINERS = "https://www.tastingtable.com/1942900/old-school-diners-worth-visiting/"     # 2025-08-23

# (name as the source writes it or as our listing spells it, town, street number to pick the location (or None), note, founded,
# founded_note, [sources])
GUIDES = {
 "hot wieners": [   # never "hot dogs": New York System wieners with meat sauce, mustard, onions and celery salt
  ("Olneyville New York System", "Providence", "18", "The Plainfield Street original, a James Beard America's Classic (2014).", 1946, "Opened in 1946, per the James Beard America's Classics list.", [RIM_WIENERS, OSM_GUIDE]),
  ("Olneyville New York System", "Cranston", "1012", "Olneyville New York System's Reservoir Avenue branch.", None, None, [RIM_WIENERS, OSM_GUIDE]),
  ("Wein-O-Rama", "Cranston", "1009", "Hot wieners on Oaklawn Avenue, a local go-to for more than sixty years.", None, None, [RIM_WIENERS]),
  ("Rod's Grille", "Warren", "6", "Warren's hot wiener counter, serving its wiener sauce since 1955.", None, None, [RIM_WIENERS]),
  ("Sam's New York System", "Warwick", "6", "Family-run hot wieners on Freeborne Street.", None, None, [RIM_WIENERS]),
  ("Wally's Providence", "Providence", "120", "Wally's Wieners on Atwells Avenue, Federal Hill.", None, None, [RIM_BEST26, RIM_SUMMER26]),
 ],
 "clam shack": [   # clam cakes, clear chowder, stuffies and fried seafood
  ("Aunt Carrie's", "Narragansett", "1240", "Clam cakes and chowder near Point Judith since 1920; a James Beard America's Classic (2007).", 1920, "Opened in 1920 by Carrie and Ulysses Cooper near Point Judith Lighthouse (South County Tourism, Aug 2025).", [SC_SHACKS, OSM_GUIDE, RIM_SUMMER26]),
  ("Iggy's Doughboys and Chowder House", "Narragansett", "1151", "Doughboys, clam cakes and chowder in Galilee.", None, None, [SC_SHACKS, OSM_GUIDE]),
  ("Iggy's Doughboys & Chowder House", "Warwick", "889", "Doughboys, clam cakes and chowder at Oakland Beach.", None, None, [OSM_GUIDE, RIM_SUMMER26]),
  ("Flo's Clam Shack", "Middletown", "4", "Clam cakes and doughboys across from First Beach.", None, None, [OSM_GUIDE]),
  ("Evelyn's Drive-In", "Tiverton", "2335", "Rhode Island clam chowder and fried fish on Nanaquaket Pond.", None, None, [OSM_GUIDE, RIM_BEST26, RIM_SUMMER26]),
  ("Champlin's Seafood", "Narragansett", "256", "A Galilee seafood deck over the harbor.", None, None, [SC_SHACKS]),
  ("Monahan's Clam Shack by the Cove", "Charlestown", "5402", "A South County clam shack.", None, None, [SC_SHACKS, RIM_SUMMER26]),
  ("Cap'n Jack's Restaurant", "South Kingstown", "706", "A South County clam shack on Succotash Road.", None, None, [SC_SHACKS]),
  ("Buster Krab's Grill & Beach Bar", "Narragansett", "265", "A Galilee clam shack.", None, None, [SC_SHACKS]),
  ("Roy Boys Clam Shack", "North Kingstown", "6710", "A South County clam shack on Post Road.", None, None, [SC_SHACKS]),
  ("Salty's", "Narragansett", "254", "A Galilee clam shack.", None, None, [SC_SHACKS]),
  ("Anthony's Seafood", "Middletown", "963", "Stuffies (stuffed quahogs) on Aquidneck Avenue.", None, None, [RIM_BEST26]),
  ("Dune Brothers Seafood", "Providence", "239", "A seafood shack turned restaurant and fish market on the river.", None, None, [NE_2026, RIM_SUMMER26]),
 ],
 "federal hill": [   # Italian dining rooms on Atwells Avenue
  ("Andino's Italian Restaurant", "Providence", "171", "Italian on Atwells Avenue, Federal Hill.", None, None, [RIM_SUMMER26]),
  ("Angelo's Restaurant", "Providence", "141", "Angelo's Civita Farnese: family-style Italian on Atwells Avenue.", None, None, [RIM_SUMMER26]),
  ("Cassarino's Restaurant", "Providence", "177", "Italian classics and seafood on Atwells Avenue.", None, None, [RIM_SUMMER26]),
  ("Costantino's Venda Bar & Ristorante", "Providence", "275", "Italian on DePasquale Plaza, off Atwells Avenue.", None, None, [RIM_SUMMER26]),
  ("Roma", "Providence", "310", "Italian on Atwells Avenue, Federal Hill.", None, None, [RIM_SUMMER26]),
  ("Massimo Ristorante", "Providence", "134", "Regional Italian on Atwells Avenue.", None, None, [RIM_SUMMER26]),
  ("Trattoria Appia", "Providence", "245", "Italian on Atwells Avenue, Federal Hill.", None, None, [RIM_SUMMER26]),
 ],
 "pizza strips": [   # bakery pizza: sheet pizza in strips with sweet tomato sauce, served at room temperature
  ("D. Palmieri's Bakery", "Johnston", "624", "Bakery pizza strips in Johnston.", None, None, [OSM_GUIDE]),
  ("DePetrillo's Pizza & Bakery Smithfield", "Smithfield", "105", "DePetrillo's: bakery pizza strips.", None, None, [OSM_GUIDE]),
  ("Tony's Colonial", "Providence", "311", "Pizza strips at the Atwells Avenue Italian market.", None, None, [RIM_BEST26]),
 ],
 "portuguese": [
  ("Cafe Alma", "East Providence", "227", "A Portuguese-inspired café on Warren Avenue: pastéis de nata by day, bitoque at night.", None, None, [RIM_BEST26, OSM_RIM]),
  ("Folklore Provisions", "Bristol", "301", "Portuguese-style breakfast on Hope Street.", None, None, [RIM_BEST25]),
  ("Matos Bakery", "Pawtucket", "569", "A Portuguese bakery on Broadway.", None, None, [OSM_RIM]),
 ],
 "sweets": [   # frozen lemonade, creameries and the Awful Awful
  ("Apponaug Village Creamery", "Warwick", "10", "Ice cream in Apponaug Village.", None, None, [RIM_BEST25]),
  ("Brickley's Ice Cream", "South Kingstown", "322", "Homemade ice cream in Wakefield.", None, None, [RIM_SUMMER26]),
  ("Brickley's Homemade Ice Cream", "Narragansett", "921", "Homemade ice cream on Boston Neck Road.", None, None, [RIM_SUMMER26]),
  ("Gray's Ice Cream", "Tiverton", "16", "Ice cream at Tiverton Four Corners.", None, None, [RIM_SUMMER26]),
  ("Gray's Ice Cream", "Bristol", "259", "Gray's Ice Cream on Thames Street.", None, None, [RIM_SUMMER26]),
  ("The Keep", "Cumberland", "2368", "Ice cream on Mendon Road.", None, None, [RIM_SUMMER26]),
  ("Pompelmo Gelato", "Westerly", "31", "Gelato on High Street.", None, None, [RIM_SUMMER26]),
  ("Wright's Creamery", "Providence", "498", "Wright's ice cream on Kinsley Avenue.", None, None, [RIM_SUMMER26]),
 ],
 "oldest": [
  ("White Horse Tavern", "Newport", "26", "A tavern since 1673 on Marlborough Street.", 1673, "A tavern here since 1673, named in 1730 (Tasting Table, Sep 2025).", [TT_OLDEST]),
  ("Modern Diner", "Pawtucket", "364", "A 1940 Sterling Streamliner diner car on East Avenue.", None, None, [TT_DINERS]),
 ],
}
# brand-wide: every location of these in our data (each source names the brand, statewide)
BRANDS_ALL = {"sweets": [("Del's Lemonade", r"^dels(?: lemonade)?(?: and refreshments)?(?: tiverton little compton)?$", "Frozen lemonade, Rhode Island's summer drink.", [OSM_GUIDE, RIM_SUMMER26]),
                         ("Newport Creamery", r"^newport creamery$", "The Awful Awful, Newport Creamery's ice milk shake.", [OSM_GUIDE])]}
# street addresses as the dated page prints them, for places the map data lacks
ADDR = {("Tony's Colonial", "Providence"): "311 Atwells Ave"}
# cuisine checked by hand where the listing's guess is wrong
CUISINE = {("Tony's Colonial", "Providence"): "Pizza", ("Matos Bakery", "Pawtucket"): "Bakery & Sweets", ("Cafe Alma", "East Providence"): "European",
           ("Folklore Provisions", "Bristol"): "Breakfast & Diner",
           ("Aunt Carrie's", "Narragansett"): "Seafood"}   # a 1920 clam shack, which the map data files as a bakery
KINDS = {"hot wieners": ["hot wieners"], "clam shack": ["clam shack"], "federal hill": ["federal hill"], "pizza strips": ["pizza strips"],
         "portuguese": ["portuguese"], "sweets": ["frozen lemonade"], "oldest": ["oldest"]}

# James Beard honors (data/research/jbf.json): facts, each with a dated source
JBF = [
 {"name": "Aunt Carrie's", "city": "Narragansett", "address": "1240 Ocean Rd", "honors": ["America's Classic 2007"],
  "sources": ["https://en.wikipedia.org/wiki/List_of_James_Beard_America%27s_Classics", SC_SHACKS], "match_names": ["AUNT CARRIES RESTAURANT"]},
 {"name": "Olneyville New York System", "city": "Providence", "address": "18 Plainfield St", "honors": ["America's Classic 2014"],
  "sources": ["https://en.wikipedia.org/wiki/List_of_James_Beard_America%27s_Classics", RIM_WIENERS]},
 {"name": "Gift Horse", "city": "Providence", "address": "272 Westminster St", "honors": ["Best Chef: Northeast winner 2025 (Sky Haneul Kim)"],
  "sources": ["https://www.rimonthly.com/?p=286834", "https://www.oceanstatemedia.org/sky-kim-wins-best-chef-northeast-for-her-locally-inspired-korean-cuisine", OSM_RIM]},
 {"name": "Loma", "city": "Providence", "address": "112 Spruce St", "honors": ["Best New Bar winner 2026"],
  "sources": ["https://www.jamesbeard.org/stories/james-beard-award-winners-2026"]},
 {"name": "Nicks On Broadway", "city": "Providence", "address": "500 Broadway", "honors": ["Best Chef: Northeast finalist 2026 (Derek Wagner)"],
  "sources": ["https://www.oceanstatemedia.org/food-drink/rhode-island-lands-two-finalists-in-2026-james-beard-awards", OSM_RIM]},
 {"name": "Al Forno Restaurant", "city": "Providence", "address": "577 S Water St", "honors": ["Best Chef: Northeast winner 1993 (George Germon and Johanne Killeen)"],
  "sources": ["https://www.jamesbeard.org/stories/in-memoriam-george-germon", RIM_BEST26], "match_names": ["AL FORNO"]},
]
# closed, each with a source (Sly Fox Den Too, Charlestown, the 2023 Best Chef: Northeast's restaurant, closed in January 2025 per the prompt's
# research; no 2025-26 page we may read confirms it yet, so it waits in LEADS.md)
CLOSED = [{"name": "Old Canteen", "address": "120 Atwells Ave", "city": "Providence", "match_names": ["JOE MARZILLIS OLD CANTEEN"], "open": False,
           "note": "Closed; Wally's Providence opened in the former Old Canteen (Rhode Island Monthly, 2025-05-23).",
           "sources": ["https://www.rimonthly.com/wallys-providence/"]}]


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0] == num]
    return hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = {"JR Crickets": "J.R. Crickets"}.get(brand_of(norm_name(name)), name)
        elif re.match(r"(?i)^j\.? ?r\.? crickets", name):
            out[-1]["display"] = "J.R. Crickets"
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

for kind, rows in BRANDS_ALL.items():
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    out = json.load(open(f"{R}/app/{fn}.json"))
    for brand, rx, note, srcs in rows:
        for i, n in enumerate(C["name"]):
            if re.match(rx, key(n)) and C["city"][i] is not None and C["addr"][i]:
                out.append({"name": C["name"][i], "address": C["addr"][i], "city": M["cities"][C["city"][i]],
                            "zip": str(C["zip"][i]) if C["zip"][i] else None, "kinds": KINDS[kind], "dishes": [], "note": note, "founded": None,
                            "founded_note": None, "website": None, "open": True, "evidence_date": "2026-10", "sources": srcs, "match_names": [],
                            "display": brand})
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)
json.dump([dict(j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)

open(f"{R}/app/LEADS.md", "w").write("# Rhode Island research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a 2025-26 source we may use
- Diners (a guide was planned): Haven Brothers (Providence, 1893 per RI Monthly Dec 2023), Seaplane, West Side, Miss Lorraine, Jigger's
  (East Greenwich), Patriots, Blue Plate: the diner pages found are 2023 (RI Monthly) or undated (visitrhodeisland.com's Diner Trail).
  Only Modern Diner has a 2025-26 page (Tasting Table, Aug 2025), so it sits in "oldest" until there are four.
- Cape Verdean: 10 Rocks Tapas (Pawtucket) and Vicente's Kitchen have only undated listings; no 2025-26 page found.
- Portuguese: O Dinis, Madeira and Campino's (East Providence, Warren Ave) have only 2023 picks or undated GoProvidence listings.
- Pizza strips: LaSalle Bakery, Original Italian Bakery, Colvitto's, Sal's, Vienna (RI Monthly, Feb 2022); DePetrillo's other branches
  (North Providence, Warwick, Coventry, Glocester; Ocean State Media June 2026 names the towns but our map data lacks them).
- Clam shacks: Quito's (Bristol) and Benny's (Narragansett) named in 2025-26 lists but missing from our map data with no printed address;
  George's of Galilee has only undated pages.
- Oldest: Haven Brothers (1893), Camille's (1914), Angelo's (1924), Twin Oaks (1933), Wright's Farm (1954), Olympia Tea Room (1916) have
  only 2024-or-older pages. The Old Canteen (Federal Hill, 1956) closed in 2025 (closed.json); Wally's Providence holds 120 Atwells Ave.
- Closed, waiting for a readable source: Sly Fox Den Too (Charlestown; Sherry Pocknett, Best Chef: Northeast 2023), closed January 2025.
- Coffee milk: Autocrat and Eclipse are syrup brands, not places; Delekta Pharmacy's coffee cabinets have only a 2024 page.
- Blocked or unusable hosts: providencejournal.com, bostonglobe.com, boston.com, turnto10.com, wpri.com, saveur.com, theinfatuation.com
  (robots), rhodybeat.com and eastbayri.com (bot checks), golocalprov.com (403 to Claude's fetcher though robots allow).
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
