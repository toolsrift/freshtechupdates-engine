#!/usr/bin/env python3
"""freshtechupdates carousel renderer.
Usage: python3 render.py slides.json out_dir
Needs (in this folder): npm i lucide-static @fontsource/space-grotesk @fontsource/inter
"""
import json, sys, re, html, pathlib, os
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).resolve().parent
NM = BASE / "node_modules"
ICONS = NM / "lucide-static" / "icons"

def icon(name, size, stroke="#F8FAFC", sw="1.6"):
    p = ICONS / f"{name}.svg"
    if not p.exists():
        p = ICONS / "sparkles.svg"
    s = p.read_text()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r'width="24"', f'width="{size}"', s)
    s = re.sub(r'height="24"', f'height="{size}"', s)
    s = s.replace('stroke="currentColor"', f'stroke="{stroke}"')
    s = re.sub(r'stroke-width="[\d.]+"', f'stroke-width="{sw}"', s)
    return s

def esc(t):
    # *word* -> cyan accent
    t = html.escape(t)
    return re.sub(r"\*(.+?)\*", r'<span class="acc">\1</span>', t)

CHIP = '''<svg width="{s}" height="{s}" viewBox="180 180 720 720" aria-hidden="true">
<g stroke="#8B5CF6" stroke-width="22" stroke-linecap="round">
''' + "".join(
    f'<line x1="{x}" y1="258" x2="{x}" y2="196"/><line x1="{x}" y1="822" x2="{x}" y2="884"/>'
    f'<line x1="258" y1="{x}" x2="196" y2="{x}"/><line x1="822" y1="{x}" x2="884" y2="{x}"/>'
    for x in (370, 483, 597, 710)) + '''</g>
<rect x="260" y="260" width="560" height="560" rx="80" fill="#111833" stroke="#22D3EE" stroke-width="22"/>
<circle cx="742" cy="338" r="34" fill="#A3E635"/>
<text x="540" y="552" text-anchor="middle" dominant-baseline="middle" font-family="SG" font-weight="700" font-size="300" letter-spacing="-12" fill="#F8FAFC">FT</text>
</svg>'''

def chip(s):
    return CHIP.replace("{s}", str(s))

CSS = f'''
@font-face{{font-family:SG;font-weight:500;src:url("file://{NM}/@fontsource/space-grotesk/files/space-grotesk-latin-500-normal.woff2")}}
@font-face{{font-family:SG;font-weight:700;src:url("file://{NM}/@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2")}}
@font-face{{font-family:IN;font-weight:500;src:url("file://{NM}/@fontsource/inter/files/inter-latin-500-normal.woff2")}}
@font-face{{font-family:IN;font-weight:600;src:url("file://{NM}/@fontsource/inter/files/inter-latin-600-normal.woff2")}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;overflow:hidden;background:#0A0F1F;font-family:IN,sans-serif;color:#F8FAFC}}
.bg{{position:absolute;inset:0;background:
radial-gradient(circle at 88% 12%,rgba(34,211,238,.28),transparent 38%),
radial-gradient(circle at 8% 92%,rgba(139,92,246,.30),transparent 42%),
linear-gradient(rgba(34,211,238,.045) 2px,transparent 2px) 0 0/60px 60px,
linear-gradient(90deg,rgba(34,211,238,.045) 2px,transparent 2px) 0 0/60px 60px,
linear-gradient(180deg,#0A0F1F,#05070F)}}
.wrap{{position:relative;height:1350px;padding:64px 72px 56px;display:flex;flex-direction:column}}
.hdr{{display:flex;align-items:center;justify-content:space-between}}
.brand{{display:flex;align-items:center;gap:18px;font-family:SG;font-weight:700;font-size:38px;letter-spacing:-1px}}
.lime{{color:#A3E635}} .acc{{color:#22D3EE}}
.count{{font-family:SG;font-weight:500;font-size:26px;color:#CBD5E1;border:2px solid rgba(255,255,255,.16);border-radius:999px;padding:8px 22px}}
.pill{{align-self:flex-start;font-family:SG;font-weight:700;font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#A3E635;border:2px solid rgba(163,230,53,.6);border-radius:999px;padding:10px 24px;background:rgba(163,230,53,.06)}}
.visual{{position:relative;height:540px;display:flex;align-items:center;justify-content:center;margin:18px 0 10px}}
.ring{{position:absolute;border-radius:50%;border:2px solid rgba(34,211,238,.22)}}
.ring.r1{{width:480px;height:480px}} .ring.r2{{width:360px;height:360px;border-color:rgba(139,92,246,.3);border-style:dashed}}
.dot{{position:absolute;border-radius:50%}}
.glass{{position:relative;width:290px;height:290px;border-radius:64px;display:flex;align-items:center;justify-content:center;
background:linear-gradient(145deg,rgba(139,92,246,.42),rgba(34,211,238,.14) 70%);border:2px solid rgba(255,255,255,.2);
box-shadow:0 40px 90px rgba(34,211,238,.25),0 0 0 14px rgba(255,255,255,.025),inset 0 2px 0 rgba(255,255,255,.25)}}
.glass svg{{filter:drop-shadow(0 0 18px rgba(34,211,238,.8))}}
h1{{font-family:SG;font-weight:700;font-size:78px;line-height:1.08;letter-spacing:-1.5px}}
.hbox{{}}
.body{{font-size:38px;line-height:1.42;color:#CBD5E1;margin-top:26px;font-weight:500}}
.grow{{flex:1}}
.ftr{{display:flex;justify-content:space-between;align-items:center;border-top:2px solid rgba(255,255,255,.1);padding-top:24px;font-size:25px;color:#94A3B8;font-weight:500}}
.ftr .src{{max-width:700px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.ftr .swipe{{color:#22D3EE;font-family:SG;font-weight:700;display:flex;align-items:center;gap:8px}}
.list{{display:flex;flex-direction:column;gap:34px;margin-top:60px}}
.li{{display:flex;align-items:center;gap:26px;font-size:37px;font-weight:600;line-height:1.25}}
.num{{flex:0 0 64px;height:64px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-family:SG;font-weight:700;font-size:30px;color:#0A0F1F;background:linear-gradient(145deg,#22D3EE,#8B5CF6)}}
.cta{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:26px}}
.btns{{display:flex;gap:22px;margin-top:20px}}
.btn{{display:flex;align-items:center;gap:12px;font-family:SG;font-weight:700;font-size:30px;padding:18px 30px;border-radius:999px;border:2px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05)}}
'''

