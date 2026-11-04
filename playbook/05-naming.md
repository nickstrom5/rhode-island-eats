# Rhode Island brand: provisional (2026-11-03), waiting for Nick's calls

Built while Nick was away, so every choice below is a placeholder in the pattern he picked for the other states. Changing any of
them is cheap: the display name and copy, `scripts/make-brand.swift` (icon, favicons, share image), `Design/Theme.swift`, the
site palette in `scripts/make-site.py`, then the screenshots again.

## Name (Nick decides)
- **Used for now: "Rhode Island Eats: Restaurants"**, Home Screen **"RI Eats"**, subtitle **"Clam Shacks, Wieners & More"** (27/30).
  Nick chose "<State> Eats" for Georgia, Delaware, Maine, Idaho, Pennsylvania and the rest, and the site is rhodeisland.eatsranked.com.
- **Caveat from the prompt:** rhodeislandeats.com is a live restaurant site, so the prompt suggested avoiding the name. Maine Eats
  went ahead despite maineeats.com belonging to someone else.
- **Alternatives from the prompt** (no App Store app used them and each .com was unregistered per RDAP on 2026-09-27; not rechecked):
  "Ocean State Eats" (the nickname; many firms use "Ocean State": check marks), "Little Rhody Eats", "Quahog Eats" (also Family
  Guy's town). Avoid: "Eat Drink RI" (a festival and news site), the tourism lines, Narragansett Beer's "Hi Neighbor!".
- Bundle id `com.rhodeislandeats.ios` and repo name `rhode-island-eats` are neutral; they don't need to change with the name.

## Icon (Nick picks one of three; `scripts/icon-concepts.swift`, PNGs in `playbook/brand/`)
- **A** a stuffie in its half shell (purple quahog rim, browned stuffing) with a lemon wedge. Passes `check.swift`; at 60 px it
  reads a little like a pie in a dish.
- **B (used for now)** a glass of coffee milk, the state drink, with a straw. Passes `check.swift`; the clearest at 60 px.
- **C** a hot wiener "all the way". Fails the shape rule (short side 0.296 < 0.34) and reads like Chicago's hot dog at 60 px; it would
  need redrawing.

## Palette (provisional): the flag
Hope blue #1D3F73 (10.4:1 on white) for titles and accents; bay teal #1C6670 as the card fill under white text (6.6:1); anchor gold
#F2C14E only as a fill under dark text (gold text on white is 1.7:1); sea-salt #F7F5EF page. No team colors. The header band is a
row of Narragansett Bay swells over a strip of gold sand. The prompt's alternative: a Narragansett Bay set (#0E3A53, sea glass
#8FC1B5, sand #EFE3C8).
