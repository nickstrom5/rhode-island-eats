"""Known chain brands in Rhode Island: regex on normalized name -> brand label.

Adapted from wi-eats/pipeline/brands.py; Wisconsin-only brands dropped, Colorado and Mountain West chains added (co-eats),
Texas chains added for tx-eats, Arizona chains in az-eats, Tennessee and Southeast chains in tn-eats,
Georgia-born and Georgia-heavy chains in ga-eats; Rhode Island and New England chains in ri-eats.
"""
import re

BRANDS = [
    ("Dunkin'", r"^DUNKIN"), ("Subway", r"^SUBWAY"), ("McDonald's", r"^MC ?DONALDS"), ("Starbucks", r"^STARBUCK"),
    ("Jimmy John's", r"^JIMMY JOHN"), ("Burger King", r"^BURGER KING"), ("Taco Bell", r"^TACO BELL"),
    ("Potbelly", r"^POTBELLY"), ("Wingstop", r"^WING ?STOP"), ("Chipotle", r"^CHIPOTLE"), ("Popeyes", r"^POPEYE"),
    ("Wendy's", r"^WENDYS"), ("Panda Express", r"^PANDA EXPRESS"), ("White Castle", r"^WHITE CASTLE"),
    ("Chick-fil-A", r"^CHICK FIL"), ("Domino's", r"^DOMINO"), ("Jersey Mike's", r"^JERSEY MIKE"),
    ("Panera Bread", r"^PANERA"), ("Jet's Pizza", r"^JETS PIZZA"), ("Little Caesars", r"^LITTLE CAESAR"),
    ("Papa John's", r"^PAPA JOHN"), ("KFC", r"^KFC|^KENTUCKY FRIED"), ("Tropical Smoothie Cafe", r"^TROPICAL SMOOTHIE"),
    ("Buffalo Wild Wings", r"^BUFFALO WILD"), ("Five Guys", r"^FIVE GUYS"), ("Raising Cane's", r"^RAISING CANE"),
    ("Portillo's", r"^PORTILLO"), ("Auntie Anne's", r"^AUNTIE ANNE"), ("Qdoba", r"^QDOBA"),
    ("Noodles & Company", r"^NOODLES (?:AND )?CO(?:MPANY)?\b"), ("Smoothie King", r"^SMOOTHIE KING"), ("Firehouse Subs", r"^FIREHOUSE SUB"),
    ("IHOP", r"^IHOP"), ("Denny's", r"^DENNYS"), ("Sonic", r"^SONIC DRIVE|^SONIC$"), ("Insomnia Cookies", r"^INSOMNIA COOKIE"),
    ("Crumbl", r"^CRUMBL"), ("Dairy Queen", r"^DAIRY QUEEN|^DQ GRILL|^DQ$"), ("Baskin-Robbins", r"^BASKIN"), ("Krispy Kreme", r"^KRISPY KREME"),
    ("Chuck E. Cheese", r"^CHUCK E CHEESE"), ("Rosati's", r"^ROSATI"), ("Nothing Bundt Cakes", r"^NOTHING BUNDT"),
    ("Hooters", r"^HOOTERS"), ("Cheesecake Factory", r"^CHEESECAKE FACTORY"), ("P.F. Chang's", r"^P ?F CHANG"), ("Maggiano's", r"^MAGGIANO"),
    ("Ruth's Chris", r"^RUTHS CHRIS"), ("Morton's", r"^MORTONS THE STEAK|^MORTONS STEAK"), ("Steak 'n Shake", r"^STEAK N SHAKE"),
    ("Applebee's", r"^APPLEBEE"), ("Chili's", r"^CHILIS"), ("Olive Garden", r"^OLIVE GARDEN"), ("Red Lobster", r"^RED LOBSTER"),
    ("Jamba", r"^JAMBA"), ("Cinnabon", r"^CINNABON"), ("Pizza Hut", r"^PIZZA HUT"), ("Arby's", r"^ARBYS"),
    ("Checkers", r"^CHECKERS DRIVE|^CHECKERS AND RALLY|^CHECKERS$"), ("MOD Pizza", r"^MOD PIZZA"), ("Tim Hortons", r"^TIM HORTON"),
    ("Peet's Coffee", r"^PEETS"), ("Colectivo", r"^COLECTIVO"), ("Cava", r"^CAVA$|^CAVA (?:MEDITERRANEAN|GRILL)"), ("Blaze Pizza", r"^BLAZE PIZZA"),
    # national chains common in Colorado, and Colorado's own
    ("Culver's", r"^CULVER"), ("Taco John's", r"^TACO JOHN"), ("Caribou Coffee", r"^CARIBOU COFFEE|^CARIBOU$"),
    ("Scooter's Coffee", r"^SCOOTERS COFFEE"), ("Dutch Bros", r"^DUTCH BRO"), ("7 Brew", r"^7 BREW"), ("The Human Bean", r"^(?:THE )?HUMAN BEAN"),
    ("Black Rock Coffee", r"^BLACK ROCK COFFEE"), ("Ziggi's Coffee", r"^ZIGGIS"), ("Dazbog Coffee", r"^DAZBOG"),
    ("Texas Roadhouse", r"^TEXAS ROADHOUSE"), ("Famous Dave's", r"^FAMOUS DAVE"), ("Red Robin", r"^RED ROBIN"),
    ("Freddy's", r"^FREDDYS FROZEN|^FREDDYS STEAKBURGER"), ("Papa Murphy's", r"^PAPA MURPH"), ("Marco's Pizza", r"^MARCOS PIZZA"),
    ("Cracker Barrel", r"^CRACKER BARREL"), ("Outback Steakhouse", r"^OUTBACK STEAK"), ("LongHorn Steakhouse", r"^LONGHORN STEAK"),
    ("Cold Stone Creamery", r"^COLD STONE"), ("Golden Corral", r"^GOLDEN CORRAL"),
    ("Old Chicago", r"^OLD CHICAGO$|^OLD CHICAGO (?:PASTA|PIZZA|TAPROOM)"), ("Rock Bottom", r"^ROCK BOTTOM"),
    ("Einstein Bros. Bagels", r"^EINSTEIN BRO"), ("Quiznos", r"^QUIZNO"), ("Fazoli's", r"^FAZOLI"), ("Dickey's Barbecue Pit", r"^DICKEYS"),
    ("HuHot Mongolian Grill", r"^HUHOT"), ("Blimpie", r"^BLIMPIE"), ("Dave's Hot Chicken", r"^DAVES HOT CHICKEN"), ("Sbarro", r"^SBARRO"),
    ("Great Harvest", r"^GREAT HARVEST"), ("Teriyaki Madness", r"^TERIYAKI MADNESS"), ("First Watch", r"^FIRST WATCH"),
    ("TGI Fridays", r"^TGI FRIDAY"), ("Mooyah", r"^MOOYAH"), ("Charleys Cheesesteaks", r"^CHARLEYS"), ("Smashburger", r"^SMASHBURGER"),
    ("Hunt Brothers Pizza", r"^HUNT BROTHERS"), ("Hot Stuff Pizza", r"^HOT STUFF"), ("Krispy Krunchy Chicken", r"^KRISPY KRUNCHY"),
    ("Cheba Hut", r"^CHEBA HUT"), ("MrBeast Burger", r"^MR ?BEAST"), ("It's Just Wings", r"^ITS JUST WINGS"), ("7-Eleven", r"^7 ELEVEN"),
    ("Casey's", r"^CASEYS"), ("Pizza Ranch", r"^PIZZA RANCH"), ("Hardee's", r"^HARDEES"), ("Carl's Jr.", r"^CARLS JR"),
    ("Jack in the Box", r"^JACK IN THE BOX"), ("Del Taco", r"^DEL TACO"), ("Whataburger", r"^WHATABURGER"), ("In-N-Out Burger", r"^IN N OUT"),
    ("Café Rio", r"^CAFE RIO"), ("Costa Vida", r"^COSTA VIDA"), ("Cafe Yumm!", r"^CAFE YUMM"), ("Waffle House", r"^WAFFLE HOUSE"),
    ("Perkins", r"^PERKINS (?:RESTAURANT|BAKERY|AMERICAN|FAMILY)|^PERKINS$"), ("Bob Evans", r"^BOB EVANS"), ("Black Bear Diner", r"^BLACK BEAR DINER"),
    ("Native Grill & Wings", r"^NATIVE GRILL"), ("BJ's Restaurant", r"^BJS RESTAURANT|^BJS BREWHOUSE"), ("Twin Peaks", r"^TWIN PEAKS"),
    ("Kneaders", r"^KNEADERS"), ("Swig", r"^SWIG$"), ("Crave Cookies", r"^CRAVE COOKIE"), ("Paris Baguette", r"^PARIS BAGUETTE"),
    ("Sweetgreen", r"^SWEETGREEN"), ("Torchy's Tacos", r"^TORCHYS"), ("Velvet Taco", r"^VELVET TACO"), ("Fuzzy's Taco Shop", r"^FUZZYS TACO"),
    ("Slim Chickens", r"^SLIM CHICKENS"), ("Zaxby's", r"^ZAXBY"), ("Bojangles", r"^BOJANGLES"), ("Church's Chicken", r"^CHURCHS (?:TEXAS )?CHICKEN"),
    ("Hooters", r"^HOOTERS"), ("Dairy Queen", r"^DAIRY QUEEN|^DQ GRILL|^DQ$"),
    # Colorado-born or Colorado-heavy chains
    ("Illegal Pete's", r"^ILLEGAL PETE"), ("Snarf's", r"^SNARFS"), ("Good Times", r"^GOOD TIMES (?:BURGERS|DRIVE)|^GOOD TIMES$"),
    ("Village Inn", r"^VILLAGE INN"), ("Garbanzo", r"^GARBANZO"), ("Modern Market", r"^MODERN MARKET"), ("Tokyo Joe's", r"^TOKYO JOE"),
    ("Smiling Moose", r"^SMILING MOOSE"), ("Snooze", r"^SNOOZE"), ("Lucile's", r"^LUCILES"), ("Bad Daddy's Burger Bar", r"^BAD DADDYS"),
    ("Mad Greens", r"^MAD GREENS"), ("Larkburger", r"^LARKBURGER"), ("Spicy Pickle", r"^SPICY PICKLE"), ("Sweet Cow", r"^SWEET COW"),
    ("Beau Jo's", r"^BEAU JO"), ("Anthony's Pizza & Pasta", r"^ANTHONYS PIZZA"), ("Blackjack Pizza", r"^BLACKJACK PIZZA"),
    ("Abo's Pizza", r"^ABOS PIZZA|^ABOS$"), ("Woody's Wings", r"^WOODYS WINGS"), ("Fat Shack", r"^FAT SHACK"), ("Wing Shack", r"^WING SHACK"),
    ("Santiago's", r"^SANTIAGOS"), ("Las Delicias", r"^LAS DELICIAS"), ("Tacos y Salsas", r"^TACOS Y SALSAS"), ("Birdcall", r"^BIRDCALL"),
    ("Brothers BBQ", r"^BROTHERS BBQ|^BROTHERS BAR B Q"), ("Moe's Original BBQ", r"^MOES ORIGINAL"), ("Famous Philly's", r"^FAMOUS PHILLYS"),
    ("Biker Jim's", r"^BIKER JIMS"), ("Kaladi Coffee", r"^KALADI"), ("Pablo's Coffee", r"^PABLOS COFFEE"), ("Novo Coffee", r"^NOVO COFFEE"),
    ("Huckleberry Roasters", r"^HUCKLEBERRY ROASTERS"), ("Corvus Coffee", r"^CORVUS"), ("Little Man Ice Cream", r"^LITTLE MAN ICE CREAM"),
    ("Rocky Mountain Chocolate Factory", r"^ROCKY MOUNTAIN CHOCOLATE"), ("Sam's No. 3", r"^SAMS NO 3"), ("Racca's", r"^RACCAS"),
    ("Odell Brewing", r"^ODELL BREWING"), ("New Belgium", r"^NEW BELGIUM"), ("Breckenridge Brewery", r"^BRECKENRIDGE BREWERY"),
    ("Tequila's", r"^TEQUILAS (?:FAMILY )?MEXICAN"), ("El Tapatio", r"^EL TAPATIO"), ("Señor Sol", r"^SENOR SOL"),
    ("Juan's Flying Burrito", r"^JUANS FLYING"), ("Rosie's Diner", r"^ROSIES DINER"), ("Bonchon", r"^BONCHON"), ("Chuy's", r"^CHUYS"),
    ("Kum & Go", r"^KUM (?:AND )?GO"), ("Maverik", r"^MAVERIK"), ("Loaf 'N Jug", r"^LOAF N JUG"), ("Love's", r"^LOVES TRAVEL"),
    # Arizona-born or Arizona-heavy chains (names only; no logos)
    ("Filiberto's", r"^FILIBERTOS"), ("Rolberto's", r"^ROLBERTOS"), ("Aliberto's", r"^ALIBERTOS"), ("Eegee's", r"^EEGEES"),
    ("Macayo's", r"^MACAYO"), ("Barro's Pizza", r"^BARROS PIZZA"), ("Peter Piper Pizza", r"^PETER PIPER"), ("Oregano's", r"^OREGANOS"),
    ("Native Grill & Wings", r"^NATIVE (?:GRILL|NEW AMERICAN|WINGS)"), ("Streets of New York", r"^STREETS OF NEW YORK"),
    ("Someburros", r"^SOMEBURROS"), ("Rubio's", r"^RUBIOS"), ("Cold Stone Creamery", r"^COLD STONE"), ("Dutch Bros", r"^DUTCH BRO"),
    ("Black Rock Coffee", r"^BLACK ROCK COFFEE"), ("Raising Cane's", r"^RAISING CANES"), ("Paradise Bakery", r"^PARADISE BAKERY"),
    ("Kneaders", r"^KNEADERS"), ("Taco Guild", r"^TACO GUILD"), ("Abuelo's", r"^ABUELOS"), ("Garcia's", r"^GARCIAS (?:MEXICAN|OF SCOTTSDALE)"),
    ("Manuel's", r"^MANUELS MEXICAN"), ("Serrano's", r"^SERRANOS MEXICAN"), ("Nello's", r"^NELLOS"), ("Grimaldi's", r"^GRIMALDI"),
    ("Cornish Pasty Co.", r"^CORNISH PASTY"), ("Rosati's", r"^ROSATIS"), ("Original ChopShop", r"^ORIGINAL CHOP ?SHOP"),
    ("The Original Breakfast House", r"^ORIGINAL BREAKFAST HOUSE"), ("Snooze", r"^SNOOZE"), ("Hash Kitchen", r"^HASH KITCHEN"),
    ("Over Easy", r"^OVER EASY"), ("Matt's Big Breakfast", r"^MATTS BIG BREAKFAST"), ("Lo-Lo's Chicken & Waffles", r"^LO ?LOS CHICKEN"),
    ("Thai Basil", r"^THAI BASIL"), ("Pita Jungle", r"^PITA JUNGLE"), ("Kona Grill", r"^KONA GRILL"), ("Mastro's", r"^MASTROS"),
    ("Dillon's", r"^DILLONS (?:BBQ|RESTAURANT|KC)"), ("Famous Sam's", r"^FAMOUS SAMS"), ("Zipps Sports Grill", r"^ZIPPS"),
    ("Tops Liquors", r"^TOPS LIQUOR"), ("Circle K", r"^CIRCLE K\b"), ("QuikTrip", r"^QUIK ?TRIP|^QT$"), ("Fry's", r"^FRYS (?:FOOD|MARKETPLACE)|^FRYS$"),
    ("Bashas'", r"^BASHAS"), ("Food City", r"^FOOD CITY"), ("Safeway", r"^SAFEWAY"), ("Love's", r"^LOVES (?:TRAVEL|COUNTRY)"),
    ("Pilot", r"^PILOT (?:TRAVEL|FLYING)"), ("Rock Springs Café", r"^ROCK SPRINGS CAFE"), ("Lenny's Burger Shop", r"^LENNYS BURGER"),
    ("Ike's Love & Sandwiches", r"^IKES"), ("Cheba Hut", r"^CHEBA HUT"), ("Teakwoods", r"^TEAKWOODS"), ("Spinato's", r"^SPINATOS"),
    # Tennessee-born or Tennessee-heavy chains, and Southeast chains common here (names only; no logos)
    ("Hattie B's Hot Chicken", r"^HATTIE BS"), ("Gus's World Famous Fried Chicken", r"^GUSS (?:WORLD FAMOUS|FAMOUS|FRIED)|^GUSS$"),
    ("Krystal", r"^KRYSTAL$|^KRYSTAL (?:RESTAURANT|BURGERS?|COMPANY)"), ("Pal's Sudden Service", r"^PALS SUDDEN|^PALS$"),
    ("Back Yard Burgers", r"^BACK ?YARD BURGERS"), ("Martin's Bar-B-Que Joint", r"^MARTINS BAR B QUE|^MARTINS BBQ"),
    ("Central BBQ", r"^CENTRAL BBQ|^CENTRAL BAR B Q"), ("Corky's BBQ", r"^CORKYS (?:BBQ|BAR)"), ("Jim 'N Nick's", r"^JIM N NICKS"),
    ("Jack's Bar-B-Que", r"^JACKS BAR B QUE|^JACKS BBQ"), ("Edley's Bar-B-Que", r"^EDLEYS"), ("Puckett's", r"^PUCKETTS"),
    ("Party Fowl", r"^PARTY FOWL"), ("Slim & Husky's", r"^SLIM (?:AND )?HUSKYS"), ("Frothy Monkey", r"^FROTHY MONKEY"),
    ("Captain D's", r"^CAPTAIN DS"), ("Shoney's", r"^SHONEYS"), ("O'Charley's", r"^OCHARLEYS|^O CHARLEYS"), ("Logan's Roadhouse", r"^LOGANS ROADHOUSE"),
    ("J. Alexander's", r"^J ALEXANDERS"), ("Ruby Tuesday", r"^RUBY TUESDAY"), ("Calhoun's", r"^CALHOUNS"), ("Aubrey's", r"^AUBREYS"),
    ("Puleo's Grille", r"^PULEOS"), ("Sticky Fingers", r"^STICKY FINGERS"), ("Tupelo Honey", r"^TUPELO HONEY"), ("Huddle House", r"^HUDDLE HOUSE"),
    ("Maple Street Biscuit Company", r"^MAPLE STREET BISCUIT"), ("Biscuitville", r"^BISCUITVILLE"), ("Moe's Southwest Grill", r"^MOES SOUTHWEST"),
    ("Newk's Eatery", r"^NEWKS"), ("McAlister's Deli", r"^MCALISTERS|^MC ALISTERS"), ("Mellow Mushroom", r"^MELLOW MUSHROOM"),
    ("Firehouse Subs", r"^FIREHOUSE SUB"), ("Hardee's", r"^HARDEES"), ("Waffle House", r"^WAFFLE HOUSE"), ("Gigi's Cupcakes", r"^GIGIS CUPCAKES"),
    ("Pancake Pantry", r"^PANCAKE PANTRY"), ("Calhoun's", r"^CALHOUNS"), ("Rafferty's", r"^RAFFERTYS"), ("Cheddar's", r"^CHEDDARS"),
    ("Taziki's", r"^TAZIKIS"), ("Chuy's", r"^CHUYS"), ("Bar Louie", r"^BAR LOUIE"), ("Twin Peaks", r"^TWIN PEAKS"),
    ("Steak 'n Shake", r"^STEAK N SHAKE"), ("Zoës Kitchen", r"^ZOES KITCHEN"), ("Shipley Do-Nuts", r"^SHIPLEY"), ("Ollie's", r"^OLLIES$"),
    ("Kroger", r"^KROGER"), ("Publix", r"^PUBLIX"), ("Food City", r"^FOOD CITY"), ("Ingles", r"^INGLES"), ("Piggly Wiggly", r"^PIGGLY WIGGLY"),
    ("Food Lion", r"^FOOD LION"), ("Weigel's", r"^WEIGELS"), ("MAPCO", r"^MAPCO"), ("Twice Daily", r"^TWICE DAILY"),
    ("Pilot", r"^PILOT (?:TRAVEL|FLYING)"), ("Dollar General", r"^DOLLAR GENERAL"), ("Save A Lot", r"^SAVE A LOT"), ("Marathon", r"^MARATHON$"),
    # Georgia-born or Georgia-heavy chains (names only; no logos). The Varsity matches only its own names, not any "Varsity" bar.
    ("The Varsity", r"^VARSITY$|^VARSITY JR$|^VARSITY (?:DOWNTOWN|ATHENS|DAWSONVILLE|NORCROSS|KENNESAW)$"),
    ("Taco Mac", r"^TACO MAC"), ("J. Christopher's", r"^J CHRISTOPHERS"), ("The Flying Biscuit Cafe", r"^FLYING BISCUIT"),
    ("Ted's Montana Grill", r"^TEDS MONTANA"), ("Willy's Mexicana Grill", r"^WILLYS MEXICANA"), ("Fresh To Order", r"^FRESH TO ORDER|^F2O$"),
    ("Tin Drum Asian Kitchen", r"^TIN DRUM"), ("Marlow's Tavern", r"^MARLOWS TAVERN"), ("Shane's Rib Shack", r"^SHANES RIB"),
    ("Sonny's BBQ", r"^SONNYS (?:BBQ|BAR B Q|REAL PIT)"), ("Fox Bros. Bar-B-Q", r"^FOX BROS"), ("Chicken Salad Chick", r"^CHICKEN SALAD CHICK"),
    ("Cook Out", r"^COOK ?OUT$|^COOK ?OUT (?:RESTAURANT|DRIVE)"), ("Golden Krust", r"^GOLDEN KRUST"), ("Henri's Bakery", r"^HENRIS BAKERY"),
    ("Rreal Tacos", r"^RREAL TACOS"), ("Gusto!", r"^GUSTO$|^GUSTO (?:KITCHEN|HEALTHY)"), ("Twisted Taco", r"^TWISTED TACO"),
    ("Uncle Maddio's", r"^UNCLE MADDIOS"), ("Dreamland Bar-B-Que", r"^DREAMLAND (?:BBQ|BAR B Q)"), ("Six Feet Under", r"^SIX FEET UNDER"),
    ("Atlanta Bread", r"^ATLANTA BREAD"), ("American Deli", r"^AMERICAN DELI$|^AMERICAN DELI (?:WINGS|AND)"), ("Bruster's Real Ice Cream", r"^BRUSTERS"),
    ("Jeni's Splendid Ice Creams", r"^JENIS SPLENDID|^JENIS ICE"), ("Hungry Howie's", r"^HUNGRY HOWIE"), ("Pollo Campero", r"^POLLO CAMPERO"),
    ("Pollo Tropical", r"^POLLO TROPICAL"), ("Huey Magoo's", r"^HUEY MAGOO"), ("PDQ", r"^PDQ$|^PDQ (?:CHICKEN|RESTAURANT)"),
    ("Chanticleer", r"^CHANTICLEER$"), ("Slutty Vegan", r"^SLUTTY VEGAN"), ("Dave & Buster's", r"^DAVE (?:AND )?BUSTERS"),
    ("Wings & Things", r"^WINGS (?:AND|N) THINGS"), ("Tropical Smoothie Cafe", r"^TROPICAL SMOOTHIE"), ("Planet Smoothie", r"^PLANET SMOOTHIE"),
    ("Twin Smokers", r"^TWIN SMOKERS"), ("Highland Bakery", r"^HIGHLAND BAKERY"), ("Big Boss Burger", r"^BIG BOSS BURGER"),
    ("Chuck's Fish", r"^CHUCKS FISH"), ("Hibachi Grill Supreme Buffet", r"^HIBACHI GRILL (?:AND )?SUPREME BUFFET"),
    ("Harveys Supermarket", r"^HARVEYS SUPERMARKET"), ("Food Depot", r"^FOOD DEPOT"), ("RaceTrac", r"^RACETRAC|^RACE TRAC"),
    ("QuikTrip", r"^QUIK ?TRIP|^QT$"), ("Sprouts", r"^SPROUTS"), ("Spinx", r"^SPINX"), ("Parker's Kitchen", r"^PARKERS KITCHEN|^PARKERS$"),
    ("Buc-ee's", r"^BUC EES"), ("Chevron", r"^CHEVRON$"), ("Shell", r"^SHELL$"), ("Exxon", r"^EXXON$"), ("Sam's Club", r"^SAMS CLUB"),
    # Rhode Island and New England chains (names only; no logos)
    ("Del's Lemonade", r"^DELS (?:FROZEN )?LEMONADE|^DELS$"), ("Newport Creamery", r"^NEWPORT CREAMERY"), ("Bess Eaton", r"^BESS EATON"),
    ("Honey Dew Donuts", r"^HONEY ?DEW DONUTS|^HONEY ?DEW$"), ("D'Angelo", r"^DANGELO"), ("Ninety Nine", r"^NINETY NINE|^99 RESTAURANT"),
    ("Bertucci's", r"^BERTUCCI"), ("Friendly's", r"^FRIENDLYS"), ("Uno Pizzeria & Grill", r"^UNO PIZZERIA|^PIZZERIA UNO|^UNO CHICAGO"),
    ("Kelly's Roast Beef", r"^KELLYS ROAST BEEF"), ("Wahlburgers", r"^WAHLBURGERS"), ("Pizza Pie-er", r"^PIZZA PIE ER"),
    ("Nick-a-Nee's", r"^NICK A NEES"), ("Gregg's", r"^GREGGS (?:RESTAURANT|PUB)"), ("Kristina's", r"^KRISTINAS"),
    ("Cumberland Farms", r"^CUMBERLAND FARMS"), ("Stop & Shop", r"^STOP (?:AND|N) SHOP"), ("Dave's Marketplace", r"^DAVES MARKETPLACE"),
    ("Shaw's", r"^SHAWS$|^SHAWS (?:SUPERMARKET|STAR)"), ("Market Basket", r"^MARKET BASKET"), ("Whole Foods", r"^WHOLE FOODS"),
    ("Xtra Mart", r"^XTRA ?MART"), ("Seven Eleven", r"^7 ?ELEVEN|^SEVEN ELEVEN"), ("Gulf", r"^GULF$"), ("Sunoco", r"^SUNOCO$"),
    ("Panera Bread", r"^ST LOUIS BREAD"),
    # delivery-only brands cooked in another restaurant's kitchen (QA 2026-11-03), so brand_store can match them; norm_name drops "THE"
    ("Burger Den", r"^BURGER DEN$"), ("The Meltdown", r"^MELTDOWN$"), ("Banda Burrito", r"^BANDA BURRITO"), ("Tenderfix", r"^TENDERFIX"),
    ("Pardon My Cheesesteak", r"^PARDON MY CHEESESTEAK"), ("Neighborhood Wings", r"^NEIGHBORHOOD WINGS"), ("It's Just Wings", r"^ITS JUST WINGS"),
]
_C = [(b, re.compile(p)) for b, p in BRANDS]

