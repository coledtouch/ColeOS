# make_heroes.py: LinkedIn project hero images (1200x960) for the projects that had none.
# Text and a schematic only. No screenshots, logos or third-party marks.
# Rules (Cole, 2026-11-05):
#   Tuner and LumaNest TV: engineering only, nothing about what plays.
#   AI Trader: no results, trading mode, account, broker or server details.
#   TMA: say it is on test data, and use no logo or screenshots.
#   PocketPGP: never call it secure or audited.
# Run: python make_heroes.py   (Windows; uses headless Chrome) -> out/*.png
import html, os, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 1200, 960

def box(x, y, w, h, label, sub="", hot=False):
    stroke = "#3cf0b4" if hot else "#2a4a40"
    fill = "#0c1a16" if hot else "#08110e"
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
    s += f'<text x="{x+w/2}" y="{y+h/2+(-6 if sub else 10)}" class="bl">{html.escape(label)}</text>'
    if sub: s += f'<text x="{x+w/2}" y="{y+h/2+28}" class="bs">{html.escape(sub)}</text>'
    return s

def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#3cf0b4" stroke-width="3" marker-end="url(#a)"/>'

def qr(x, y, n=9, c=14):
    import random; r = random.Random(7); s = ""
    for i in range(n):
        for j in range(n):
            corner = (i < 3 and j < 3) or (i < 3 and j > n-4) or (i > n-4 and j < 3)
            on = (i in (0, 2) or j in (0, 2) or (i == 1 and j == 1)) if (i < 3 and j < 3) else \
                 (i in (0, 2) or j in (n-3, n-1) or (i == 1 and j == n-2)) if (i < 3 and j > n-4) else \
                 (i in (n-3, n-1) or j in (0, 2) or (i == n-2 and j == 1)) if (i > n-4 and j < 3) else r.random() < .45
            if on: s += f'<rect x="{x+j*c}" y="{y+i*c}" width="{c}" height="{c}" fill="#e8fff6"/>'
    return s

D = {}
D["tuner"] = dict(cat="TV media player", name="Tuner", tag="One player, written natively for each TV platform.",
  chips=["Kotlin", "Jetpack Compose", "Media3", "webOS", "Roku SceneGraph", "GitHub Actions"], foot="tunertv.app",
  svg=lambda: (
    '<rect x="70" y="20" width="560" height="330" rx="18" fill="#08110e" stroke="#3cf0b4" stroke-width="3"/>'
    '<rect x="300" y="350" width="100" height="22" fill="#2a4a40"/><rect x="250" y="372" width="200" height="10" rx="5" fill="#2a4a40"/>'
    '<rect x="100" y="50" width="250" height="270" rx="10" fill="#0c1a16" stroke="#2a4a40"/>'
    + "".join(f'<rect x="118" y="{70+i*48}" width="214" height="34" rx="6" fill="{"#174034" if i==1 else "#10221d"}"/>' for i in range(5)) +
    '<rect x="370" y="50" width="230" height="140" rx="10" fill="#0c1a16" stroke="#2a4a40"/><text x="485" y="128" class="bs">preview</text>'
    '<rect x="390" y="205" width="190" height="115" rx="10" fill="#e8fff6"/>' + qr(408, 214, 7, 11) +
    '<text x="535" y="262" class="code" fill="#08110e">K7Q2</text><text x="535" y="292" class="code" fill="#08110e">X9MD</text>'
    '<rect x="730" y="90" width="150" height="270" rx="22" fill="#08110e" stroke="#3cf0b4" stroke-width="3"/>'
    '<rect x="752" y="130" width="106" height="106" rx="6" fill="#0c1a16" stroke="#2a4a40"/><text x="805" y="190" class="bs">scan</text>'
    '<rect x="752" y="260" width="106" height="36" rx="8" fill="#3cf0b4"/><text x="805" y="285" class="bk">Approve</text>'
    + arrow(720, 230, 600, 262) +
    '<text x="350" y="420" class="cap">Remote-driven guide · phone pairing by QR · Multi View</text>'))

