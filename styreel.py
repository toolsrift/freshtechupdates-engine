#!/usr/bin/env python3
"""freshtechupdates styled Reel (paper | comic | blueprint) -> HyperFrames project, 1080x1920 @30fps.
Usage: python3 styreel.py reel.json <project_dir> <style>
reel.json: {"hook":{"headline","more","voice"}, "stories":[{"category","shape","headline","source","voice"} x3],
            "outro_question","outro_voice"}
shape (animated scene): rocket | robot | shield | phone | bolt | chip | globe
Needs in this folder: node_modules (gsap, @fontsource/space-grotesk, @fontsource/inter, @fontsource/bangers,
@fontsource/space-mono), kokoro-v1.0.onnx + voices-v1.0.bin, python: kokoro-onnx soundfile numpy.
"""
import json, sys, re, html, pathlib, shutil, random
import numpy as np, soundfile as sf

BASE = pathlib.Path(__file__).resolve().parent
NM = BASE / "node_modules"
FPS, SR = 30, 24000
VOICE, SPEED = "af_heart", 1.15
SHAPES = ("rocket", "robot", "shield", "phone", "bolt", "chip", "globe")
SFX = {"rocket": "LIFT-OFF!", "robot": "WATCH & LEARN", "shield": "BLOCKED!", "phone": "NEW DROP!",
       "bolt": "POWER UP!", "chip": "NEW MODEL!", "globe": "WORLDWIDE"}
SHAPE_WORDS = [("rocket", "fund|ipo|invest|rais|launch|valuation|business|startup|market|stock"),
               ("robot", "robot|agent|humanoid|automation"),
               ("shield", "secur|privacy|breach|hack|scam|regulat|law|ban|court|policy"),
               ("phone", "phone|gadget|device|iphone|pixel|galaxy|wearable|watch|glasses|laptop"),
               ("bolt", "energy|power|electric|battery|data cent"),
               ("globe", "india|global|world|government|upi|telecom")]

def pick_shape(s):
    if s.get("shape") in SHAPES: return s["shape"]
    txt = (s.get("category", "") + " " + s.get("headline", "")).lower()
    for shp, pat in SHAPE_WORDS:
        if re.search(pat, txt): return shp
    return "chip"

def T(x): return f"{x:.3f}"
def E(s): return html.escape(str(s))

# ------------------------------------------------------------------ styles
STYLES = {
 "paper": dict(
  fonts=[("FTHead", 700, "@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2"),
         ("FTBody", 800, "@fontsource/inter/files/inter-latin-800-normal.woff2")],
  ink="#F3EBDD", hl="#B5E05A", capword="#8F6CF0",
  css="""
#bgc{background:#1E2452}
#noise{opacity:.22;mix-blend-mode:overlay}
.sc svg .f1{fill:#4FD1E8} .sc svg .f2{fill:#8F6CF0} .sc svg .f3{fill:#F3EBDD} .sc svg .f4{fill:#B5E05A} .sc svg .f5{fill:#FF8A65}
.sc svg .eye{fill:#1E2452} .sc svg .eyeG{fill:#B5E05A}
.sc svg .ln{stroke:#F3EBDD;stroke-width:12;fill:none;stroke-linecap:round}
.sc svg .lnA{stroke:#B5E05A;stroke-width:12;fill:none;stroke-linecap:round;stroke-linejoin:round}
.sc svg .lnT{stroke:#F3EBDD;stroke-width:5;fill:none;stroke-linecap:round}
.sc svg .lnE{stroke:#1E2452;stroke-width:6;fill:none;stroke-linecap:round}
.sc svg .beam{stroke:#B5E05A;stroke-width:5;fill:none;stroke-dasharray:14 12}
.sc svg .flame{fill:#FF8A65}
.sc svg .pp{filter:url(#ps)}
.sc svg .lbl{font-family:FTHead;font-weight:700;font-size:34px;fill:#F3EBDD;letter-spacing:3px}
.sc svg .chiptext{font-family:FTHead;font-weight:700;font-size:96px;fill:#1E2452}
.sfxbox{fill:#F3EBDD} .sfxtxt{font-family:FTHead;font-weight:700;font-size:44px;fill:#1E2452;letter-spacing:2px}
.h1{font-family:FTHead;font-weight:700;color:#F3EBDD;letter-spacing:-2px;line-height:1.05;font-size:82px}
.h1 .acc .w{background:#B5E05A;color:#1E2452;padding:0 12px;border-radius:6px;box-shadow:0 8px 0 rgba(0,0,0,.28)}
.tag{font-family:FTHead;font-weight:700;font-size:28px;letter-spacing:3px;text-transform:uppercase;color:#1E2452;background:#B5E05A;padding:10px 22px;border-radius:6px;box-shadow:0 7px 0 rgba(0,0,0,.28)}
.num{font-family:FTHead;font-weight:700;font-size:32px;color:#1E2452;background:#F3EBDD;padding:8px 16px;border-radius:6px;box-shadow:0 7px 0 rgba(0,0,0,.28)}
.src{font-family:FTBody;font-weight:800;font-size:24px;color:#AEB4D6}
.capbox{background:#F3EBDD;color:#1E2452;border-radius:14px;box-shadow:0 10px 0 rgba(0,0,0,.3);transform:rotate(-1deg)}
.badge{background:#FF8A65;color:#1E2452;border-radius:8px;box-shadow:0 9px 0 rgba(0,0,0,.3)}
.brandtxt{color:#F3EBDD} .bar{background:rgba(243,235,221,.2)} .fill{background:#B5E05A}
"""),
 "comic": dict(
  fonts=[("FTHead", 400, "@fontsource/bangers/files/bangers-latin-400-normal.woff2"),
         ("FTBody", 800, "@fontsource/inter/files/inter-latin-800-normal.woff2")],
  ink="#111111", hl="#FF4D6D", capword="#FF4D6D",
  css="""
#bgc{background:#FFD93D}
#dots{background:radial-gradient(circle,rgba(255,77,109,.28) 28%,transparent 31%) 0 0/28px 28px}
#rays{background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,.38) 0deg 9deg,transparent 9deg 22deg)}
.panel{position:absolute;left:54px;top:296px;width:972px;height:608px;background:#fff;border:8px solid #111;box-shadow:14px 14px 0 #111;overflow:hidden}
.panel::before{content:"";position:absolute;inset:0;background:radial-gradient(circle,rgba(41,197,246,.30) 26%,transparent 29%) 0 0/22px 22px}
.sc svg *{stroke:#111;stroke-width:7;stroke-linejoin:round;stroke-linecap:round}
.sc svg .f1{fill:#29C5F6} .sc svg .f2{fill:#FF4D6D} .sc svg .f3{fill:#FFFFFF} .sc svg .f4{fill:#FFD93D} .sc svg .f5{fill:#FF8A3D}
.sc svg .eye{fill:#111} .sc svg .eyeG{fill:#29C5F6}
.sc svg .ln{stroke-width:11;fill:none} .sc svg .lnA{stroke:#FF4D6D;stroke-width:12;fill:none}
.sc svg .lnT{stroke-width:5;fill:none} .sc svg .lnE{stroke-width:6;fill:none}
.sc svg .beam{stroke:#FF4D6D;stroke-width:6;fill:none;stroke-dasharray:14 12}
.sc svg .flame{fill:#FF8A3D}
.sc svg .lbl{font-family:FTHead;font-size:40px;fill:#111;stroke:none;letter-spacing:2px}
.sc svg .chiptext{font-family:FTHead;font-size:110px;fill:#111;stroke:none}
.sfxbox{fill:#FFD93D} .sfxtxt{font-family:FTHead;font-size:58px;fill:#FF4D6D;stroke:#111;stroke-width:3px;paint-order:stroke;letter-spacing:2px}
.h1{font-family:FTHead;color:#111;line-height:.98;font-size:94px;letter-spacing:1px;background:#fff;border:7px solid #111;box-shadow:12px 12px 0 #111;padding:18px 30px;transform:rotate(-1.5deg)}
.h1 .acc{color:#FF4D6D}
.tag{font-family:FTHead;font-size:38px;letter-spacing:2px;color:#fff;background:#FF4D6D;border:5px solid #111;padding:4px 20px;box-shadow:6px 6px 0 #111}
.num{font-family:FTHead;font-size:50px;color:#111;background:#29C5F6;border:5px solid #111;padding:2px 18px;box-shadow:6px 6px 0 #111;transform:rotate(-6deg)}
.src{font-family:FTBody;font-weight:800;font-size:24px;color:#111;background:#fff;border:4px solid #111;padding:4px 12px}
.capbox{background:#fff;color:#111;border:6px solid #111;box-shadow:9px 9px 0 #111}
.badge{background:#FF4D6D;color:#fff;border:6px solid #111;box-shadow:9px 9px 0 #111}
.brandtxt{color:#111} .bar{background:rgba(17,17,17,.18)} .fill{background:#FF4D6D}
"""),
 "blueprint": dict(
  fonts=[("FTHead", 700, "@fontsource/space-mono/files/space-mono-latin-700-normal.woff2"),
         ("FTBody", 400, "@fontsource/space-mono/files/space-mono-latin-400-normal.woff2")],
  ink="#EAF4FF", hl="#FFD84D", capword="#FFD84D",
  css="""
#bgc{background:radial-gradient(circle at 50% 35%,#1563BE,#0B3F86 75%)}
#bpgrid{background:linear-gradient(rgba(255,255,255,.07) 2px,transparent 2px) 0 0/30px 30px,linear-gradient(90deg,rgba(255,255,255,.07) 2px,transparent 2px) 0 0/30px 30px,linear-gradient(rgba(255,255,255,.16) 2px,transparent 2px) 0 0/150px 150px,linear-gradient(90deg,rgba(255,255,255,.16) 2px,transparent 2px) 0 0/150px 150px}
#frame{position:absolute;left:36px;top:36px;right:36px;bottom:36px;border:3px solid rgba(234,244,255,.55)}
#tblock{position:absolute;right:36px;bottom:36px;width:430px;height:150px;border:3px solid rgba(234,244,255,.55);font-family:FTBody;color:rgba(234,244,255,.75);font-size:22px;padding:16px 20px;line-height:1.5}
.sc svg *{stroke:#EAF4FF;stroke-width:4.5;fill:rgba(234,244,255,.06);stroke-linecap:round;stroke-linejoin:round}
.sc svg .d{stroke-dasharray:1 1}
.sc svg .f4,.sc svg .lnA,.sc svg .eyeG,.sc svg .flame{stroke:#FFD84D}
.sc svg .ln,.sc svg .lnA,.sc svg .lnT,.sc svg .lnE,.sc svg .beam{fill:none}
.sc svg .ln{stroke-width:7} .sc svg .lnA{stroke-width:8} .sc svg .beam{stroke:#FFD84D;stroke-dasharray:10 10}
.sc svg .eye{fill:#EAF4FF}
.sc svg .lbl{font-family:FTBody;font-size:26px;fill:#EAF4FF;stroke:none;letter-spacing:3px}
.sc svg .chiptext{font-family:FTHead;font-size:84px;fill:#FFD84D;stroke:none}
.sfxbox{fill:none} .sfxtxt{font-family:FTBody;font-size:28px;fill:#FFD84D;stroke:none;letter-spacing:3px}
.h1{font-family:FTHead;font-weight:700;color:#EAF4FF;text-transform:uppercase;line-height:1.08;font-size:60px;letter-spacing:-1px;border-top:3px solid rgba(234,244,255,.6);border-bottom:3px solid rgba(234,244,255,.6);padding:18px 0}
.h1 .acc{color:#FFD84D}
.tag{font-family:FTBody;font-size:24px;letter-spacing:4px;text-transform:uppercase;color:#FFD84D;border:3px solid #FFD84D;padding:8px 18px}
.num{font-family:FTHead;font-size:28px;color:#0B3F86;background:#EAF4FF;padding:8px 14px}
.src{font-family:FTBody;font-size:22px;color:rgba(234,244,255,.8)}
.capbox{background:rgba(11,63,134,.9);color:#EAF4FF;border:3px solid #EAF4FF;font-family:FTHead !important}
.badge{background:#FFD84D;color:#0B3F86}
.brandtxt{color:#EAF4FF} .bar{background:rgba(234,244,255,.2)} .fill{background:#FFD84D}
"""),
}

