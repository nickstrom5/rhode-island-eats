#!/usr/bin/env python3
"""Build the captioned App Store screenshots from simulator captures (the family's frame, from chi-eats/ios/scripts/appstore-screenshots.py,
by way of mi-eats).

Usage (from ri-eats/): .venv/bin/python scripts/appstore-screenshots.py
Reads playbook/app-store/raw/iphone/*.png (1320x2868, iPhone 17 Pro Max) and playbook/app-store/raw/ipad/*.png (2064x2752, iPad Pro 13"),
made with: OUT=$PWD/playbook/app-store/raw/<iphone|ipad> SLEEP=14 bash scripts/capture-screenshots.sh <udid> <screens>
(the map needs about 20 s on a busy Mac). Writes playbook/app-store/iphone/NN-name.png and .../ipad/NN-name.png at the same sizes.
Each frame: sea-salt behind, a Hope-blue caption band with white condensed type and a short anchor-gold rule (the app header's sand
under the bay swells), and the real capture below in a rounded frame.
Rules (STATE_EATS_PLAYBOOK.md "Screenshots"): real captures, home screen first, no negative board in any image, map zoomed in to
individual pins; captions make no price claim ("free"), use no third-party marks (say "award winners", not MICHELIN or James Beard)
and no "best".
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LAKE, SAND, BG, WHITE, INK = (29, 63, 115), (242, 193, 78), (247, 245, 239), (255, 255, 255), (20, 33, 58)   # Hope blue band, gold rule, sea salt
FONT = "/System/Library/Fonts/Avenir Next Condensed.ttc"   # Heavy face; the app itself uses the system compressed face

IPHONE = [("01-home", "home.png", "Rhode Island's food, list by list"),
          ("02-wieners", "wieners.png", "Hot wieners, nearest first"),
          ("03-detail", "detail.png", "Each place, with notes checked by hand"),
          ("04-clams", "clams.png", "Clam shacks and stuffies by the shore"),
          ("05-fedhill", "fedhill.png", "Federal Hill, table by table"),
          ("06-map", "map.png", "Hand-checked places on the map"),
          ("07-sweets", "sweets.png", "Frozen lemonade and creameries"),
          ("08-saved", "saved.png", "Keep your short list")]
IPAD = [("01-home", "home.png", "Rhode Island's food, list by list"),
        ("02-wieners", "wieners.png", "Hot wieners, nearest first"),
        ("03-clams", "clams.png", "Clam shacks and stuffies by the shore"),
        ("04-map", "map.png", "Hand-checked places on the map"),
        ("05-fedhill", "fedhill.png", "Federal Hill, table by table"),
        ("06-honors", "honors.png", "Award winners and classics")]
BANNED = ("free", "best", "#1", "top ", "james beard", "michelin")   # price claims, rankings and others' marks stay out of captions
for _, _, cap in IPHONE + IPAD:
    assert not any(b in cap.lower() for b in BANNED), cap


def font(size):
    for index in (8, 0):                # Heavy, else Bold (upright faces of Avenir Next Condensed)
        try:
            return ImageFont.truetype(FONT, size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_lines(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def frame(src, out, caption, W, H, band, fsize, radius):
    shot = Image.open(src).convert("RGB")
    assert shot.size == (W, H), f"{src}: {shot.size}, expected {(W, H)}"
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, band], fill=LAKE)
    f = font(fsize)
    lines = fit_lines(d, caption.upper(), f, W * 0.86)
    lh = int(fsize * 1.05)
    y = (band - lh * len(lines)) // 2 - int(fsize * 0.08)
    for line in lines:
        w = d.textlength(line, font=f)
        d.text(((W - w) / 2, y), line, font=f, fill=WHITE)
        y += lh
    d.rectangle([(W - 160) // 2, band - 34, (W + 160) // 2, band - 24], fill=SAND)
    top = band + int(H * 0.035)
    scale = min((H - top - int(H * 0.03)) / shot.height, (W * 0.9) / shot.width)
    sw, sh = int(shot.width * scale), int(shot.height * scale)
    x = (W - sw) // 2
    pad = int(W * 0.012)
    d.rounded_rectangle([x - pad, top - pad, x + sw + pad, top + sh + pad], radius=radius + pad, fill=INK)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=radius, fill=255)
    canvas.paste(shot, (x, top), mask)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, optimize=True)
    print("wrote", out.relative_to(ROOT))


for d_ in ("iphone", "ipad"):   # a renamed or dropped shot must not linger in the upload folder
    for old in (ROOT / "playbook/app-store" / d_).glob("*.png"):
        old.unlink()
for name, cap, caption in IPHONE:
    frame(ROOT / "playbook/app-store/raw/iphone" / cap, ROOT / "playbook/app-store/iphone" / f"{name}.png", caption, 1320, 2868, 520, 118, 96)
for name, cap, caption in IPAD:
    frame(ROOT / "playbook/app-store/raw/ipad" / cap, ROOT / "playbook/app-store/ipad" / f"{name}.png", caption, 2064, 2752, 420, 120, 60)
