#!/usr/bin/env python3
"""freshtechupdates thumbnails and covers (static PNG via Playwright).

  python3 thumbs.py long  episode.json  [show]   -> out/thumbnail.png (A), out/thumbnail-B.png, out/thumbnail-C.png  (1280x720)
  python3 thumbs.py short reel.json              -> out/short-cover.png (1080x1920) + out/short.txt (YouTube Shorts title/description)
  python3 thumbs.py short trend.json trend       -> out/trend-cover.png + out/trend-short.txt (explainer lane)

Three long-video designs for YouTube Studio > Thumbnail > Test & Compare:
  A  "Headline"  big 2-3 line hook + the story-1 illustration on a glowing stage
  B  "Callout"   giant stat (or alt hook) + illustration with a red arrow / circle callout
  C  "Rundown"   "N big AI & tech updates" with the top-3 illustrations as tiles
All share one brand look (dark navy, cyan / lime / coral, 3D FT logo) so the channel is recognisable.
"""
import json, sys, re, html, os, pathlib
BASE = pathlib.Path(__file__).resolve().parent
NM = BASE / "node_modules"
sys.path.insert(0, str(BASE))
import illus
from ftlogo import logo_svg

E = html.escape
BRAND = dict(family="flat", fills=["#22D3EE", "#FF4D6D", "#F4F6FB", "#FFD166", "#8B5CF6"], line="#F4F6FB", acc="#A3E635", light=False)

def plain(t): return re.sub(r"\*", "", t or "")

def accent_html(text, cls="ac"):
    out = []
    for tok in re.findall(r"\*[^*]+\*|[^*]+", text):
        if tok.startswith("*"): out.append(f'<span class="{cls}">{E(tok.strip("*"))}</span>')
        else: out.append(E(tok))
    return "".join(out)

def scene_svg(story, pid, w, h):
    name = illus.pick(story); svg, _ = illus.SCENES[name](pid, 0, 6, "paper")
    return f'<div class="sc" style="display:inline-block"><svg class="scn" viewBox="0 0 1080 640" width="{w}" height="{h}" style="overflow:visible">{svg}</svg></div>'

def css():
    import longform as LF
    fonts = "".join(f"@font-face{{font-family:{f};font-weight:100 900;src:url('file://{NM / s}')}}" for f, s in (
        ("TH", "@fontsource/inter/files/inter-latin-900-normal.woff2"), ("TG", "@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2"),
        ("FTHead", "@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2"), ("FTBody", "@fontsource/inter/files/inter-latin-800-normal.woff2")))
    return fonts + LF.scene_css(BRAND) + """
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;position:relative;background:radial-gradient(circle at 72% 45%,#1b2b6b 0%,#0B1230 45%,#05070F 100%)}
.grid{position:absolute;inset:0;background:linear-gradient(rgba(255,255,255,.04) 2px,transparent 2px) 0 0/80px 80px,linear-gradient(90deg,rgba(255,255,255,.04) 2px,transparent 2px) 0 0/80px 80px}
.glow{position:absolute;border-radius:50%;filter:blur(40px)}
.sc [id$="-sfx"]{display:none}
.brand{position:absolute;display:flex;align-items:center;gap:12px;font-family:TG;font-weight:700;color:#F4F6FB}
.brand b{color:#22D3EE;font-weight:700}
.hk{font-family:TH;font-weight:900;color:#FFFFFF;line-height:.98;letter-spacing:-2px;text-transform:uppercase;
    text-shadow:0 6px 0 rgba(0,0,0,.55),0 0 40px rgba(0,0,0,.6)}
.hk .ac{color:#0B1230;background:#A3E635;padding:0 14px;border-radius:12px;box-decoration-break:clone;-webkit-box-decoration-break:clone;text-shadow:none}
.chip{position:absolute;font-family:TG;font-weight:700;letter-spacing:3px;border-radius:12px;padding:10px 20px}
"""

def render(html_doc, out_png, w, h):
    from playwright.sync_api import sync_playwright
    tmp = pathlib.Path(out_png).with_suffix(".html"); tmp.write_text(html_doc)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH", "/usr/bin/google-chrome"), args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": w, "height": h}); pg.goto(f"file://{tmp.resolve()}"); pg.wait_for_timeout(500)
        pg.screenshot(path=str(out_png)); b.close()
    tmp.unlink()

def page(body, w, h):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css()} body{{width:{w}px;height:{h}px}}</style></head><body>'
            '<div class="grid"></div><svg width="0" height="0" style="position:absolute"><defs><filter id="ps"><feDropShadow dx="0" dy="9" stdDeviation="0" flood-color="#000" flood-opacity=".25"/></filter></defs></svg>'
            f'{body}</body></html>')