# v2 illustration classes for each Reel style
import illus as _illus
STYLES["paper"]["css"] += _illus.css("flat", ["#4FD1E8", "#8F6CF0", "#F3EBDD", "#B5E05A", "#FF8A65"], "#F3EBDD", "#B5E05A")
STYLES["comic"]["css"] += _illus.css("ink", ["#29C5F6", "#FF4D6D", "#FFFFFF", "#FFD93D", "#FF8A3D"], "#111111", "#FF4D6D")
STYLES["blueprint"]["css"] += _illus.css("line", None, "#EAF4FF", "#FFD84D")

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:100%;height:100%;overflow:hidden}
.full{position:absolute;inset:0}
.scene{position:absolute;inset:0}
.inner{position:absolute;inset:0}
.w{display:inline-block}
.sc{position:absolute;left:0;top:300px;width:1080px;height:600px}
#top{position:absolute;left:0;top:0;width:1080px;height:300px}
.bars{position:absolute;left:72px;right:72px;top:188px;display:flex;gap:10px}
.bar{flex:1;height:9px;border-radius:9px;overflow:hidden}
.fill{height:100%;width:100%;transform-origin:0 50%}
.brand{position:absolute;left:66px;top:196px;display:flex;align-items:center;gap:14px;font-family:FTHead;font-size:32px}
.cap{position:absolute;left:0;right:0;top:1240px;display:flex;justify-content:center}
.capbox{max-width:920px;text-align:center;font-family:FTBody;font-weight:800;font-size:50px;line-height:1.15;padding:14px 26px}
.capbox .cw{display:inline-block}
.badge{display:inline-block;font-family:FTHead;font-size:50px;padding:14px 34px}
.toprow{position:absolute;left:66px;right:66px;top:922px;display:flex;gap:16px;align-items:center;z-index:3}
.brand{opacity:.92}
"""

def bot_svg(p, x, y, s, st):
    pins = "".join(f'<line class="lnT d" pathLength="1" x1="{sx*70}" y1="{yy}" x2="{sx*88}" y2="{yy}"/>' for yy in (-72, -44, -16) for sx in (-1, 1))
    return (f'<g transform="translate({x} {y}) scale({s})"><g id="{p}-bot"><g id="{p}-botb" class="pp">'
            f'<line class="ln d" pathLength="1" x1="0" y1="-98" x2="0" y2="-126"/><circle class="f4 d" pathLength="1" cx="0" cy="-134" r="13"/>{pins}'
            f'<rect class="f1 d" pathLength="1" x="-72" y="-102" width="144" height="112" rx="28"/>'
            f'<rect class="f3 d" pathLength="1" x="-52" y="-84" width="104" height="72" rx="18"/>'
            f'<ellipse id="{p}-eL" class="eye" cx="-22" cy="-54" rx="10" ry="13"/><ellipse id="{p}-eR" class="eye" cx="22" cy="-54" rx="10" ry="13"/>'
            f'<path class="lnE d" pathLength="1" d="M -16 -32 Q 0 -20 16 -32"/>'
            f'<rect class="f2 d" pathLength="1" x="-44" y="18" width="88" height="72" rx="18"/><circle class="f4" cx="0" cy="54" r="12"/>'
            f'<line id="{p}-aL" class="ln d" pathLength="1" x1="-44" y1="36" x2="-84" y2="80"/><circle id="{p}-hL" class="f4" cx="-84" cy="80" r="13"/>'
            f'<line id="{p}-aR" class="ln d" pathLength="1" x1="44" y1="36" x2="84" y2="80"/><circle id="{p}-hR" class="f4" cx="84" cy="80" r="13"/>'
            f'</g></g></g>')

def bot_js(p, a, d, pose_t, pose="cheer"):
    js = [f'tl.fromTo("#{p}-bot",{{y:0}},{{y:-10,duration:.45,ease:"sine.inOut",repeat:{max(1, int(d / .45) - 1)},yoyo:true}},{T(a)})']
    for bt in (a + 1.1, a + d * 0.65):
        js.append(f'tl.to(["#{p}-eL","#{p}-eR"],{{scaleY:.1,transformOrigin:"50% 50%",duration:.06}},{T(bt)}); tl.to(["#{p}-eL","#{p}-eR"],{{scaleY:1,duration:.08}},{T(bt+.1)})')
    if pose == "cheer":
        for side, sx in (("L", -1), ("R", 1)):
            js.append(f'tl.to("#{p}-a{side}",{{attr:{{x2:{sx*80},y2:-20}},duration:.25,ease:"back.out(2)"}},{T(pose_t)}); tl.to("#{p}-h{side}",{{attr:{{cx:{sx*80},cy:-20}},duration:.25,ease:"back.out(2)"}},{T(pose_t)})')
    else:  # wave right arm
        js.append(f'tl.to("#{p}-aR",{{attr:{{x2:82,y2:-16}},duration:.22}},{T(pose_t)}); tl.to("#{p}-hR",{{attr:{{cx:82,cy:-16}},duration:.22}},{T(pose_t)})')
        for k in range(4):
            xx, yy = (104, 4) if k % 2 == 0 else (82, -16)
            js.append(f'tl.to("#{p}-aR",{{attr:{{x2:{xx},y2:{yy}}},duration:.18}},{T(pose_t+.25+k*.2)}); tl.to("#{p}-hR",{{attr:{{cx:{xx},cy:{yy}}},duration:.18}},{T(pose_t+.25+k*.2)})')
    return js

def sfx_svg(p, x, y, word, st):
    if st == "comic":
        pts = []
        for k in range(24):
            rr = 150 if k % 2 == 0 else 108; ang = k * np.pi / 12
            pts.append(f"{rr*np.cos(ang)*1.35:.0f},{rr*np.sin(ang)*.62:.0f}")
        box = f'<polygon class="sfxbox" points="{" ".join(pts)}"/>'
    elif st == "paper":
        w = 34 * len(word) + 60
        box = f'<rect class="sfxbox pp" x="{-w/2:.0f}" y="-42" width="{w}" height="84" rx="8" transform="rotate(-4)"/>'
    else:
        box = f'<line class="lnT" x1="-160" y1="30" x2="160" y2="30"/>'
        word = f"FIG. — {word}"
    return f'<g transform="translate({x} {y})"><g id="{p}-sfx">{box}<text class="sfxtxt" x="0" y="16" text-anchor="middle">{E(word)}</text></g></g>'

def ent(st, gids, t, stg=.07):
    """entrance for groups, themed by style"""
    if st == "blueprint":
        sel = ", ".join(f"#{g} .d" for g in gids)
        return [f'tl.fromTo("{sel}",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.8,ease:"power2.inOut",stagger:.025}},{T(t)})',
                f'tl.fromTo({json.dumps(["#" + g for g in gids])},{{opacity:0}},{{opacity:1,duration:.2,stagger:{stg}}},{T(t)})']
    if st == "paper":
        return [f'tl.fromTo({json.dumps(["#" + g for g in gids])},{{opacity:0,y:60,rotation:-6,transformOrigin:"50% 100%"}},{{opacity:1,y:0,rotation:0,duration:.55,ease:"back.out(1.7)",stagger:{stg}}},{T(t)})']
    return [f'tl.fromTo({json.dumps(["#" + g for g in gids])},{{scale:0,rotation:-10,transformOrigin:"50% 50%"}},{{scale:1,rotation:0,duration:.4,ease:"back.out(2.4)",stagger:{stg}}},{T(t)})']

def sfx_js(p, t, st):
    if st == "comic":
        return [f'tl.fromTo("#{p}-sfx",{{scale:0,rotation:-25,transformOrigin:"50% 50%"}},{{scale:1,rotation:-8,duration:.35,ease:"back.out(3)"}},{T(t)})']
    if st == "paper":
        return [f'tl.fromTo("#{p}-sfx",{{opacity:0,y:-80,rotation:10,transformOrigin:"50% 50%"}},{{opacity:1,y:0,rotation:0,duration:.5,ease:"back.out(2)"}},{T(t)})']
    return [f'tl.fromTo("#{p}-sfx",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.4}},{T(t)})']

# ------------------------------------------------------------------ animated story scenes (1080x640)
def sc_rocket(p, a, d, st):
    bars = "".join(f'<rect class="{"f2" if k % 2 else "f1"} d" pathLength="1" x="{150+k*100}" y="{600-h}" width="70" height="{h}" rx="8"/>' for k, h in enumerate((80, 130, 110, 200, 170)))
    stars = "".join(f'<circle id="{p}-tw{k}" class="f4" cx="{x}" cy="{y}" r="7"/>' for k, (x, y) in enumerate(((120, 120), (330, 80), (520, 150), (980, 330), (860, 90), (640, 60))))
    smoke = "".join(f'<circle id="{p}-sm{k}" class="f3" cx="{690+dx}" cy="{300+dy}" r="34" opacity="0"/>' for k, (dx, dy) in enumerate(((0, 0), (-40, 25), (30, 30), (-10, 50))))
    svg = (f'<g id="{p}-bars" class="pp">{bars}</g><g id="{p}-stars">{stars}</g>'
           f'<line class="ln d" pathLength="1" x1="90" y1="600" x2="1000" y2="600"/>'
           f'<polyline id="{p}-chart" class="lnA" pathLength="1" style="stroke-dasharray:1 1" points="150,520 250,470 350,490 450,380 550,410 700,250"/>{smoke}'
           f'<g transform="translate(700 250)"><g id="{p}-rk"><g transform="rotate(35)" class="pp">'
           f'<path id="{p}-fl" class="flame" d="M -18 40 Q 0 120 18 40 Z"/>'
           f'<path class="f3 d" pathLength="1" d="M0,-95 C34,-62 36,10 28,42 L-28,42 C-36,10 -34,-62 0,-95 Z"/>'
           f'<path class="f5 d" pathLength="1" d="M0,-95 C16,-80 26,-62 30,-50 L-30,-50 C-26,-62 -16,-80 0,-95 Z"/>'
           f'<circle class="f1 d" pathLength="1" cx="0" cy="-12" r="15"/>'
           f'<path class="f2 d" pathLength="1" d="M-28,8 L-56,52 L-26,42 Z"/><path class="f2 d" pathLength="1" d="M28,8 L56,52 L26,42 Z"/>'
           f'</g></g></g>' + sfx_svg(p, 300, 120, SFX["rocket"], st) + bot_svg(p, 930, 500, .72, st))
    js = (ent(st, [f"{p}-bars"], a + .15) if st == "blueprint" else
          [f'tl.fromTo("#{p}-bars rect",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:.5,ease:"back.out(1.6)",stagger:.08}},{T(a+.15)})'])
    js += [f'tl.fromTo("#{p}-chart",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.8,ease:"power2.inOut"}},{T(a+.5)})']
    js += ent(st, [f"{p}-rk", f"{p}-botb"], a + 1.0)
    lt = a + min(2.0, d * .4)
    js += [f'tl.fromTo("#{p}-fl",{{scaleY:.6,transformOrigin:"50% 0%"}},{{scaleY:1.35,duration:.08,ease:"none",repeat:{int((a+d-lt)/.08)},yoyo:true}},{T(lt-.3)})',
           f'tl.to("#{p}-rk",{{x:-10,duration:.05,repeat:5,yoyo:true}},{T(lt-.35)})',
           f'tl.to("#{p}-rk",{{x:360,y:-460,duration:1.4,ease:"power2.in"}},{T(lt)})']
    for k in range(4):
        js.append(f'tl.fromTo("#{p}-sm{k}",{{opacity:.95,scale:.3,transformOrigin:"50% 50%"}},{{opacity:0,scale:1.8,duration:1.1,ease:"power2.out"}},{T(lt+k*.08)})')
    for k in range(6):
        js.append(f'tl.fromTo("#{p}-tw{k}",{{opacity:.2}},{{opacity:1,duration:.4,repeat:{int(d/.8)},yoyo:true,ease:"sine.inOut"}},{T(a+k*.13)})')
    js += sfx_js(p, lt + .1, st) + bot_js(p, a, d, lt + .1, "cheer")
    return svg, js

def sc_robot(p, a, d, st):
    svg = (f'<g id="{p}-hum" class="pp"><circle class="f3 d" pathLength="1" cx="280" cy="230" r="42"/>'
           f'<line class="ln d" pathLength="1" x1="280" y1="272" x2="280" y2="420"/><line class="ln d" pathLength="1" x1="280" y1="420" x2="240" y2="540"/>'
           f'<line class="ln d" pathLength="1" x1="280" y1="420" x2="320" y2="540"/><line class="ln d" pathLength="1" x1="280" y1="310" x2="225" y2="395"/>'
           f'<line id="{p}-ha" class="ln d" pathLength="1" x1="280" y1="310" x2="345" y2="390"/></g>'
           f'<g id="{p}-beams"><line class="beam" x1="732" y1="198" x2="300" y2="228"/><line class="beam" x1="792" y1="198" x2="300" y2="236"/></g>'
           f'<g id="{p}-rob" class="pp"><line class="ln d" pathLength="1" x1="762" y1="140" x2="762" y2="108"/><circle class="f4 d" pathLength="1" cx="762" cy="100" r="11"/>'
           f'<rect class="f1 d" pathLength="1" x="692" y="140" width="140" height="112" rx="24"/>'
           f'<circle id="{p}-re1" class="eyeG" cx="732" cy="196" r="16"/><circle id="{p}-re2" class="eyeG" cx="792" cy="196" r="16"/>'
           f'<rect class="f4 d" pathLength="1" x="737" y="226" width="50" height="9" rx="4"/>'
           f'<rect class="f2 d" pathLength="1" x="707" y="264" width="110" height="150" rx="20"/>'
           f'<line class="ln d" pathLength="1" x1="737" y1="414" x2="737" y2="535"/><line class="ln d" pathLength="1" x1="787" y1="414" x2="787" y2="535"/>'
           f'<line class="ln d" pathLength="1" x1="707" y1="292" x2="662" y2="382"/><line id="{p}-ra" class="ln d" pathLength="1" x1="817" y1="292" x2="862" y2="382"/>'
           f'<rect class="lnT d" pathLength="1" x="640" y="572" width="244" height="28" rx="14"/></g>'
           f'<rect id="{p}-pg" class="f4" x="644" y="576" width="0" height="20" rx="10"/>'
           + sfx_svg(p, 540, 80, SFX["robot"], st) + bot_svg(p, 110, 560, .55, st))
    js = ent(st, [f"{p}-hum", f"{p}-rob", f"{p}-botb"], a + .15, .15)
    js += [f'tl.fromTo("#{p}-beams",{{opacity:0}},{{opacity:1,duration:.3}},{T(a+.9)})',
           f'tl.fromTo("#{p}-beams line",{{strokeDashoffset:0}},{{strokeDashoffset:-260,duration:{T(d-1)},ease:"none"}},{T(a+.9)})',
           f'tl.fromTo("#{p}-pg",{{attr:{{width:0}}}},{{attr:{{width:236}},duration:{T(d-1.4)},ease:"power1.inOut"}},{T(a+1)})']
    for k in range(int((d - 1.2) / .32)):
        hx, hy = (360, 236) if k % 2 == 0 else (392, 280)
        js.append(f'tl.to("#{p}-ha",{{attr:{{x2:{hx},y2:{hy}}},duration:.24,ease:"sine.inOut"}},{T(a+.9+k*.32)})')
        rx, ry = (872, 206) if k % 2 == 0 else (904, 250)
        js.append(f'tl.to("#{p}-ra",{{attr:{{x2:{rx},y2:{ry}}},duration:.24,ease:"sine.inOut"}},{T(a+1.5+k*.32)})')
    js.append(f'tl.fromTo(["#{p}-re1","#{p}-re2"],{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.35,duration:.3,repeat:{int(d/.6)},yoyo:true}},{T(a+.9)})')
    js += sfx_js(p, a + .6, st) + bot_js(p, a, d, a + 1.2, "wave")
    return svg, js

def sc_shield(p, a, d, st):
    cards = ""
    for k, (cx, cy) in enumerate(((640, 110), (690, 180), (740, 250))):
        cards += (f'<g id="{p}-cd{k}" class="pp"><rect class="f3 d" pathLength="1" x="{cx}" y="{cy}" width="280" height="200" rx="18"/>'
                  f'<rect class="{"f1" if k != 1 else "f2"} d" pathLength="1" x="{cx}" y="{cy}" width="280" height="44" rx="18"/>'
                  + "".join(f'<line class="lnT d" pathLength="1" x1="{cx+30}" y1="{cy+80+j*34}" x2="{cx+(240 if j != 2 else 160)}" y2="{cy+80+j*34}"/>' for j in range(3)) + '</g>')
    rings = "".join(f'<circle id="{p}-rp{k}" class="lnT" cx="470" cy="330" r="120" opacity="0"/>' for k in range(2))
    svg = (cards + rings +
           f'<g id="{p}-arm"><g class="pp"><rect class="f2 d" pathLength="1" x="-80" y="312" width="350" height="38" rx="19"/><circle class="f1 d" pathLength="1" cx="270" cy="331" r="28"/>'
           f'<path class="f5 d" pathLength="1" d="M290,312 L352,286 L364,306 L312,326 Z"/><path class="f5 d" pathLength="1" d="M290,350 L352,376 L364,356 L312,336 Z"/></g></g>'
           f'<g transform="translate(470 330)"><g id="{p}-sh" class="pp"><path class="f1 d" pathLength="1" d="M0,-150 Q82,-134 136,-120 L136,12 Q124,100 0,165 Q-124,100 -136,12 L-136,-120 Q-82,-134 0,-150 Z"/>'
           f'<path class="lnA" pathLength="1" id="{p}-ck" style="stroke-dasharray:1 1" d="M -56 6 L -14 48 L 64 -40"/></g></g>'
           + sfx_svg(p, 820, 560, SFX["shield"], st) + bot_svg(p, 120, 560, .55, st))
    js = ent(st, [f"{p}-cd0", f"{p}-cd1", f"{p}-cd2", f"{p}-botb"], a + .1, .12)
    hit = a + min(1.7, d * .35)
    js += [f'tl.fromTo("#{p}-arm",{{x:-420}},{{x:-20,duration:.9,ease:"power2.in"}},{T(hit-.9)})',
           f'tl.to("#{p}-arm",{{x:-300,duration:.6,ease:"back.out(1.4)"}},{T(hit+.05)})']
    js += ent(st, [f"{p}-sh"], hit - .55)
    js += [f'tl.fromTo("#{p}-ck",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.4}},{T(hit+.1)})',
           f'tl.to("#{p}-sh",{{x:10,duration:.05,repeat:5,yoyo:true}},{T(hit)})']
    for k in range(2):
        js.append(f'tl.fromTo("#{p}-rp{k}",{{opacity:1,scale:.8,transformOrigin:"50% 50%"}},{{opacity:0,scale:1.9,duration:.8,ease:"power2.out"}},{T(hit+k*.15)})')
    js += sfx_js(p, hit + .3, st) + bot_js(p, a, d, hit + .3, "cheer")
    return svg, js

def sc_phone(p, a, d, st):
    notes = "".join(f'<g id="{p}-n{k}"><rect class="{("f4", "f2", "f1")[k]} d" pathLength="1" x="-78" y="{-150+k*96}" width="156" height="76" rx="14"/>'
                    f'<line class="lnE d" pathLength="1" x1="-56" y1="{-122+k*96}" x2="40" y2="{-122+k*96}"/><line class="lnE d" pathLength="1" x1="-56" y1="{-100+k*96}" x2="10" y2="{-100+k*96}"/></g>' for k in range(3))
    sp = "".join(f'<path id="{p}-sp{k}" class="f4" d="M{x},{y-22} L{x+6},{y-6} L{x+22},{y} L{x+6},{y+6} L{x},{y+22} L{x-6},{y+6} L{x-22},{y} L{x-6},{y-6} Z"/>' for k, (x, y) in enumerate(((330, 160), (760, 120), (790, 430), (300, 470))))
    svg = (sp + f'<g transform="translate(540 330)"><g id="{p}-ph" class="pp"><rect class="f1 d" pathLength="1" x="-112" y="-235" width="224" height="450" rx="36"/>'
           f'<rect class="f3 d" pathLength="1" x="-94" y="-205" width="188" height="390" rx="22"/><rect class="eye" x="-30" y="-226" width="60" height="12" rx="6"/>{notes}</g></g>'
           + sfx_svg(p, 540, 590, SFX["phone"], st) + bot_svg(p, 900, 540, .62, st))
    js = ent(st, [f"{p}-ph", f"{p}-botb"], a + .1, .2)
    js.append(f'tl.fromTo("#{p}-ph",{{rotation:-8,transformOrigin:"50% 50%"}},{{rotation:4,duration:{T(d)},ease:"sine.inOut"}},{T(a)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-n{k}",{{opacity:0,y:-40,scale:.6,transformOrigin:"50% 50%"}},{{opacity:1,y:0,scale:1,duration:.35,ease:"back.out(2.4)"}},{T(a+.9+k*.45)})')
    for k in range(4):
        js.append(f'tl.fromTo("#{p}-sp{k}",{{scale:0,rotation:0,transformOrigin:"50% 50%"}},{{scale:1.2,rotation:90,duration:.5,repeat:{int(d/1.0)},yoyo:true}},{T(a+.5+k*.2)})')
    js += sfx_js(p, a + 1.2, st) + bot_js(p, a, d, a + 1.0, "wave")
    return svg, js

def sc_bolt(p, a, d, st):
    ticks = "".join(f'<line class="lnT" x1="{540+200*np.cos(np.pi*(1-k/8)):.0f}" y1="{520-200*np.sin(np.pi*(1-k/8)):.0f}" x2="{540+170*np.cos(np.pi*(1-k/8)):.0f}" y2="{520-170*np.sin(np.pi*(1-k/8)):.0f}"/>' for k in range(9))
    rays = "".join(f'<line id="{p}-ry{k}" class="lnA" x1="{540+130*np.cos(k*np.pi/4):.0f}" y1="{230+130*np.sin(k*np.pi/4):.0f}" x2="{540+190*np.cos(k*np.pi/4):.0f}" y2="{230+190*np.sin(k*np.pi/4):.0f}"/>' for k in range(8))
    svg = (f'<g id="{p}-gauge" class="pp"><path class="ln d" pathLength="1" d="M 340 520 A 200 200 0 0 1 740 520"/>{ticks}</g>'
           f'<line id="{p}-nd" class="lnA" x1="540" y1="520" x2="380" y2="520"/><circle class="f2" cx="540" cy="520" r="18"/>{rays}'
           f'<g transform="translate(540 230)"><g id="{p}-bt" class="pp"><path class="f4 d" pathLength="1" d="M 22,-120 L -66,8 L -8,8 L -34,120 L 66,-14 L 8,-14 Z"/></g></g>'
           + sfx_svg(p, 540, 600, SFX["bolt"], st) + bot_svg(p, 900, 540, .62, st))
    js = ent(st, [f"{p}-gauge", f"{p}-bt", f"{p}-botb"], a + .1, .15)
    pts = [(np.pi * (1 - f)) for f in (0, .3, .55, .8, .95)]
    for k, ang in enumerate(pts):
        js.append(f'tl.to("#{p}-nd",{{attr:{{x2:{540+160*np.cos(ang):.0f},y2:{520-160*np.sin(ang):.0f}}},duration:.45,ease:"power2.out"}},{T(a+.8+k*.4)})')
    js.append(f'tl.fromTo("#{p}-bt",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.12,duration:.25,repeat:{int(d/.5)},yoyo:true}},{T(a+.8)})')
    for k in range(8):
        js.append(f'tl.fromTo("#{p}-ry{k}",{{opacity:0}},{{opacity:1,duration:.15,repeat:{int(d/.6)},yoyo:true,repeatDelay:.15}},{T(a+.9+k*.05)})')
    js += sfx_js(p, a + 1.4, st) + bot_js(p, a, d, a + 1.4, "cheer")
    return svg, js

def sc_chip(p, a, d, st):
    pins = "".join(f'<line class="lnT d" pathLength="1" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>' for k in range(5)
                   for (x1, y1, x2, y2) in ((460+k*40, 170, 460+k*40, 140), (460+k*40, 410, 460+k*40, 440), (420, 210+k*40, 390, 210+k*40), (660, 210+k*40, 690, 210+k*40)))
    tr = [((690, 250), (800, 250), (840, 150), (960, 150)), ((690, 330), (860, 330), (900, 420), (980, 420)), ((390, 290), (260, 290), (220, 180), (120, 180)),
          ((390, 370), (240, 370), (200, 470), (100, 470)), ((540, 440), (540, 520), (650, 580)), ((500, 140), (500, 70), (380, 40))]
    traces = "".join(f'<polyline class="lnA" pathLength="1" style="stroke-dasharray:1 1" id="{p}-tr{k}" points="{" ".join(f"{x},{y}" for x, y in t)}"/><circle id="{p}-te{k}" class="f4" cx="{t[-1][0]}" cy="{t[-1][1]}" r="12"/>' for k, t in enumerate(tr))
    svg = (traces + f'<g id="{p}-ch" class="pp">{pins}<rect class="f1 d" pathLength="1" x="420" y="170" width="240" height="240" rx="28"/>'
           f'<rect class="f2 d" pathLength="1" x="460" y="210" width="160" height="160" rx="18"/><text class="chiptext" x="540" y="322" text-anchor="middle">AI</text></g>'
           + sfx_svg(p, 540, 600, SFX["chip"], st) + bot_svg(p, 920, 560, .55, st))
    js = ent(st, [f"{p}-ch", f"{p}-botb"], a + .1, .2)
    for k in range(len(tr)):
        js.append(f'tl.fromTo("#{p}-tr{k}",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.6,ease:"power2.out"}},{T(a+.7+k*.12)})')
        js.append(f'tl.fromTo("#{p}-te{k}",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1.3,duration:.3,ease:"back.out(3)",repeat:{int(d/.9)},yoyo:true,repeatDelay:.3}},{T(a+1.2+k*.12)})')
    js.append(f'tl.fromTo("#{p}-ch",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:6,duration:.3,repeat:{int(d/.6)},yoyo:true,ease:"sine.inOut"}},{T(a+.9)})')
    js += sfx_js(p, a + 1.3, st) + bot_js(p, a, d, a + 1.3, "wave")
    return svg, js

def sc_globe(p, a, d, st):
    mer = "".join(f'<ellipse id="{p}-m{k}" class="lnT" cx="540" cy="320" rx="{60+k*60}" ry="190"/>' for k in range(2))
    lat = "".join(f'<line class="lnT d" pathLength="1" x1="{540-np.sqrt(190**2-y**2):.0f}" y1="{320+y}" x2="{540+np.sqrt(190**2-y**2):.0f}" y2="{320+y}"/>' for y in (-110, -40, 40, 110))
    pins = "".join(f'<g id="{p}-pn{k}"><path class="f5 d" pathLength="1" d="M{x},{y} C{x-26},{y-30} {x-20},{y-62} {x},{y-62} C{x+20},{y-62} {x+26},{y-30} {x},{y} Z"/><circle class="f3" cx="{x}" cy="{y-40}" r="8"/></g>' for k, (x, y) in enumerate(((470, 260), (600, 330), (520, 420), (640, 220))))
    orb = [(540 + 280 * np.cos(t), 320 + 80 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 13)]
    svg = (f'<ellipse class="lnA" cx="540" cy="320" rx="280" ry="80"/>'
           f'<g id="{p}-gl" class="pp"><circle class="f1 d" pathLength="1" cx="540" cy="320" r="190"/>{mer}{lat}</g>{pins}'
           f'<circle id="{p}-sat" class="f4" cx="820" cy="320" r="16"/>'
           + sfx_svg(p, 540, 590, SFX["globe"], st) + bot_svg(p, 930, 560, .55, st))
    js = ent(st, [f"{p}-gl", f"{p}-botb"], a + .1, .2)
    for k in range(2):
        js.append(f'tl.fromTo("#{p}-m{k}",{{attr:{{rx:{60+k*60}}}}},{{attr:{{rx:{190-k*40}}},duration:1.2,repeat:{int(d/1.2)},yoyo:true,ease:"sine.inOut"}},{T(a+.4)})')
    for k in range(4):
        js.append(f'tl.fromTo("#{p}-pn{k}",{{scale:0,y:-40,transformOrigin:"50% 100%"}},{{scale:1,y:0,duration:.4,ease:"bounce.out"}},{T(a+.9+k*.25)})')
    for k in range(1, len(orb)):
        js.append(f'tl.to("#{p}-sat",{{attr:{{cx:{orb[k][0]:.0f},cy:{orb[k][1]:.0f}}},duration:{T((d-.5)/12)},ease:"none"}},{T(a+.3+(k-1)*(d-.5)/12)})')
    js += sfx_js(p, a + 1.5, st) + bot_js(p, a, d, a + 1.5, "cheer")
    return svg, js

SCENES = {"rocket": sc_rocket, "robot": sc_robot, "shield": sc_shield, "phone": sc_phone, "bolt": sc_bolt, "chip": sc_chip, "globe": sc_globe}

def words_html(text, pid):
    out, i = [], 0
    for tok in re.findall(r"\*[^*]+\*|\S+", text):
        acc = tok.startswith("*")
        ws = tok.strip("*").split()
        if acc:
            inner = " ".join(f'<span id="{pid}-{i+j}" class="w">{E(w)}</span>' for j, w in enumerate(ws)); i += len(ws)
            out.append(f'<span class="acc">{inner}</span>')
        else:
            for w in ws:
                out.append(f'<span id="{pid}-{i}" class="w">{E(w)}</span>'); i += 1
    return " ".join(out), i

def words_js(pid, n, t, st, gap=.08):
    if st == "comic":
        return [f'tl.fromTo("#{pid}-{k}",{{scale:2.2,opacity:0,rotation:-8}},{{scale:1,opacity:1,rotation:0,duration:.18,ease:"back.out(2)"}},{T(t+k*gap)})' for k in range(n)]
    if st == "paper":
        return [f'tl.fromTo("#{pid}-{k}",{{y:50,opacity:0,rotation:6}},{{y:0,opacity:1,rotation:0,duration:.35,ease:"back.out(2)"}},{T(t+k*gap)})' for k in range(n)]
    return [f'tl.fromTo("#{pid}-{k}",{{opacity:0,x:-14}},{{opacity:1,x:0,duration:.12,ease:"none"}},{T(t+k*gap)})' for k in range(n)]

def story_scene(i, ns, s, a, d, st):
    import illus
    p = f"s{i}"; shape = illus.pick(s)
    svg, js = illus.SCENES[shape](p, a, d, st)
    svg += bot_svg(p, 985, 548, .5, st)
    js += ent(st, [f"{p}-botb"], a + .9) + bot_js(p, a, d, a + 1.6, "cheer" if i % 2 else "wave")
    hw, nw = words_html(s["headline"], f"{p}-h")
    panel = '<div class="panel"></div>' if st == "comic" else ""
    m = (f'<div class="inner" id="{p}-in">{panel}'
         f'<div class="toprow" id="{p}-top"><span class="num">{ {"comic": f"#{i}", "paper": f"{i} of {ns}", "blueprint": f"FIG. {i:02d}"}[st] }</span><span class="tag">{E(s["category"])}</span>'
         f'<span class="src" style="margin-left:auto">Source: {E(s["source"])}</span></div>'
         f'<div class="sc"><svg width="1080" height="600" viewBox="0 0 1080 640">{svg}</svg></div>'
         f'<div style="position:absolute;left:66px;right:66px;top:990px"><div class="h1" id="{p}-hb">{hw}</div></div></div>')
    js = [f'tl.fromTo("#{p}-top",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{T(a+.05)})'] + js
    if st == "comic":
        js.append(f'tl.fromTo("#{p}-in .panel",{{scale:.85,rotation:-3,transformOrigin:"50% 50%"}},{{scale:1,rotation:0,duration:.35,ease:"back.out(2)"}},{T(a)})')
        js.append(f'tl.fromTo("#{p}-hb",{{scale:.7,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{T(a+.25)})')
    js += words_js(f"{p}-h", nw, a + .35, st)
    js += exit_js(f"{p}-in", a + d, st)
    return m, js

def exit_js(sel, end, st):
    if st == "paper":
        return [f'tl.fromTo("#{sel}",{{y:0,rotation:0}},{{y:260,rotation:5,opacity:0,duration:.26,ease:"power3.in",transformOrigin:"50% 100%"}},{T(end-.28)})']
    if st == "comic":
        return [f'tl.fromTo("#{sel}",{{x:0}},{{x:-1150,rotation:-6,duration:.26,ease:"power3.in"}},{T(end-.28)})']
    return [f'tl.fromTo("#{sel}",{{opacity:1,y:0}},{{opacity:0,y:-40,duration:.24,ease:"power2.in"}},{T(end-.26)})']

def hook_scene(h, a, d, st):
    hw, nw = words_html(h["headline"], "hk")
    kick = {"comic": "BREAKING!", "paper": "Today in AI", "blueprint": "SPEC // TODAY IN AI"}[st]
    size = {"comic": 128, "paper": 106, "blueprint": 80}[st]
    m = (f'<div class="inner" id="hk-in">'
         f'<div style="position:absolute;left:0;right:0;top:330px;text-align:center"><span class="tag" id="hk-k" style="font-size:{48 if st=="comic" else 32}px">{kick}</span></div>'
         f'<div style="position:absolute;left:66px;right:66px;top:440px;text-align:center"><div class="h1" id="hk-hb" style="font-size:{size}px">{hw}</div></div>'
         f'<div id="hk-more" style="position:absolute;left:0;right:0;top:960px;text-align:center"><span class="badge">{E(h.get("more","+2 more AI & tech updates"))}</span></div>'
         f'<div class="sc" style="top:1060px;height:300px"><svg width="1080" height="300" viewBox="0 0 1080 300">{bot_svg("hk", 540, 170, .9, st)}</svg></div></div>')
    js = [f'tl.fromTo("#hk-k",{{scale:1.4,rotation:-12}},{{scale:1,rotation:-3,duration:.35,ease:"back.out(3)"}},{T(a)})']
    # frame 0 is the cover: headline fully visible from the first frame, then a punch-in
    js.append(f'tl.fromTo("#hk-hb",{{scale:1.12}},{{scale:1,duration:.45,ease:"back.out(2.5)"}},{T(a)})')
    js += ent(st, ["hk-botb"], a + .5) + bot_js("hk", a, d, a + .9, "wave")
    js.append(f'tl.fromTo("#hk-more",{{opacity:0,scale:.5}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2.5)"}},{T(a+min(1.5, d*.5))})')
    js += exit_js("hk-in", a + d, st)
    return m, js

def outro_scene(q, a, d, st):
    qw, nq = words_html(q, "oq")
    m = (f'<div class="inner" id="oq-in">'
         f'<div class="sc" style="top:300px;height:330px"><svg width="1080" height="330" viewBox="0 0 1080 330">{bot_svg("oq", 540, 190, 1.0, st)}</svg></div>'
         f'<div style="position:absolute;left:66px;right:66px;top:640px;text-align:center"><div class="h1" style="font-size:{ {"comic":96,"paper":96,"blueprint":72}[st] }px">{qw}</div></div>'
         f'<div id="oq-c" style="position:absolute;left:0;right:0;top:990px;text-align:center"><span class="badge">Comment below</span></div>'
         f'<div id="oq-f" class="brand brandtxt" style="position:absolute;left:0;right:0;top:1120px;justify-content:center;font-size:52px">Follow @freshtechupdates</div></div>')
    js = ent(st, ["oq-botb"], a + .05) + bot_js("oq", a, d, a + .5, "wave") + words_js("oq", nq, a + .25, st, .08)
    js += [f'tl.fromTo("#oq-c",{{opacity:0,scale:.5}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2.5)"}},{T(a+.9)})',
           f'tl.fromTo("#oq-f",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4}},{T(a+1.1)})']
    return m, js


def cta_scene(a, d):
    """Brand end card (same on every style): points viewers to the full YouTube episode."""
    play = ('<svg width="150" height="106" viewBox="0 0 150 106"><rect width="150" height="106" rx="30" fill="#FF0033"/>'
            '<path d="M60,30 L102,53 L60,76 Z" fill="#fff"/></svg>')
    m = ('<div class="full" style="background:radial-gradient(circle at 50% 38%,#16224d,#05070F 72%)"></div>'
         '<div class="full" style="background:radial-gradient(circle,rgba(243,235,221,.18) 1.5px,transparent 2.5px) 0 0/60px 60px"></div>'
         f'<div id="ct-logo" style="position:absolute;left:0;right:0;top:330px;display:flex;justify-content:center">{chip_logo(330)}</div>'
         '<div id="ct-k" style="position:absolute;left:0;right:0;top:760px;text-align:center;font-family:FTCta;font-weight:700;font-size:44px;letter-spacing:10px;color:#A3E635">WANT ALL OF TODAY\'S UPDATES?</div>'
         '<div id="ct-h" style="position:absolute;left:60px;right:60px;top:840px;text-align:center;font-family:FTCta;font-weight:700;font-size:118px;line-height:1.02;color:#F8FAFC">Watch the <span style="color:#22D3EE">full episode</span></div>'
         f'<div id="ct-yt" style="position:absolute;left:0;right:0;top:1130px;display:flex;justify-content:center;align-items:center;gap:26px">{play}'
         '<span style="font-family:FTCta;font-weight:700;font-size:58px;color:#F3EBDD">on YouTube</span></div>'
         '<div id="ct-f" style="position:absolute;left:0;right:0;top:1330px;text-align:center;font-family:FTCta;font-weight:700;font-size:56px;color:#F8FAFC">'
         '<span style="color:#22D3EE">@</span>freshtechupdates</div>'
         '<div id="ct-s" style="position:absolute;left:0;right:0;top:1430px;text-align:center;font-family:FTCta;font-weight:700;font-size:38px;color:#94A3B8">Subscribe for daily AI &amp; tech updates</div>')
    js = [f'tl.to("#top",{{opacity:0,duration:.2}},{T(a)})', f'tl.fromTo("#ct-logo",{{scale:0,rotation:-25,opacity:0}},{{scale:1,rotation:0,opacity:1,duration:.55,ease:"back.out(1.8)"}},{T(a+.05)})',
          f'tl.fromTo("#ct-k",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.35}},{T(a+.35)})',
          f'tl.fromTo("#ct-h",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:.4,ease:"expo.out"}},{T(a+.55)})',
          f'tl.fromTo("#ct-yt",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.4,ease:"back.out(2)"}},{T(a+.85)})',
          f'tl.to("#ct-yt svg",{{scale:1.1,duration:.35,yoyo:true,repeat:{max(1, int((d-1.3)/.35))},ease:"sine.inOut",transformOrigin:"50% 50%"}},{T(a+1.3)})',
          f'tl.fromTo("#ct-f",{{opacity:0}},{{opacity:1,duration:.3}},{T(a+1.1)})',
          f'tl.fromTo("#ct-s",{{opacity:0}},{{opacity:1,duration:.3}},{T(a+1.3)})',
          f'tl.to("#ct-logo",{{y:-14,duration:.6,yoyo:true,repeat:{max(1, int((d-.6)/.6))},ease:"sine.inOut"}},{T(a+.6)})']
    return m, js

# ------------------------------------------------------------------ audio
def narrate(k, text):
    sents = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]
    parts, words, t = [], [], 0.0
    for s in sents:
        a, _ = k.create(s.replace("freshtechupdates", "fresh tech updates"), voice=VOICE, speed=SPEED, lang="en-us")
        a = a.astype(np.float32); d = len(a) / SR
        ws = s.split(); wt = [len(w) + 2 + (3 if re.search(r"[,.!?;:]$", w) else 0) for w in ws]
        tot = sum(wt); span = max(0.1, d - 0.16); c = t + 0.07
        for w, x in zip(ws, wt):
            dd = span * x / tot; words.append((w, c, c + dd)); c += dd
        parts += [a, np.zeros(int(0.08 * SR), np.float32)]; t += d + 0.08
    return np.concatenate(parts), words

def whoosh(dur=0.42, seed=1):
    rng = np.random.default_rng(seed); n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32); env = np.sin(np.linspace(0, np.pi, n)) ** 2
    y = np.zeros(n, np.float32); acc = 0.0
    for i in range(n):
        c = 0.02 + 0.25 * (i / n); acc += c * (x[i] - acc); y[i] = acc
    y = y - np.convolve(y, np.ones(40) / 40, "same")
    return 0.55 * env * y / (np.abs(y).max() + 1e-6)

def pop(dur=0.18):
    t = np.arange(int(dur * SR)) / SR; f = 900 * np.exp(-t * 25) + 300
    return (0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)).astype(np.float32)

import itertools
from ftlogo import logo_svg
_LID = itertools.count()
def chip_logo(size):
    return logo_svg(round(size * 1.45), uid=f"lg{next(_LID)}")

def background(st):
    if st == "paper":
        hills = ('<svg class="full" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;inset:0">'
                 '<defs><filter id="ps" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="9" stdDeviation="0" flood-color="#000" flood-opacity=".3"/></filter></defs>'
                 '<g id="hl1" filter="url(#ps)"><path d="M0,1400 C180,1330 330,1420 520,1370 C700,1320 860,1400 1080,1350 L1080,1920 L0,1920 Z" fill="#8F6CF0"/></g>'
                 '<g id="hl2" filter="url(#ps)"><path d="M0,1520 C200,1460 380,1560 560,1500 C760,1440 900,1530 1080,1480 L1080,1920 L0,1920 Z" fill="#4FD1E8"/></g>'
                 '<g id="hl3" filter="url(#ps)"><path d="M0,1660 C220,1600 420,1700 640,1630 C820,1580 960,1660 1080,1620 L1080,1920 L0,1920 Z" fill="#B5E05A"/></g>'
                 + "".join(f'<g filter="url(#ps)"><circle id="cl{k}" cx="{x}" cy="{y}" r="{r}" fill="#F3EBDD" opacity=".9"/></g>' for k, (x, y, r) in enumerate(()))
                 + '</svg>'
                 '<svg id="noise" class="full" width="1080" height="1920" style="position:absolute;inset:0"><filter id="nz"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#nz)"/></svg>')
        return '<div id="bgc" class="full"></div>' + hills, ['tl.fromTo("#hl1",{x:0},{x:-30,duration:TOTAL,ease:"none"},0)', 'tl.fromTo("#hl3",{x:0},{x:30,duration:TOTAL,ease:"none"},0)']
    if st == "comic":
        return ('<div id="bgc" class="full"></div><div id="rays" style="position:absolute;left:-900px;top:-500px;width:2880px;height:2880px"></div><div id="dots" class="full"></div>',
                ['tl.fromTo("#rays",{rotation:0},{rotation:25,duration:TOTAL,ease:"none"},0)'])
    return ('<div id="bgc" class="full"></div><div id="bpgrid" class="full"></div><div id="frame"></div>'
            '<div id="tblock">PROJECT: FRESHTECHUPDATES<br>DWG: DAILY AI &amp; TECH BRIEF<br>SCALE: 1:1 · REV A</div>', [])

def build(data, proj, st):
    from kokoro_onnx import Kokoro
    S = STYLES[st]
    k = Kokoro(str(BASE / "kokoro-v1.0.onnx"), str(BASE / "voices-v1.0.bin"))
    proj = pathlib.Path(proj); (proj / "assets/fonts").mkdir(parents=True, exist_ok=True); (proj / "assets/lib").mkdir(parents=True, exist_ok=True)
    shutil.copy(NM / "gsap/dist/gsap.min.js", proj / "assets/lib/gsap.min.js")
    shutil.copy(NM / "@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2", proj / "assets/fonts/ftcta.woff2")
    ff = "@font-face{font-family:FTCta;font-weight:700;src:url('assets/fonts/ftcta.woff2')}\n"
    for fam, wt, src in S["fonts"]:
        dst = f"{fam}-{wt}.woff2"; shutil.copy(NM / src, proj / "assets/fonts" / dst)
        ff += f"@font-face{{font-family:{fam};font-weight:{wt};src:url('assets/fonts/{dst}')}}\n"
    if st == "paper":  # paper also needs the shadow filter on scene svgs
        pass
    stories = data["stories"][:3]; ns = len(stories)
    plan = [("hook", data["hook"], data["hook"]["voice"])] + [("story", s, s["voice"]) for s in stories]
    plan.append(("outro", None, data.get("outro_voice", "Which one surprised you most? Tell me in the comments.")))
    plan.append(("cta", None, data.get("cta_voice", "Want all of today's updates? Watch the full episode on YouTube, at freshtechupdates.")))
    audio, t, scenes = [], 0.0, []
    for kind, s, v in plan:
        aud, ws = narrate(k, v)
        lead = 0.3; extra = 0.9 if kind == "story" else (1.4 if kind == "cta" else 0.35)
        dur = round((lead + len(aud) / SR + extra) * FPS) / FPS
        seg = np.zeros(int(round(dur * SR)), np.float32); seg[int(lead * SR):int(lead * SR) + len(aud)] = aud
        audio.append(seg); scenes.append(dict(kind=kind, s=s, start=round(t, 4), dur=dur, words=[(w, t + lead + b, t + lead + e) for w, b, e in ws])); t += dur
    total = round(t * FPS) / FPS
    vo = np.concatenate(audio)
    for j, sc in enumerate(scenes[1:], 1):
        p = int((sc["start"] - 0.2) * SR); w = whoosh(seed=j); vo[p:p + len(w)] += 0.5 * w[:len(vo) - p]
        q = int((sc["start"] + 0.15) * SR); pp = pop(); vo[q:q + len(pp)] += pp[:len(vo) - q]
    vo = (vo / max(1.0, np.abs(vo).max() / 0.95)).astype(np.float32)
    sf.write(str(proj / "assets/vo.wav"), vo, SR)

    bg, bgjs = background(st)
    body, js, caps = [], [j.replace("TOTAL", str(total)) for j in bgjs], []
    defs = ('<svg width="0" height="0" style="position:absolute"><defs><filter id="ps" x="-20%" y="-20%" width="140%" height="160%">'
            '<feDropShadow dx="0" dy="9" stdDeviation="0" flood-color="#000" flood-opacity=".3"/></filter></defs></svg>') if st != "paper" else ""
    for i, sc in enumerate(scenes):
        a, d = sc["start"], sc["dur"]
        if sc["kind"] == "hook": m, j = hook_scene(sc["s"], a, d, st)
        elif sc["kind"] == "outro": m, j = outro_scene(data.get("outro_question", "Which update *surprised* you most?"), a, d, st)
        elif sc["kind"] == "cta": m, j = cta_scene(a, d)
        else: m, j = story_scene(i, ns, sc["s"], a, d, st)
        body.append(f'<div id="scn{i}" class="clip scene" data-start="{a}" data-duration="{d}" data-track-index="2" style="z-index:5">{m}</div>')
        js += j
        if sc["kind"] != "story": continue
        ws = sc["words"]; g, groups = [], []
        for w in ws:
            g.append(w)
            if len(g) >= 3 or re.search(r"[.,!?;:]$", w[0]): groups.append(g); g = []
        if g: groups.append(g)
        for gi, gr in enumerate(groups):
            cs = gr[0][1]; ce = groups[gi + 1][0][1] if gi + 1 < len(groups) else min(gr[-1][2] + 0.35, a + d - 0.3)
            cid = f"c{i}_{gi}"
            spans = " ".join(f'<span id="{cid}-{wi}" class="cw">{E(w[0])}</span>' for wi, w in enumerate(gr))
            caps.append(f'<div id="{cid}" class="clip cap" data-start="{cs:.3f}" data-duration="{max(0.2, ce - cs):.3f}" data-track-index="3" style="z-index:8"><div class="capbox">{spans}</div></div>')
            for wi, w in enumerate(gr):
                js.append(f'tl.fromTo("#{cid}-{wi}",{{opacity:.3,scale:.9}},{{opacity:1,scale:1,color:"{S["capword"]}",duration:.1}},{w[1]:.3f})')
                js.append(f'tl.to("#{cid}-{wi}",{{color:"{S["ink"] if st != "paper" else "#1E2452"}",duration:.12}},{w[2]:.3f})')
    bars = "".join(f'<div class="bar"><div id="fill{i}" class="fill"></div></div>' for i in range(len(scenes)))
    top = (f'<div id="top" class="clip" data-start="0" data-duration="{total}" data-track-index="4" style="z-index:9">'
           f'<div class="brand brandtxt">{chip_logo(52)}<span>@freshtechupdates</span></div></div>')
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="assets/lib/gsap.min.js"></script>
<style>{ff}{BASE_CSS}{S["css"]}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
{defs}{bg}
{''.join(body)}
{''.join(caps)}
{top}
<audio id="vo" class="clip" src="assets/vo.wav" data-start="0" data-duration="{total}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body></html>"""
    (proj / "index.html").write_text(doc)
    print(f"built {proj} · {st} · {total:.1f}s · scenes:", [pick_shape(sc['s']) if sc['kind'] == 'story' else sc['kind'] for sc in scenes])

if __name__ == "__main__":
    build(json.loads(pathlib.Path(sys.argv[1]).read_text()), sys.argv[2], sys.argv[3])

