#!/usr/bin/env python3
"""
LinkedIn banner for Cole Ciprari — 1584x396.

Design notes:
  * Rendered at 3x and downsampled, so every edge is properly antialiased
    instead of the chunky nearest-neighbour look of the old one.
  * Matches ciprari.ai: phosphor-green CRT, scanlines, bloom. Someone who sees
    this banner and then opens the site should recognise it instantly.
  * LinkedIn's avatar circle covers roughly x 80-290 in the lower half, and
    mobile crops the sides — so all load-bearing text lives between x 430-1500
    and y 90-300. The left third is deliberately atmospheric.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

S = 3                                  # supersample factor
W, H = 1584 * S, 396 * S

BG      = (5, 11, 8)
GREEN   = (51, 255, 102)
DIM     = (79, 174, 124)
MUT     = (45, 107, 74)
AMBER   = (255, 215, 94)
INK     = (143, 255, 196)

MONO  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f  = lambda p, s: ImageFont.truetype(p, int(s * S))


# ---------------------------------------------------------------- background
img = Image.new("RGB", (W, H), BG)

# radial phosphor bloom, centred behind the headline
yy, xx = np.mgrid[0:H, 0:W]
cx, cy = int(W * 0.60), int(H * 0.42)
d = np.sqrt(((xx - cx) / (W * 0.52)) ** 2 + ((yy - cy) / (H * 0.95)) ** 2)
glow = np.clip(1.0 - d, 0, 1) ** 2.2
base = np.array(img, dtype=np.float32)
for i, c in enumerate((18, 74, 44)):
    base[:, :, i] += glow * c
img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

d0 = ImageDraw.Draw(img)

# faint blueprint grid — an architect's paper, barely there
for gx in range(0, W, 46 * S):
    d0.line([(gx, 0), (gx, H)], fill=(10, 26, 18), width=1)
for gy in range(0, H, 46 * S):
    d0.line([(0, gy), (W, gy)], fill=(10, 26, 18), width=1)


# ---------------------------------------------------------------- right: architecture graph
# A dim node-and-edge diagram: the "architect" motif, used as texture not content.
NODES = [(1195, 96), (1330, 70), (1455, 118), (1250, 196), (1392, 205),
         (1180, 292), (1320, 306), (1462, 262)]
EDGES = [(0, 1), (1, 2), (0, 3), (1, 3), (2, 4), (3, 4), (3, 5), (4, 6),
         (5, 6), (6, 7), (4, 7)]
for a, b in EDGES:
    d0.line([(NODES[a][0] * S, NODES[a][1] * S), (NODES[b][0] * S, NODES[b][1] * S)],
            fill=(20, 62, 42), width=int(1.6 * S))
for i, (nx, ny) in enumerate(NODES):
    r = int((9 if i % 3 else 12) * S)
    col = MUT if i % 3 else DIM
    d0.ellipse([nx * S - r, ny * S - r, nx * S + r, ny * S + r],
               outline=col, width=int(1.8 * S))
    if i % 3 == 0:
        d0.ellipse([nx * S - r // 3, ny * S - r // 3, nx * S + r // 3, ny * S + r // 3], fill=col)


# ---------------------------------------------------------------- left: window glyphs
# Three dim stacked windows — the desktop metaphor, hinted rather than drawn.
# Sits in the upper-left; LinkedIn's avatar swallows everything below y~200.
for i, (wx, wy, ww, wh_) in enumerate([(112, 46, 118, 78), (152, 84, 118, 78), (192, 122, 118, 78)]):
    edge = [DIM, (34, 92, 62), (26, 70, 48)][i]
    d0.rectangle([wx * S, wy * S, (wx + ww) * S, (wy + wh_) * S], outline=edge, width=int(1.5 * S))
    d0.rectangle([wx * S, wy * S, (wx + ww) * S, (wy + 15) * S], fill=edge)
    for ln in range(3):
        ly = (wy + 30 + ln * 13)
        d0.line([((wx + 11) * S, ly * S), ((wx + ww - 16 - ln * 18) * S, ly * S)],
                fill=edge, width=int(1.4 * S))


# ---------------------------------------------------------------- centre: the message
x0 = 430
d0.text((x0 * S, 92 * S), "cole@ciprari.ai:~$ ", font=f(MONO, 17), fill=MUT)
w_prompt = d0.textlength("cole@ciprari.ai:~$ ", font=f(MONO, 17))
d0.text((x0 * S + w_prompt, 92 * S), "whoami", font=f(MONO, 17), fill=DIM)

# headline
d0.text((x0 * S, 126 * S), "BUSINESS SYSTEMS", font=f(SANSB, 45), fill=INK)
d0.text((x0 * S, 178 * S), "ARCHITECT", font=f(SANSB, 45), fill=INK)

# accent rule
d0.rectangle([x0 * S, 235 * S, (x0 + 74) * S, 238 * S], fill=GREEN)

# the numbers that matter
d0.text((x0 * S, 253 * S), "12", font=f(MONOB, 27), fill=GREEN)
w12 = d0.textlength("12", font=f(MONOB, 27))
d0.text((x0 * S + w12 + 10 * S, 259 * S), "production platforms shipped solo",
        font=f(MONO, 18), fill=DIM)

d0.text((x0 * S, 291 * S), "ERP  ·  multi-tenant SaaS  ·  AI automation  ·  $8.5M portfolio",
        font=f(MONO, 15), fill=MUT)

# the hook + the call to action, on one line
hook = "my résumé is an operating system  →  "
d0.text((x0 * S, 322 * S), hook, font=f(MONOB, 18), fill=AMBER)
wh = d0.textlength(hook, font=f(MONOB, 18))
d0.text((x0 * S + wh, 322 * S), "ciprari.ai", font=f(MONOB, 18), fill=GREEN)
wu = d0.textlength("ciprari.ai", font=f(MONOB, 18))
# underline the domain so it reads as a destination, then a live cursor
d0.line([(x0 * S + wh, 344 * S), (x0 * S + wh + wu, 344 * S)], fill=GREEN, width=int(1.6 * S))
d0.rectangle([x0 * S + wh + wu + 7 * S, 322 * S, x0 * S + wh + wu + 17 * S, 344 * S], fill=GREEN)


# ---------------------------------------------------------------- top-right chip
tag = "WORCESTER, MA"
tw = d0.textlength(tag, font=f(MONO, 13))
d0.rectangle([1584 * S - tw - 46 * S, 30 * S, 1584 * S - 30 * S, 56 * S],
             outline=MUT, width=int(1.2 * S))
d0.text((1584 * S - tw - 38 * S, 36 * S), tag, font=f(MONO, 13), fill=DIM)


# ---------------------------------------------------------------- bloom pass
# Duplicate the bright pixels, blur them, add back: makes phosphor look lit
# rather than printed.
arr = np.array(img).astype(np.float32)
lum = arr.max(axis=2)
mask = np.clip((lum - 120) / 135, 0, 1)[:, :, None]
bright = Image.fromarray((arr * mask).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(radius=7 * S))
img = Image.fromarray(np.clip(arr + np.array(bright).astype(np.float32) * 0.55,
                              0, 255).astype(np.uint8))


# ---------------------------------------------------------------- scanlines + vignette
arr = np.array(img).astype(np.float32)
arr[1::3, :, :] *= 0.90                       # every third row, gently
vy = np.linspace(-1, 1, H)[:, None]
vx = np.linspace(-1, 1, W)[None, :]
vig = np.clip(1.06 - 0.30 * (vx ** 2 + vy ** 2), 0, 1.06)[:, :, None]
arr *= vig
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- down-sample
out = img.resize((1584, 396), Image.LANCZOS)
out.save("linkedin-banner-v5.png")
print("wrote linkedin-banner-v5.png", out.size)