FIT = '''<script>
document.fonts.ready.then(()=>{
 document.querySelectorAll('[data-fit]').forEach(el=>{
  const max=parseFloat(el.dataset.fit); let f=parseFloat(getComputedStyle(el).fontSize);
  while(el.offsetHeight>max && f>40){f-=2; el.style.fontSize=f+'px';}
 });
 document.body.setAttribute('data-ready','1');
});
</script>'''

def page(inner):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="bg"></div><div class="wrap">{inner}</div>{FIT}</body></html>'

def header(n, total):
    return (f'<div class="hdr"><div class="brand">{chip(76)}<span><span class="lime">fresh</span>techupdates</span></div>'
            f'<div class="count">{n}/{total}</div></div>')

def visual(ic):
    return ('<div class="visual"><div class="ring r1"></div><div class="ring r2"></div>'
            '<div class="dot" style="width:22px;height:22px;background:#A3E635;top:40px;left:calc(50% + 150px);box-shadow:0 0 20px #A3E635"></div>'
            '<div class="dot" style="width:16px;height:16px;background:#8B5CF6;bottom:70px;left:calc(50% - 230px);box-shadow:0 0 18px #8B5CF6"></div>'
            '<div class="dot" style="width:12px;height:12px;background:#22D3EE;top:200px;left:calc(50% + 238px);box-shadow:0 0 16px #22D3EE"></div>'
            f'<div class="glass">{icon(ic, 160)}</div></div>')

def swipe(label="Swipe"):
    return f'<span class="swipe">{label} {icon("arrow-right", 30, "#22D3EE", "2.5")}</span>'

def cover(d, total):
    items = "".join(f'<div class="li"><div class="num">{i+1}</div><div>{esc(t)}</div></div>' for i, t in enumerate(d["teasers"][:5]))
    return page(header(1, total) +
        f'<div style="height:56px"></div><div class="pill">{esc(d.get("kicker","Top 5 AI & tech updates"))}</div>'
        f'<div class="hbox" style="margin-top:34px"><h1 data-fit="330" style="font-size:104px">{esc(d["headline"])}</h1></div>'
        f'<div class="list">{items}</div><div class="grow"></div>'
        f'<div class="ftr"><span class="src">Sources on every slide</span>{swipe("Swipe for details")}</div>')

def story(s, n, total):
    return page(header(n, total) +
        f'<div style="height:40px"></div><div class="pill">{esc(s["category"])}</div>' + visual(s.get("icon", "sparkles")) +
        f'<div class="hbox"><h1 data-fit="260">{esc(s["headline"])}</h1></div>'
        f'<p class="body">{esc(s["body"])}</p><div class="grow"></div>'
        f'<div class="ftr"><span class="src">Source: {html.escape(s["source"])}</span>{swipe()}</div>')

def cta(n, total):
    return page(header(n, total) +
        f'<div class="cta">{chip(300)}'
        '<div style="font-family:SG;font-weight:700;font-size:44px;color:#CBD5E1;margin-top:20px">Follow for daily updates</div>'
        '<div style="font-family:SG;font-weight:700;font-size:76px;letter-spacing:-2px">@<span class="lime">fresh</span>techupdates</div>'
        '<div style="font-size:34px;color:#94A3B8;font-weight:500">Daily AI &amp; tech news, made simple</div>'
        f'<div class="btns"><div class="btn">{icon("heart",34,"#F8FAFC","2.2")}Like</div>'
        f'<div class="btn">{icon("bookmark",34,"#A3E635","2.2")}Save</div>'
        f'<div class="btn">{icon("send",34,"#22D3EE","2.2")}Share</div></div></div>'
        f'<div class="ftr" style="justify-content:center;gap:12px">{icon("bell",28,"#94A3B8","2.2")}<span>Turn on notifications so you never miss an update</span></div>')

def main():
    data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    stories = data["stories"]
    total = len(stories) + 2
    pages = [cover(data["cover"], total)] + [story(s, i + 2, total) for i, s in enumerate(stories)] + [cta(total, total)]
    with sync_playwright() as p:
        chrome = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")
        kw = {"executable_path": chrome} if os.path.exists(chrome) else {}
        b = p.chromium.launch(args=["--allow-file-access-from-files"], **kw)
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, h in enumerate(pages, 1):
            f = out / f"slide-{i:02d}.html"
            f.write_text(h)
            pg.goto(f.as_uri())
            pg.wait_for_selector("body[data-ready='1']", timeout=15000)
            pg.screenshot(path=str(out / f"slide-{i:02d}.png"))
            f.unlink()
            print("rendered", out / f"slide-{i:02d}.png")
        b.close()

if __name__ == "__main__":
    main()
