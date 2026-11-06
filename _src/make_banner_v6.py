# make_banner_v6.py: LinkedIn header, 1584x396. The 20 platforms appear as a live
# "system board" on the right; the title sits in the safe zone (x 430-1000).
# The avatar covers roughly x 80-290 in the lower half, so that area holds no text.
# Platform names and the count come from PRODUCTS in index.html.
#   python _src/make_banner_v6.py   -> _src/linkedin-banner-v6.png (gitignored)
import html, pathlib, re, subprocess
from PIL import Image

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 1584, 396

idx = (ROOT / "index.html").read_text(encoding="utf-8")
body = re.search(r"const PRODUCTS=\[([\s\S]*?)\n\];", idx).group(1)
prods = re.findall(r'\{n:"([^"]+)",u:"([^"]*)"', body)
N = len(prods)
SHORT = {"Coen Construction Platform": "Coen ERP", "North Point Construction": "North Point",
         "Valhalla K9 Services": "Valhalla K9", "Show It With Words": "Show It With Words",
         "Northern Hardy Honey": "Hardy Honey", "TMA Family App": "TMA Family"}
WORDS = {1: "one", 2: "two"}

tiles = ""
for i, (n, u) in enumerate(prods):
    live = bool(u)
    test = n == "TMA Family App"      # Cole's rule: TMA runs on test data, never "live"
    cls = " p" if not live else (" x" if test else "")
    lab = "private" if not live else ("test data" if test else "live")
    tiles += f'<div class="t{cls}"><i></i><b>{html.escape(SHORT.get(n, n))}</b><span>{lab}</span></div>'

page = f"""<!doctype html><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#040907;font-family:Consolas,'Cascadia Mono',monospace;color:#e8fff6;position:relative}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(#0c1a15 1px,transparent 1px),linear-gradient(90deg,#0c1a15 1px,transparent 1px);background-size:33px 33px}}
.glow{{position:absolute;left:330px;top:-260px;width:900px;height:900px;background:radial-gradient(circle,#0f3d2c 0,transparent 62%)}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 1px,transparent 1px 3px)}}
.l{{position:absolute;left:430px;top:58px;width:560px}}
.p1{{font-size:19px;color:#4fae7c}}.p1 em{{color:#8fffc4;font-style:normal}}
h1{{font:800 54px 'Segoe UI',Arial,sans-serif;letter-spacing:.01em;line-height:1.02;margin-top:12px;color:#c9ffe6;text-shadow:0 0 18px rgba(60,240,180,.45)}}
.bar{{width:70px;height:4px;background:#33ff66;margin:16px 0 14px}}
.n{{font-size:22px;color:#8fffc4}}.n b{{color:#33ff66;font-size:30px;margin-right:8px}}
.s{{font-size:17px;color:#3f7a5c;margin-top:8px}}
.u{{font-size:21px;margin-top:16px;color:#ffd75e;font-weight:700}}.u a{{color:#33ff66;text-decoration:underline;text-underline-offset:4px}}
.cur{{display:inline-block;width:11px;height:22px;background:#33ff66;vertical-align:-4px;margin-left:8px}}
.board{{position:absolute;left:1010px;top:34px;width:546px}}
.hd{{display:flex;justify-content:space-between;font-size:13px;color:#4fae7c;letter-spacing:.08em;margin-bottom:9px}}
.hd span:last-child{{color:#33ff66}}
.g{{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}}
.t{{height:56px;border:1.5px solid #1f4a39;background:rgba(8,20,16,.92);border-radius:7px;padding:7px 9px;position:relative}}
.t b{{display:block;font:700 13.5px 'Segoe UI',Arial,sans-serif;color:#d8fff0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:12px;letter-spacing:-.01em}}
.t span{{font-size:11.5px;color:#3cf0b4;letter-spacing:.06em;position:absolute;bottom:7px;left:9px}}
.t i{{position:absolute;top:9px;right:8px;width:7px;height:7px;border-radius:50%;background:#33ff66;box-shadow:0 0 7px #33ff66}}

.t.x span{{color:#ffd75e}}.t.x i{{background:#ffd75e;box-shadow:0 0 7px #ffd75e}}
.t.p{{border-style:dashed;border-color:#2a4a40}}.t.p span{{color:#8a9d95}}.t.p i{{background:#ffd75e;box-shadow:0 0 7px #ffd75e}}
.win{{position:absolute;left:70px;top:46px;width:200px;height:120px;border:1.5px solid #2d6b4a;background:rgba(5,14,10,.8)}}
.win:before{{content:"";display:block;height:14px;background:#1d4a34}}
.win i{{display:block;height:3px;background:#2d6b4a;margin:12px 14px 0;width:70%}}
.w2{{left:110px;top:84px}}.w3{{left:150px;top:122px;opacity:.85}}
</style>
<div class="grid"></div><div class="glow"></div>
<div class="win"><i></i><i style="width:50%"></i><i style="width:60%"></i></div>
<div class="win w2"><i></i><i style="width:40%"></i></div>
<div class="win w3"><i></i><i style="width:55%"></i><i style="width:35%"></i></div>
<div class="l"><div class="p1">cole@ciprari.ai:~$ <em>whoami</em></div>
<h1>BUSINESS SYSTEMS<br>ARCHITECT</h1><div class="bar"></div>
<div class="n"><b>{N}</b>production platforms shipped solo</div>
<div class="s">ERP · multi-tenant SaaS · AI automation · $8.5M portfolio</div>
<div class="u">my résumé is an operating system → <a>ciprari.ai</a><span class="cur"></span></div></div>
<div class="board"><div class="hd"><span>SYSTEM BOARD · WORCESTER, MA</span><span>{sum(1 for _, u in prods if u)} PUBLIC · {sum(1 for _, u in prods if not u)} PRIVATE</span></div>
<div class="g">{tiles}</div></div>
<div class="scan"></div>"""

f = SRC / "banner_v6.html"; f.write_text(page, encoding="utf-8")
big = SRC / "linkedin-banner-v6@2x.png"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H}", f"--screenshot={big}", f.as_uri()], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
out = SRC / "linkedin-banner-v6.png"
Image.open(big).convert("RGB").resize((W, H), Image.LANCZOS).save(out, optimize=True)
big.unlink(); f.unlink()
print("wrote", out, "with", N, "platforms")