def fit(text, sizes):
    n = len(plain(text))
    for lim, sz in sizes:
        if n <= lim: return sz
    return sizes[-1][1]

# ------------------------------------------------------------------ long video (1280x720)
def long_thumbs(data, show_name="", outdir=BASE / "out"):
    outdir = pathlib.Path(outdir); outdir.mkdir(exist_ok=True)
    st = data["stories"]; top = st[0]; n = len(st)
    hook = data.get("thumb_text") or top["headline"]
    brand = f'<div class="brand" style="left:36px;top:30px;font-size:30px">{logo_svg(74, uid="tb")}<span><b>fresh</b>techupdates</span></div>'
    show = f'<div class="chip" style="right:34px;top:34px;font-size:22px;background:rgba(255,255,255,.1);color:#F4F6FB">{E(show_name)}</div>' if show_name else ""

    # A: headline + big illustration
    sz = fit(hook, [(14, 132), (20, 116), (28, 100), (40, 86), (99, 74)])
    a = (brand + show + '<div class="glow" style="right:40px;top:120px;width:560px;height:520px;background:rgba(34,211,238,.28)"></div>'
         f'<div style="position:absolute;right:-70px;top:120px">{scene_svg(top, "ta", 830, 492)}</div>'
         f'<div class="hk" style="position:absolute;left:44px;top:150px;width:640px;font-size:{sz}px">{accent_html(hook)}</div>'
         f'<div class="chip" style="left:44px;bottom:40px;font-size:24px;background:#FF4D6D;color:#fff">+{n-1} MORE UPDATES</div>')
    render(page(a, 1280, 720), outdir / "thumbnail.png", 1280, 720)

    # B: callout (stat if real, else alternative hook)
    stat = top.get("stat") if isinstance(top.get("stat"), dict) and top["stat"].get("value") else None
    big = stat["value"] if stat else plain(data.get("thumb_text_b") or hook).upper()
    sub = (stat.get("label", "") if stat else plain(top["headline"]))
    bsz = fit(big, [(5, 230), (8, 170), (12, 120), (20, 96), (99, 80)])
    arrow = ('<svg style="position:absolute;left:520px;top:300px" width="230" height="170" viewBox="0 0 230 170">'
             '<path d="M10,140 C70,150 140,120 180,50" stroke="#FF3B3B" stroke-width="18" fill="none" stroke-linecap="round"/>'
             '<path d="M150,40 L200,20 L196,78 Z" fill="#FF3B3B" stroke="#FF3B3B" stroke-width="8" stroke-linejoin="round"/></svg>')
    ring = '<div style="position:absolute;left:760px;top:170px;width:420px;height:330px;border:12px solid #FF3B3B;border-radius:50%;transform:rotate(-8deg)"></div>'
    b = (brand + show + '<div class="glow" style="right:80px;top:140px;width:480px;height:440px;background:rgba(255,77,109,.28)"></div>'
         f'<div style="position:absolute;right:-40px;top:130px">{scene_svg(top, "tb2", 760, 450)}</div>' + ring + arrow +
         f'<div class="hk" style="position:absolute;left:44px;top:170px;width:620px;font-size:{bsz}px;color:#A3E635">{E(big)}</div>'
         f'<div class="hk" style="position:absolute;left:48px;top:{170 + int(bsz*1.05*(1 if len(big) < 13 else 2)) + 20}px;width:560px;font-size:44px;text-transform:none;letter-spacing:-1px">{E(sub)}</div>')
    render(page(b, 1280, 720), outdir / "thumbnail-B.png", 1280, 720)

    # C: rundown tiles
    tiles = ""
    for i, s in enumerate(st[:3]):
        x = 40 + i * 410
        tiles += (f'<div style="position:absolute;left:{x}px;top:250px;width:390px;height:330px;border-radius:26px;background:rgba(255,255,255,.07);'
                  f'border:3px solid rgba(255,255,255,.14);overflow:hidden">{scene_svg(s, f"tc{i}", 390, 231)}'
                  f'<div style="position:absolute;left:18px;right:18px;bottom:16px;font-family:TH;font-weight:900;font-size:27px;line-height:1.05;color:#fff">{E(plain(s["headline"]))}</div>'
                  f'<div style="position:absolute;left:14px;top:14px;width:52px;height:52px;border-radius:50%;background:#FFD166;color:#0B1230;font-family:TH;font-size:30px;display:flex;align-items:center;justify-content:center">{i+1}</div></div>')
    c = (brand + show + f'<div class="hk" style="position:absolute;left:44px;top:120px;font-size:84px;white-space:nowrap">{n} BIG <span class="ac">AI &amp; TECH</span> UPDATES</div>' + tiles +
         '<div class="chip" style="left:44px;bottom:36px;font-size:24px;background:#22D3EE;color:#0B1230">TODAY&#39;S FULL RUNDOWN</div>')
    render(page(c, 1280, 720), outdir / "thumbnail-C.png", 1280, 720)