D["lumanest"] = dict(cat="Web platform", name="LumaNest TV", tag="Checkout, renewals and TV pairing behind the Tuner app.",
  chips=["Cloudflare Workers", "D1", "R2", "React", "PayPal", "GitHub Actions"], foot="lumanest.tv",
  svg=lambda: (
    box(20, 40, 230, 110, "Phone", "approves pairing") + box(20, 220, 230, 110, "PayPal", "verified webhooks") +
    box(360, 110, 260, 160, "One Worker", "site · checkout · console", hot=True) +
    box(730, 20, 220, 100, "D1", "records") + box(730, 140, 220, 100, "R2", "TV app downloads") + box(730, 260, 220, 100, "TV", "pairs once") +
    arrow(250, 95, 355, 160) + arrow(250, 275, 355, 225) + arrow(620, 160, 725, 75) + arrow(620, 190, 725, 190) + arrow(620, 225, 725, 305) +
    '<text x="485" y="420" class="cap">Codes expire in 10 minutes · only a hash of the device code is stored</text>'))

D["tma"] = dict(cat="Booster-club family app", name="TMA Family App", tag="Balances, trips and payments for a school music booster club's families.",
  chips=["PWA", "React", "Google Apps Script", "Google Sheets", "Web Push", "PayPal"], foot="mytma.org  ·  running on test data",
  svg=lambda: (
    '<rect x="60" y="10" width="200" height="380" rx="26" fill="#08110e" stroke="#3cf0b4" stroke-width="3"/>'
    '<text x="160" y="60" class="bs">Activity fund</text><text x="160" y="104" class="big">$ —</text>'
    + "".join(f'<rect x="82" y="{130+i*56}" width="156" height="42" rx="8" fill="#10221d"/>' for i in range(4)) +
    '<text x="160" y="157" class="bs">Trip · due date</text><text x="160" y="213" class="bs">Pay or use funds</text><text x="160" y="269" class="bs">Concert reminder</text><text x="160" y="325" class="bs">6-digit email code</text>'
    + box(390, 40, 250, 120, "Google Sheet", "the treasurer keeps it", hot=True) + box(390, 230, 250, 120, "Apps Script", "backend") +
    box(760, 40, 220, 120, "Board tools", "approvals · reports") + box(760, 230, 220, 120, "Push Worker", "VAPID · no Firebase") +
    arrow(265, 200, 385, 290) + arrow(515, 225, 515, 165) + arrow(640, 100, 755, 100) + arrow(640, 290, 755, 290) +
    '<text x="520" y="430" class="cap">No separate database · no app store · installs from the browser</text>'))

D["trader"] = dict(cat="Private trading assistant", name="AI Trader", tag="Two models must agree. Code checks the risk. Each order waits for approval.",
  chips=["Python", "FastAPI", "Docker Compose", "Multi-model AI", "Risk management", "PWA"], foot="Personal software  ·  no public link",
  svg=lambda: (
    box(0, 70, 190, 110, "Scanner", "a short list") +
    box(250, 10, 170, 100, "Claude") + box(250, 150, 170, 100, "Grok") +
    box(480, 60, 200, 130, "Both agree?", "smaller size wins", hot=True) +
    box(740, 0, 260, 100, "Risk in code", "hard caps") + box(740, 135, 260, 100, "Your approval", "on by default") +
    box(740, 270, 260, 100, "Stop at broker") +
    arrow(190, 105, 245, 65) + arrow(190, 145, 245, 195) + arrow(420, 60, 475, 105) + arrow(420, 200, 475, 150) +
    arrow(680, 110, 735, 55) + arrow(870, 100, 870, 130) + arrow(870, 235, 870, 265) +
    '<text x="340" y="330" class="cap">Every signal logged</text><text x="340" y="362" class="cap">every AI decision kept with its reasoning</text>'))

