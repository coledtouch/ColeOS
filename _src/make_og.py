#!/usr/bin/env python3
"""Regenerate og-image-v2.png (the 1200x630 social card) with the current platform count.

The card was hand-designed — Arial Bold on a teal gradient, no generator — so this
patches the one number in place on _src/og-base.png rather than rebuilding the card:
it erases the stats-number cell and redraws it in the same font, size and colour.

    python3 _src/make_og.py          # count derived from PRODUCTS in index.html
    python3 _src/make_og.py 13       # or explicit

Needs Pillow and Arial Bold (Windows font, also reachable from WSL). The text is a
new URL for social scrapers only when the filename changes — if LinkedIn keeps a
stale thumbnail after a change, bump the filename and its 14 references.
"""
import os, re, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
if len(sys.argv) > 1:
    N = sys.argv[1]
else:
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    body = re.search(r"const PRODUCTS=\[([\s\S]*?)\n\];", idx).group(1)
    N = str(len(re.findall(r'^\s*\{n:"', body, re.M)))

FONTS = ["/mnt/c/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arialbd.ttf",
         "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
FONT = next((f for f in FONTS if os.path.exists(f)), None)
if not FONT:
    raise SystemExit("need Arial Bold (or Liberation Sans Bold) — none found")

DIGIT = (103, 232, 249); BG = (11, 88, 94)     # measured off the original card
INK_LEFT, INK_TOP, SIZE = 84, 354, 41          # original "10": ink starts (84,354); Arial Bold 41 matches its width exactly

im = Image.open(os.path.join(HERE, "og-base.png")).convert("RGB")
ImageDraw.Draw(im).rectangle([79, 347, 200, 390], fill=BG)   # clear the number cell (bg is flat here)
layer = Image.new("RGBA", (300, 120), (0, 0, 0, 0))
ImageDraw.Draw(layer).text((10, 10), N, font=ImageFont.truetype(FONT, SIZE), fill=DIGIT + (255,))
glyph = layer.crop(layer.getbbox())
im.paste(glyph, (INK_LEFT, INK_TOP), glyph)
out = os.path.join(ROOT, "og-image-v2.png")
im.save(out)
print("wrote", out, "with count", N)
