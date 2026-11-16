#!/usr/bin/env python3
"""freshtechupdates channel art.

  python3 banner.py  -> out/channel-banner.png (2560x1440, YouTube banner)
                        out/channel-banner-preview.png (safe-area guides, for checking only)
                        out/profile-picture.png (800x800, 3D FT logo)

YouTube shows the 1546x423 centre on every device and 2560x423 on desktop,
so the logo, name and tagline sit in the centre and illustrations fill the sides.
"""
import pathlib, sys
BASE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import illus
import thumbs
from ftlogo import logo_svg

OUT = BASE / "out"


def scene(name, pid, w):
    svg, _ = illus.SCENES[name](pid, 0, 6, "paper")
    h = round(w * 640 / 1080)
    return (f'<div class="sc" style="display:inline-block"><svg viewBox="0 0 1080 640" width="{w}" height="{h}" '
            f'style="overflow:visible">{svg}</svg></div>')


def banner_html(guides=False):
    g = ""
    if guides:
        g = ('<div style="position:absolute;left:0;right:0;top:508px;height:424px;border:4px dashed #FF4D6D"></div>'
             '<div style="position:absolute;left:507px;width:1546px;top:508px;height:424px;border:4px solid #A3E635"></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{thumbs.css()}
body{{width:2560px;height:1440px}}
.band{{position:absolute;left:0;right:0;top:508px;height:424px}}
.name{{font-family:TH;font-weight:900;font-size:118px;letter-spacing:-4px;color:#F4F6FB;line-height:1;
  text-shadow:0 6px 0 rgba(0,0,0,.5)}}
.name b{{color:#22D3EE;font-weight:900}}
.tag{{font-family:TG;font-weight:700;font-size:44px;color:#F4F6FB;margin-top:18px;letter-spacing:.5px}}
.tag .ac{{color:#0B1230;background:#A3E635;padding:2px 16px;border-radius:12px}}
.pill{{display:inline-flex;gap:14px;align-items:center;font-family:TG;font-weight:700;font-size:26px;letter-spacing:4px;
  color:#22D3EE;border:3px solid rgba(34,211,238,.55);border-radius:40px;padding:10px 26px;margin-top:22px}}
.dot{{width:14px;height:14px;border-radius:50%;background:#FF4D6D;box-shadow:0 0 14px #FF4D6D}}
</style></head><body>
<div class="grid"></div>
<div class="glow" style="left:820px;top:470px;width:900px;height:500px;background:rgba(34,211,238,.18)"></div>
<div class="glow" style="left:-120px;top:520px;width:700px;height:420px;background:rgba(139,92,246,.22)"></div>
<div class="glow" style="left:1980px;top:520px;width:700px;height:420px;background:rgba(163,230,53,.14)"></div>

<!-- side illustrations: visible on desktop and TV -->
<div style="position:absolute;left:30px;top:560px;opacity:.95">{scene("robot", "b1", 470)}</div>
<div style="position:absolute;left:2060px;top:560px;opacity:.95">{scene("rocket", "b2", 470)}</div>
<!-- outer TV-only area -->
<div style="position:absolute;left:180px;top:150px;opacity:.55">{scene("chip", "b3", 520)}</div>
<div style="position:absolute;left:1860px;top:150px;opacity:.55">{scene("globe", "b4", 520)}</div>
<div style="position:absolute;left:180px;top:1000px;opacity:.55">{scene("phone", "b5", 520)}</div>
<div style="position:absolute;left:1860px;top:1000px;opacity:.55">{scene("cloud", "b6", 520)}</div>

<!-- safe area: 1546x423 centred -->
<div class="band" style="display:flex;align-items:center;justify-content:center;gap:56px">
  {logo_svg(330, uid="bn", depth=12, style="filter:drop-shadow(0 18px 30px rgba(0,0,0,.55))")}
  <div>
    <div class="name">fresh<b>tech</b>updates</div>
    <div class="tag">Daily <span class="ac">AI &amp; tech updates</span> in 3 minutes</div>
    <div class="pill"><span class="dot"></span>NEW EPISODE EVERY DAY · @freshtechupdates</div>
  </div>
</div>
{g}
</body></html>"""


def pfp_html():
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{thumbs.css()}
body{{width:800px;height:800px;display:flex;align-items:center;justify-content:center}}
</style></head><body>
<div class="grid"></div>
<div class="glow" style="left:150px;top:200px;width:500px;height:400px;background:rgba(34,211,238,.22)"></div>
<div style="position:relative">{logo_svg(560, uid="pf", depth=12, style="filter:drop-shadow(0 16px 26px rgba(0,0,0,.55))")}</div>
</body></html>"""


def shoot(html_text, w, h, path):
    from playwright.sync_api import sync_playwright
    tmp = OUT / "_art.html"
    tmp.write_text(html_text)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(600)
        pg.screenshot(path=str(path)); b.close()
    tmp.unlink()


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    shoot(banner_html(), 2560, 1440, OUT / "channel-banner.png")
    shoot(banner_html(guides=True), 2560, 1440, OUT / "channel-banner-preview.png")
    shoot(pfp_html(), 800, 800, OUT / "profile-picture.png")
    print("banner + profile picture written to out/")