D["pgp"] = dict(cat="Offline key manager", name="PocketPGP", tag="Encrypt, decrypt, sign and verify text and files, with no network.",
  chips=["OpenPGP.js", "Works with GnuPG", "Android", "Windows", "WebView", "Robolectric"], foot="Android + Windows app  ·  no public link",
  svg=lambda: (
    box(20, 20, 210, 100, "Encrypt", hot=True) + box(250, 20, 210, 100, "Decrypt") + box(20, 140, 210, 100, "Sign") + box(250, 140, 210, 100, "Verify", hot=True) +
    '<rect x="20" y="270" width="440" height="110" rx="14" fill="#08110e" stroke="#2a4a40" stroke-width="2.5"/>'
    '<text x="240" y="318" class="bl">Curve25519 · RSA 3072/4096</text><text x="240" y="352" class="bs">a glyph from each fingerprint</text>'
    + "".join(f'<circle cx="{620+ (i%4)*70}" cy="{70+(i//4)*70}" r="{12+((i*7)%5)*4}" fill="none" stroke="#3cf0b4" stroke-width="{2+(i%3)}" opacity="{0.4+0.15*(i%4)}"/>' for i in range(12)) +
    box(560, 270, 400, 110, "One encrypted sync file", "in your own cloud drive") +
    '<text x="760" y="420" class="cap">No INTERNET permission on Android</text>'))

D["punchlist"] = dict(cat="AI consulting", name="The Punchlist", tag="An AI automation consultancy, productized into a platform.",
  chips=["AI advisor", "Solution library", "Live UI previews", "Lead qualification"], foot="thepunchlist.vercel.app",
  svg=lambda: (
    '<rect x="20" y="40" width="420" height="300" rx="16" fill="#08110e" stroke="#3cf0b4" stroke-width="3"/>'
    '<text x="60" y="100" class="lt">Describe your bottleneck</text><rect x="60" y="125" width="340" height="120" rx="10" fill="#10221d"/>'
    '<text x="80" y="170" class="lt2">"We re-key every invoice</text><text x="80" y="205" class="lt2">into two systems…"</text>'
    + box(520, 20, 440, 100, "Pattern already shipped", "in your industry", hot=True) + box(520, 150, 440, 100, "Scoped fix") + box(520, 280, 440, 100, "Live interactive preview") +
    arrow(440, 190, 515, 70) + arrow(740, 120, 740, 145) + arrow(740, 250, 740, 275)))

D["mari"] = dict(cat="D2C storefront", name="Mari' Cosmetics", tag="An affordable-luxury beauty storefront with guided shade matching.",
  chips=["Base44", "Shade-match flow", "Editorial looks", "E-commerce"], foot="mariaelena.base44.app",
  svg=lambda: (
    "".join(f'<circle cx="{110+i*120}" cy="110" r="46" fill="{c}"/>' for i, c in enumerate(["#f3d9c4", "#e2b89a", "#c99572", "#a8744f", "#7d5236", "#5a3824", "#3d2618", "#2a1a10"])) +
    box(40, 220, 260, 120, "Undertone?") + box(370, 220, 260, 120, "Coverage?") + box(700, 220, 260, 120, "Your match", hot=True) +
    arrow(300, 280, 365, 280) + arrow(630, 280, 695, 280)))

D["hire"] = dict(cat="Web résumé", name="Hire Mariaelena", tag="A candidate's entire case, built as a single persuasive page.",
  chips=["Evidence-first", "Capability tags", "Local SEO", "Mobile-first"], foot="hiremariaelena.com",
  svg=lambda: (
    '<rect x="300" y="0" width="400" height="390" rx="16" fill="#08110e" stroke="#3cf0b4" stroke-width="3"/>'
    '<text x="500" y="50" class="bl">Why Mariaelena</text>'
    + "".join(f'<rect x="340" y="{75+i*26}" width="{320-(i%3)*60}" height="12" rx="6" fill="#2a4a40"/>' for i in range(4)) +
    '<text x="500" y="210" class="bs">Experience as outcomes</text>'
    + "".join(f'<rect x="{335+(i%3)*112}" y="{235+(i//3)*44}" width="100" height="32" rx="16" fill="#10221d" stroke="#2a4a40"/>' for i in range(6)) +
    '<text x="385" y="257" class="tg">HRIS</text><text x="497" y="257" class="tg">E-Verify</text><text x="609" y="257" class="tg">Leave</text>'
    '<text x="385" y="301" class="tg">Union/CBA</text><text x="497" y="301" class="tg">H-1B</text><text x="609" y="301" class="tg">Benefits</text>'
    '<rect x="340" y="335" width="320" height="38" rx="10" fill="#3cf0b4"/><text x="500" y="361" class="bk">Contact</text>'
    ''))