# distinctive brands also recognized mid-name ("HALE FAMILY MCDONALDS", "SAII BABA DUNKIN")
_ANYWHERE = [(b, re.compile(p)) for b, p in [("McDonald's", r"\bMC ?DONALDS\b"), ("Dunkin'", r"\bDUNKIN\b"), ("Starbucks", r"\bSTARBUCKS\b"),
             ("Wingstop", r"\bWING ?STOP\b"), ("Culver's", r"\bCULVERS\b"), ("Popeyes", r"\bPOPEYES\b"), ("Chipotle", r"\bCHIPOTLE\b"),
             ("Jimmy John's", r"\bJIMMY JOHNS\b"), ("Taco Bell", r"\bTACO BELL\b"), ("Hattie B's Hot Chicken", r"\bHATTIE BS\b"),
             ("Zaxby's", r"\bZAXBYS\b"), ("Chick-fil-A", r"\bCHICK FIL A\b"), ("Waffle House", r"\bWAFFLE HOUSE\b")]]


def brand_of(nkey, *more):
    """Brand from the display name, else from Overture's brand label."""
    keys = [k for k in [nkey] + [m for m in more if isinstance(m, str)] if isinstance(k, str)]
    for k in keys:
        for part in [k or ""] + [p.strip() for p in (k or "").split("/")]:
            for b, p in _C:
                if p.search(part):
                    return b
    for k in keys:
        for b, p in _ANYWHERE:
            if p.search(k or ""):
                return b
    return None