# ------------------------------------------------------------------ Short / Reel cover (1080x1920, key content inside the 3:4 centre)
def short_cover(reel, outdir=BASE / "out", prefix="short"):
    """Cover + Shorts text. prefix "short" -> short-cover.png / short.txt (daily);
    prefix "trend" -> trend-cover.png / trend-short.txt (explainer lane)."""
    outdir = pathlib.Path(outdir); outdir.mkdir(exist_ok=True)
    explainer = reel.get("mode") == "explainer"
    hook = reel["hook"]["headline"]; s0 = reel["stories"][0]
    sz = fit(hook, [(14, 150), (22, 128), (32, 108), (99, 92)])
    chip = reel["hook"].get("more") or ("Explained in 40 seconds" if explainer else "+2 more AI & tech updates")
    chip_bg = "#22D3EE;color:#0B1230" if explainer else "#FF4D6D;color:#fff"
    kicker = ('<div class="chip" style="left:50%;transform:translateX(-50%);top:1010px;font-size:30px;background:#A3E635;color:#0B1230;white-space:nowrap">TRENDING NOW</div>'
              if explainer else "")
    body = (f'<div class="brand" style="left:0;right:0;top:300px;justify-content:center;font-size:44px">{logo_svg(110, uid="sc")}<span><b>fresh</b>techupdates</span></div>'
            '<div class="glow" style="left:140px;top:430px;width:800px;height:640px;background:rgba(34,211,238,.3)"></div>'
            f'<div style="position:absolute;left:-20px;top:430px">{scene_svg(s0, "sc0", 1120, 663)}</div>'
            f'{kicker}<div class="hk" style="position:absolute;left:60px;right:60px;top:1110px;text-align:center;font-size:{sz}px">{accent_html(hook)}</div>'
            f'<div class="chip" style="left:50%;transform:translateX(-50%);top:1560px;font-size:34px;background:{chip_bg};white-space:nowrap">{E(chip.upper())}</div>')
    render(page(body, 1080, 1920), outdir / f"{prefix}-cover.png", 1080, 1920)
    if explainer:
        topic = plain(reel.get("topic") or hook)
        title = (reel.get("title") or f"{topic}: explained").strip()
        title = plain(title)[:95]
        desc = [plain(reel["hook"].get("voice", hook)).strip(), ""]
        desc += [f"{plain(s.get('label') or str(i+1)).title()}: {plain(s['headline'])}" for i, s in enumerate(reel["stories"])]
        srcs = reel.get("sources") or []
        if srcs:
            desc += ["", "Sources:"] + [f"- {x}" for x in srcs]
        desc += ["", "A new AI & tech explainer every day, plus daily updates: @freshtechupdates", "",
                 "#shorts #explained #AI #tech #freshtechupdates"]
        name = f"{prefix}-short.txt"
    else:
        title = plain(hook)
        title = (title + " | AI & Tech Updates")[:95]
        desc = [plain(hook) + ".", ""] + [f"{i+1}. {plain(s['headline'])} ({s['source']})" for i, s in enumerate(reel["stories"])]
        desc += ["", "Full episode with all of today's updates on our channel: @freshtechupdates", "", "#shorts #AI #TechNews #AIupdates #freshtechupdates"]
        name = "short.txt" if prefix == "short" else f"{prefix}-short.txt"
    (outdir / name).write_text(f"TITLE:\n{title}\n\nDESCRIPTION:\n" + "\n".join(desc) + "\n")
    return outdir / f"{prefix}-cover.png", outdir / name

if __name__ == "__main__":
    kind, src = sys.argv[1], json.loads(pathlib.Path(sys.argv[2]).read_text())
    if kind == "long":
        import longform as LF, datetime
        ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        show = int(sys.argv[3]) if len(sys.argv) > 3 else ist.isoweekday()
        long_thumbs(src, LF.SHOWS[show]["name"])
        print("thumbnails: out/thumbnail.png out/thumbnail-B.png out/thumbnail-C.png")
    else:
        prefix = sys.argv[3] if len(sys.argv) > 3 else "short"
        c, t = short_cover(src, prefix=prefix); print(f"cover: out/{c.name}  text: out/{t.name}")