CSS = """
*{margin:0;box-sizing:border-box}
body{width:%dpx;height:%dpx;background:#050706;color:#e8fff6;font-family:'Segoe UI',Arial,sans-serif;position:relative;overflow:hidden}
.grid{position:absolute;inset:0;background-image:linear-gradient(#0d1d18 1px,transparent 1px),linear-gradient(90deg,#0d1d18 1px,transparent 1px);background-size:48px 48px;opacity:.55}
.glow{position:absolute;width:900px;height:900px;right:-300px;top:-420px;background:radial-gradient(circle,#0f3a2e 0,transparent 65%%)}
.wrap{position:absolute;inset:0;padding:64px 72px}
.cat{font:600 26px Consolas,monospace;color:#3cf0b4;letter-spacing:.06em;text-transform:uppercase}
h1{font-size:104px;font-weight:800;line-height:1.02;margin-top:14px;letter-spacing:-.02em}
.tag{font-size:36px;color:#b7d8cc;margin-top:16px;line-height:1.25;max-width:1050px}
svg{position:absolute;left:100px;top:372px}
.chips{position:absolute;left:72px;right:72px;bottom:120px;display:flex;flex-wrap:wrap;gap:12px}
.chip{font:600 22px Consolas,monospace;color:#cfeee2;border:2px solid #2a4a40;background:#08110e;border-radius:10px;padding:8px 16px}
.foot{position:absolute;left:72px;right:72px;bottom:48px;display:flex;justify-content:space-between;font:600 26px Consolas,monospace}
.foot .d{color:#3cf0b4}.foot .b{color:#6f9488}
""" % (W, H)
SVG_CSS = """<style>.bl{font:700 30px 'Segoe UI',Arial;fill:#e8fff6;text-anchor:middle}.bs{font:500 22px 'Segoe UI',Arial;fill:#9dc2b5;text-anchor:middle}
.bk{font:700 22px 'Segoe UI',Arial;fill:#05100c;text-anchor:middle}.cap{font:600 22px Consolas,monospace;fill:#6f9488;text-anchor:middle}
.big{font:800 40px 'Segoe UI',Arial;fill:#e8fff6;text-anchor:middle}.code{font:700 26px Consolas,monospace;text-anchor:middle}
.lt{font:700 28px 'Segoe UI',Arial;fill:#e8fff6}.lt2{font:italic 500 24px 'Segoe UI',Arial;fill:#9dc2b5}.tg{font:600 15px 'Segoe UI',Arial;fill:#cfeee2;text-anchor:middle}</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#3cf0b4"/></marker></defs>"""

for key, d in D.items():
    page = f"""<!doctype html><meta charset="utf-8"><style>{CSS}</style><div class="grid"></div><div class="glow"></div>
<div class="wrap"><div class="cat">{html.escape(d['cat'])}</div><h1>{html.escape(d['name'])}</h1><div class="tag">{html.escape(d['tag'])}</div></div>
<svg width="1000" height="400" viewBox="0 0 1000 440">{SVG_CSS}{d['svg']()}</svg>
<div class="chips">{''.join(f'<span class="chip">{html.escape(c)}</span>' for c in d['chips'])}</div>
<div class="foot"><span class="d">{html.escape(d['foot'])}</span><span class="b">Built solo · ciprari.ai</span></div>"""
    f = OUT / f"{key}.html"; f.write_text(page, encoding="utf-8")
    png = OUT / f"hero-{key}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                    f"--screenshot={png}", "--default-background-color=00000000", f.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", png.name)
