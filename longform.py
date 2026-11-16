#!/usr/bin/env python3
"""freshtechupdates daily YouTube episode (16:9, 1920x1080 @30fps) -> HyperFrames project.

Usage: python3 longform.py episode.json <project_dir> [show 1-7]   (default show = IST weekday, Mon=1)

One continuous camera world: every story is a "station"; the camera travels between them
(whip / zoom / pan / hop / arc / slide / rotate depending on the show), drifts while you listen,
pushes into the illustration, then the key points, with FT Bot reacting in a second voice.

episode.json:
{
 "title": "YouTube title (max 70 chars)",
 "summary": "1-2 sentence description for YouTube",
 "thumb_text": "max 5 words, *accent*",
 "hook_voice": "1-2 sentences teasing today's biggest updates",
 "stories": [   # 5-8 stories, most important first
   {"category": "AI tools", "headline": "max 9 words, one *accent*", "scene": "<scene>",
    "voice": "3-5 short sentences, 45-80 words, plain spoken English",
    "points": ["max 7 words", "max 7 words", "max 7 words"],     # 2-3 key takeaways
    "stat": {"value": "$2B+", "label": "stolen in crypto in 2025"}, # optional, only a real number from the source
    "bot": "optional one-line FT Bot reaction or safety tip",
    "source": "Publication name"}
 ],
 "question": "Which update *surprised* you most?",
 "outro_voice": "spoken outro (ask the question + subscribe)",
 "tags": ["tag", ...]
}
scenes: rocket robot shield phone bolt chip globe chat cloud car money
"""
import json, sys, re, html, math, pathlib, shutil, datetime
import numpy as np, soundfile as sf
import styreel as SR_
from styreel import SCENES as BASE_SCENES, bot_svg, bot_js, ent, sfx_svg, sfx_js, pick_shape
from ftlogo import logo_svg, logo_inner

BASE = pathlib.Path(__file__).resolve().parent
NM = BASE / "node_modules"
FPS, SR = 30, 24000
E = html.escape
def T(x): return f"{x:.3f}"
HOST = ("af_heart", 1.08)
BOT = ("am_puck", 1.15)

# ============================================================ extra scenes (same class vocabulary as styreel)
def sc_chat(p, a, d, st):
    bub = [(160, 130, 430, "f1"), (470, 250, 430, "f2"), (160, 370, 360, "f1")]
    b = "".join(f'<g id="{p}-b{k}" class="pp"><rect class="{c} d" pathLength="1" x="{x}" y="{y}" width="{w}" height="96" rx="40"/>'
                f'<line class="lnE d" pathLength="1" x1="{x+40}" y1="{y+38}" x2="{x+w-80}" y2="{y+38}"/>'
                f'<line class="lnE d" pathLength="1" x1="{x+40}" y1="{y+62}" x2="{x+w-160}" y2="{y+62}"/></g>' for k, (x, y, w, c) in enumerate(bub))
    dots = "".join(f'<circle id="{p}-td{k}" class="f4" cx="{520+k*44}" cy="526" r="13"/>' for k in range(3))
    svg = (f'<g id="{p}-win" class="pp"><rect class="f3 d" pathLength="1" x="110" y="70" width="840" height="520" rx="36"/>'
           f'<rect class="f2 d" pathLength="1" x="470" y="490" width="200" height="72" rx="36" opacity=".35"/></g>{b}{dots}'
           + sfx_svg(p, 760, 110, "AI CHAT", st) + bot_svg(p, 940, 520, .6, st))
    js = ent(st, [f"{p}-win", f"{p}-botb"], a + .1, .15)
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-b{k}",{{opacity:0,scale:.4,transformOrigin:"{"0% 100%" if k != 1 else "100% 100%"}"}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2.2)"}},{T(a+.6+k*.7)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-td{k}",{{y:0}},{{y:-16,duration:.25,repeat:{max(1,int(d/.5))},yoyo:true,ease:"sine.inOut"}},{T(a+.4+k*.1)})')
    js += sfx_js(p, a + 1.2, st) + bot_js(p, a, d, a + 1.0, "wave")
    return svg, js

def sc_cloud(p, a, d, st):
    racks = "".join(f'<g id="{p}-rk{k}" class="pp"><rect class="{("f1","f2","f1")[k]} d" pathLength="1" x="{250+k*200}" y="360" width="150" height="220" rx="16"/>'
                    + "".join(f'<rect class="f3 d" pathLength="1" x="{268+k*200}" y="{382+j*62}" width="114" height="40" rx="8"/>'
                              f'<circle id="{p}-led{k}{j}" class="f4" cx="{360+k*200}" cy="{402+j*62}" r="8"/>' for j in range(3)) + '</g>' for k in range(3))
    cloud = (f'<g id="{p}-cl" class="pp"><path class="f3 d" pathLength="1" d="M330,250 C250,250 240,150 320,140 C330,70 450,50 490,110 '
             f'C530,40 680,50 690,140 C780,130 800,250 710,250 Z"/></g>')
    wires = "".join(f'<line id="{p}-w{k}" class="beam" x1="{325+k*200}" y1="255" x2="{325+k*200}" y2="360"/>' for k in range(3))
    pk = "".join(f'<circle id="{p}-pk{k}" class="f4" cx="{325+k*200}" cy="350" r="11"/>' for k in range(3))
    svg = cloud + wires + racks + pk + sfx_svg(p, 860, 140, "THE CLOUD", st) + bot_svg(p, 920, 540, .58, st)
    js = ent(st, [f"{p}-cl", f"{p}-rk0", f"{p}-rk1", f"{p}-rk2", f"{p}-botb"], a + .1, .12)
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-pk{k}",{{attr:{{cy:350}}}},{{attr:{{cy:262}},duration:.7,repeat:{max(1,int(d/.7))},ease:"none"}},{T(a+.8+k*.2)})')
        js.append(f'tl.fromTo("#{p}-w{k}",{{strokeDashoffset:0}},{{strokeDashoffset:-120,duration:{T(d)},ease:"none"}},{T(a)})')
        for j in range(3):
            js.append(f'tl.fromTo("#{p}-led{k}{j}",{{opacity:1}},{{opacity:.2,duration:.18,repeat:{max(1,int(d/.5))},yoyo:true,repeatDelay:{.1+((k*3+j)%4)*.08:.2f}}},{T(a+.6+(k+j)*.07)})')
    js += sfx_js(p, a + 1.0, st) + bot_js(p, a, d, a + 1.2, "cheer")
    return svg, js

def sc_car(p, a, d, st):
    city = "".join(f'<rect class="{("f2","f1","f5","f2","f1")[k%5]} d" pathLength="1" x="{90+k*120}" y="{420-h}" width="96" height="{h}" rx="6"/>' for k, h in enumerate((150, 230, 120, 260, 180, 140, 210, 170)))
    dash = "".join(f'<rect class="f3" x="{k*140}" y="548" width="80" height="10" rx="5"/>' for k in range(9))
    waves = "".join(f'<path id="{p}-sw{k}" class="lnA" d="M{700+k*44},{380-k*30} Q{740+k*54},{440} {700+k*44},{500+k*30}" opacity="0"/>' for k in range(3))
    car = (f'<g id="{p}-car" class="pp"><path class="f1 d" pathLength="1" d="M260,470 L300,400 Q330,360 400,360 L560,360 Q620,360 650,410 L700,430 Q730,440 730,470 L730,500 L260,500 Z"/>'
           f'<path class="f3 d" pathLength="1" d="M330,410 L360,380 L470,380 L470,420 L330,420 Z"/><path class="f3 d" pathLength="1" d="M490,380 L560,380 Q590,382 610,420 L490,420 Z"/>'
           + "".join(f'<g transform="translate({x} 505)"><g id="{p}-wh{k}"><circle class="f2 d" pathLength="1" r="42"/><circle class="f3" r="14"/>'
                     f'<line class="lnT" x1="-30" y1="0" x2="30" y2="0"/><line class="lnT" x1="0" y1="-30" x2="0" y2="30"/></g></g>' for k, x in enumerate((360, 640))) + '</g>')
    svg = (f'<g id="{p}-city" class="pp">{city}</g><line class="ln d" pathLength="1" x1="40" y1="520" x2="1040" y2="520"/>'
           f'<g id="{p}-dash">{dash}</g>{waves}{car}' + sfx_svg(p, 300, 110, "SELF-DRIVING", st) + bot_svg(p, 940, 300, .55, st))
    js = ent(st, [f"{p}-city", f"{p}-car", f"{p}-botb"], a + .1, .15)
    js += [f'tl.fromTo("#{p}-dash",{{x:0}},{{x:-140,duration:.35,repeat:{max(1,int(d/.35))},ease:"none"}},{T(a)})',
           f'tl.fromTo("#{p}-car",{{y:0}},{{y:-5,duration:.18,repeat:{max(1,int(d/.18))},yoyo:true,ease:"sine.inOut"}},{T(a+.6)})']
    for k in range(2):
        js.append(f'tl.fromTo("#{p}-wh{k}",{{rotation:0}},{{rotation:{int(360*d/0.5)},duration:{T(d)},ease:"none",transformOrigin:"50% 50%"}},{T(a)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-sw{k}",{{opacity:0}},{{opacity:1,duration:.25,repeat:{max(1,int(d/.9))},yoyo:true,repeatDelay:.4}},{T(a+1.0+k*.15)})')
    js += sfx_js(p, a + 1.3, st) + bot_js(p, a, d, a + 1.3, "wave")
    return svg, js

def sc_money(p, a, d, st):
    coins = "".join(f'<g id="{p}-c{k}"><ellipse class="f4 d" pathLength="1" cx="{260+(k%3)*12}" cy="{540-k*34}" rx="90" ry="26"/></g>' for k in range(6))
    bills = "".join(f'<g id="{p}-bl{k}" class="pp"><rect class="f5 d" pathLength="1" x="-70" y="-38" width="140" height="76" rx="10"/>'
                    f'<circle class="f3" r="20"/></g>' for k in range(3))
    svg = (f'<line class="ln d" pathLength="1" x1="440" y1="560" x2="1000" y2="560"/><line class="ln d" pathLength="1" x1="440" y1="560" x2="440" y2="120"/>'
           f'<polyline id="{p}-ln" class="lnA" pathLength="1" style="stroke-dasharray:1 1" points="470,500 560,460 640,480 720,360 800,390 900,200"/>'
           f'<path id="{p}-ar" class="f4 d" pathLength="1" d="M900,170 L940,240 L860,240 Z"/>{coins}'
           + f'<g id="{p}-bills">{bills}</g>'
           + sfx_svg(p, 640, 90, "BIG MONEY", st) + bot_svg(p, 980, 520, .5, st))
    js = ent(st, [f"{p}-c{k}" for k in range(6)], a + .1, .08)
    js += [f'tl.fromTo("#{p}-ln",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.0,ease:"power2.inOut"}},{T(a+.6)})',
           f'tl.fromTo("#{p}-ar",{{scale:0,transformOrigin:"50% 100%"}},{{scale:1,duration:.4,ease:"back.out(3)"}},{T(a+1.5)})']
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-bl{k}",{{x:{200+k*40},y:-80,rotation:-30,opacity:1}},{{x:{560+k*140},y:{560-k*40},rotation:{40+k*50},duration:1.6,ease:"power1.in",repeat:{max(0,int(d/2.2)-1)},repeatDelay:.6}},{T(a+.9+k*.35)})')
    js += sfx_js(p, a + 1.4, st)
    return svg, js

SCENES = dict(BASE_SCENES, chat=sc_chat, cloud=sc_cloud, car=sc_car, money=sc_money)
SCENE_WORDS = [("chat", "chatbot|chatgpt|gemini|assistant|copilot|claude|llm|reply|conversation"),
               ("car", "car|tesla|waymo|ev\\b|vehicle|driv|robotaxi"),
               ("cloud", "cloud|server|aws|azure|data cent|storage"),
               ("money", "fund|ipo|valuation|revenue|stock|invest|billion|price|deal|acqui")]
def scene_for(s):
    if s.get("scene") in SCENES: return s["scene"]
    txt = (s.get("category", "") + " " + s.get("headline", "")).lower()
    for k, pat in SCENE_WORDS:
        if re.search(pat, txt): return k
    return pick_shape({"category": s.get("category", ""), "headline": s.get("headline", "")})

# ============================================================ the 7 shows
F_SG = ("@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2", 700)
F_IN = ("@fontsource/inter/files/inter-latin-800-normal.woff2", 800)
F_IN6 = ("@fontsource/inter/files/inter-latin-600-normal.woff2", 600)
F_BG = ("@fontsource/bangers/files/bangers-latin-400-normal.woff2", 400)
F_SM = ("@fontsource/space-mono/files/space-mono-latin-700-normal.woff2", 700)
F_SM4 = ("@fontsource/space-mono/files/space-mono-latin-400-normal.woff2", 400)

SHOWS = {
 1: dict(key="newsroom", name="THE NEWSROOM", family="flat", head=F_SG, body=F_IN, layout="line", trans="whip", mirror=True,
         bg="radial-gradient(circle at 75% 15%,#1d2a63,transparent 55%),radial-gradient(circle at 10% 90%,#3b0d2a,transparent 50%),#0B1020",
         pat="linear-gradient(rgba(255,255,255,.045) 2px,transparent 2px) 0 0/120px 120px,linear-gradient(90deg,rgba(255,255,255,.045) 2px,transparent 2px) 0 0/120px 120px",
         ink="#F4F6FB", sub="#AEB6D3", acc="#FF3B5C", acc2="#22D3EE", hl="#FFD166", fills=["#22D3EE", "#FF3B5C", "#F4F6FB", "#FFD166", "#7C83FD"],
         line="#F4F6FB", card="background:rgba(17,24,52,.78);border:2px solid rgba(255,255,255,.08);border-radius:36px;box-shadow:0 40px 90px rgba(0,0,0,.45)",
         cardx='<div class="bar" style="position:absolute;left:40px;top:120px;bottom:120px;width:12px;border-radius:6px;background:#FF3B5C"></div>',
         label=lambda i, n: f"STORY {i}", music=dict(bpm=118, timbre="pluck", kick=[1,0,0,0,1,0,0,0], snare=[0,0,1,0,0,0,1,0]), ticker=True),
 2: dict(key="countdown", name="THE COUNTDOWN", family="flat", head=F_SG, body=F_IN, layout="drop", trans="zoom", mirror=False, reverse=True,
         bg="radial-gradient(circle at 50% 0%,#5b1aa8,transparent 60%),radial-gradient(circle at 100% 100%,#a3125f,transparent 50%),#14072B",
         pat="radial-gradient(circle,rgba(255,255,255,.18) 1.5px,transparent 2.5px) 0 0/70px 70px",
         ink="#FFFFFF", sub="#D7C6F5", acc="#FF2E93", acc2="#B6FF3B", hl="#B6FF3B", fills=["#B6FF3B", "#FF2E93", "#FFFFFF", "#FFD23F", "#7B5CFF"],
         line="#FFFFFF", card="background:linear-gradient(160deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:2px solid rgba(255,255,255,.14);border-radius:48px",
         cardx="", label=lambda i, n: f"#{n - i + 1}", music=dict(bpm=124, timbre="saw", kick=[1,0,1,0,1,0,1,0], snare=[0,0,1,0,0,0,1,1]), bignum=True),
 3: dict(key="blueprint", name="BLUEPRINT LAB", family="line", head=F_SM, body=F_SM4, layout="snake", trans="pan", mirror=True, upper=True,
         bg="radial-gradient(circle at 50% 35%,#1563BE,#0B3F86 75%)",
         pat="linear-gradient(rgba(255,255,255,.07) 2px,transparent 2px) 0 0/40px 40px,linear-gradient(90deg,rgba(255,255,255,.07) 2px,transparent 2px) 0 0/40px 40px,linear-gradient(rgba(255,255,255,.16) 2px,transparent 2px) 0 0/200px 200px,linear-gradient(90deg,rgba(255,255,255,.16) 2px,transparent 2px) 0 0/200px 200px",
         ink="#EAF4FF", sub="#B9D3F5", acc="#FFD84D", acc2="#EAF4FF", hl="#FFD84D", fills=None, line="#EAF4FF",
         card="border:3px solid rgba(234,244,255,.6)", cardx='<div class="tick" style="position:absolute;right:60px;bottom:60px;width:330px;height:110px;border:3px solid rgba(234,244,255,.6);font-family:FTBody;font-size:20px;color:rgba(234,244,255,.8);padding:14px 18px;line-height:1.6">PROJECT: FRESHTECHUPDATES<br>DWG: DAILY AI &amp; TECH</div>',
         label=lambda i, n: f"FIG. {i:02d}", music=dict(bpm=100, timbre="sine", kick=[1,0,0,1,0,0,1,0], snare=[0,0,0,0,1,0,0,0])),
 4: dict(key="arcade", name="UPDATE ARCADE", family="ink", head=F_BG, body=F_IN, layout="zigzag", trans="hop", mirror=True,
         bg="radial-gradient(circle at 50% 40%,#7AF2E0,#2FC7B3 80%)",
         pat="radial-gradient(circle,rgba(17,17,17,.14) 26%,transparent 29%) 0 0/36px 36px",
         ink="#111111", sub="#1d3b38", acc="#FF4D6D", acc2="#FFD93D", hl="#FF4D6D", fills=["#29C5F6", "#FF4D6D", "#FFFFFF", "#FFD93D", "#FF8A3D"],
         line="#111111", card="background:#fff;border:9px solid #111;box-shadow:22px 22px 0 #111", cardx="",
         label=lambda i, n: f"LEVEL {i}", music=dict(bpm=132, timbre="square", kick=[1,0,0,0,1,0,0,0], snare=[0,0,1,0,0,0,1,0])),
 5: dict(key="worldmap", name="WORLD TOUR", family="flat", head=F_SG, body=F_IN, layout="circle", trans="arc", mirror=False,
         bg="radial-gradient(circle at 30% 20%,#0f5157,transparent 55%),radial-gradient(circle at 80% 90%,#3a2a0a,transparent 50%),#062226",
         pat="radial-gradient(circle,rgba(46,196,182,.35) 2px,transparent 3px) 0 0/48px 48px",
         ink="#F7F3E8", sub="#A9CFCB", acc="#FF9F1C", acc2="#2EC4B6", hl="#FF9F1C", fills=["#2EC4B6", "#FF9F1C", "#F7F3E8", "#FFE66D", "#E36414"],
         line="#F7F3E8", card="background:rgba(6,40,44,.85);border-top:10px solid #FF9F1C;border-radius:28px;box-shadow:0 40px 80px rgba(0,0,0,.5)",
         cardx="", label=lambda i, n: f"STOP {i}", music=dict(bpm=108, timbre="pluck", kick=[1,0,0,1,0,0,1,0], snare=[0,0,1,0,0,0,1,0])),
 6: dict(key="classroom", name="THE CLASSROOM", family="line", head=F_SG, body=F_IN6, layout="board", trans="slide", mirror=True, chalk=True,
         bg="radial-gradient(circle at 50% 40%,#2d5a43,#173226 80%)",
         pat="radial-gradient(circle,rgba(255,255,255,.06) 1px,transparent 2px) 0 0/22px 22px",
         ink="#F1EDE0", sub="#C9D8CC", acc="#FFE066", acc2="#9AD1FF", hl="#FFE066", fills=None, line="#F1EDE0",
         card="background:rgba(255,255,255,.035);border:20px solid #7a4e2a;border-radius:10px;box-shadow:inset 0 0 80px rgba(0,0,0,.35),0 30px 60px rgba(0,0,0,.4)",
         cardx="", label=lambda i, n: f"LESSON {i}", music=dict(bpm=96, timbre="sine", kick=[1,0,0,0,0,0,1,0], snare=[0,0,0,0,1,0,0,0])),
 7: dict(key="paper", name="PAPER STUDIO", family="flat", head=F_SG, body=F_IN, layout="scatter", trans="rotate", mirror=True, light=True,
         bg="radial-gradient(circle at 50% 30%,#FBF6EC,#EADFC9 85%)",
         pat="radial-gradient(circle,rgba(30,36,82,.08) 1.5px,transparent 2.5px) 0 0/34px 34px",
         ink="#1E2452", sub="#5A5F80", acc="#FF6B4A", acc2="#3A86FF", hl="#FFD23F", fills=["#3A86FF", "#FF6B4A", "#FFFFFF", "#FFD23F", "#8AC926"],
         line="#1E2452", card="background:#FFFFFF;border-radius:14px;box-shadow:0 26px 0 rgba(30,36,82,.10),0 40px 70px rgba(30,36,82,.18)",
         cardx='<div style="position:absolute;left:50%;top:18px;width:260px;height:56px;margin-left:-130px;background:rgba(255,210,63,.75);transform:rotate(-3deg)"></div>',
         label=lambda i, n: f"PAGE {i}", music=dict(bpm=104, timbre="sine", kick=[1,0,0,0,1,0,0,1], snare=[0,0,1,0,0,0,1,0])),
}
FAM_ST = {"flat": "paper", "ink": "comic", "line": "blueprint"}

def scene_css(S):
    fam = S["family"]
    if fam == "line":
        L, A = S["line"], S["acc"]
        return f"""
.sc svg *{{stroke:{L};stroke-width:4.5;fill:rgba(255,255,255,.05);stroke-linecap:round;stroke-linejoin:round}}
.sc svg .d{{stroke-dasharray:1 1}}
.sc svg .f4,.sc svg .lnA,.sc svg .eyeG,.sc svg .flame{{stroke:{A}}}
.sc svg .ln,.sc svg .lnA,.sc svg .lnT,.sc svg .lnE,.sc svg .beam{{fill:none}}
.sc svg .ln{{stroke-width:7}} .sc svg .lnA{{stroke-width:8}} .sc svg .beam{{stroke:{A};stroke-dasharray:10 10}}
.sc svg .eye{{fill:{L}}}
.sc svg .lbl{{font-family:FTBody;font-size:26px;fill:{L};stroke:none;letter-spacing:3px}}
.sc svg .chiptext{{font-family:FTHead;font-size:84px;fill:{A};stroke:none}}
.sfxbox{{fill:none}} .sfxtxt{{font-family:FTBody;font-size:28px;fill:{A};stroke:none;letter-spacing:3px}}"""
    f = S["fills"]
    if fam == "ink":
        return f"""
.sc svg *{{stroke:#111;stroke-width:7;stroke-linejoin:round;stroke-linecap:round}}
.sc svg .f1{{fill:{f[0]}}} .sc svg .f2{{fill:{f[1]}}} .sc svg .f3{{fill:{f[2]}}} .sc svg .f4{{fill:{f[3]}}} .sc svg .f5{{fill:{f[4]}}}
.sc svg .eye{{fill:#111}} .sc svg .eyeG{{fill:{f[0]}}}
.sc svg .ln{{stroke-width:11;fill:none}} .sc svg .lnA{{stroke:{f[1]};stroke-width:12;fill:none}}
.sc svg .lnT{{stroke-width:5;fill:none}} .sc svg .lnE{{stroke-width:6;fill:none}}
.sc svg .beam{{stroke:{f[1]};stroke-width:6;fill:none;stroke-dasharray:14 12}} .sc svg .flame{{fill:{f[4]}}}
.sc svg .chiptext{{font-family:FTHead;font-size:110px;fill:#111;stroke:none}}
.sfxbox{{fill:{f[3]}}} .sfxtxt{{font-family:FTHead;font-size:58px;fill:{f[1]};stroke:#111;stroke-width:3px;paint-order:stroke;letter-spacing:2px}}"""
    L = S["line"]; dark = S.get("light")
    return f"""
.sc svg .f1{{fill:{f[0]}}} .sc svg .f2{{fill:{f[1]}}} .sc svg .f3{{fill:{f[2]}}} .sc svg .f4{{fill:{f[3]}}} .sc svg .f5{{fill:{f[4]}}}
.sc svg .eye{{fill:#1E2452}} .sc svg .eyeG{{fill:{f[3]}}}
.sc svg .ln{{stroke:{L};stroke-width:12;fill:none;stroke-linecap:round}}
.sc svg .lnA{{stroke:{f[3]};stroke-width:12;fill:none;stroke-linecap:round;stroke-linejoin:round}}
.sc svg .lnT{{stroke:{"#1E2452" if dark else L};stroke-width:5;fill:none;stroke-linecap:round}}
.sc svg .lnE{{stroke:#1E2452;stroke-width:6;fill:none;stroke-linecap:round}}
.sc svg .beam{{stroke:{f[3]};stroke-width:5;fill:none;stroke-dasharray:14 12}} .sc svg .flame{{fill:{f[4]}}}
.sc svg .pp{{filter:url(#ps)}}
.sc svg .chiptext{{font-family:FTHead;font-weight:700;font-size:96px;fill:#1E2452}}
.sfxbox{{fill:{f[2] if not dark else "#1E2452"}}} .sfxtxt{{font-family:FTHead;font-weight:700;font-size:44px;fill:{"#1E2452" if not dark else "#FFFFFF"};letter-spacing:2px}}"""

def show_css(S):
    ink, sub, acc, acc2, hl = S["ink"], S["sub"], S["acc"], S["acc2"], S["hl"]
    fam = S["family"]; up = "text-transform:uppercase;" if S.get("upper") else ""
    if fam == "ink":
        h1 = f"font-family:FTHead;font-weight:400;letter-spacing:1px;line-height:1.0;color:#111"
        accs = f".h1 .acc{{color:{acc}}}"
        tag = f"font-family:FTHead;font-size:40px;letter-spacing:2px;color:#fff;background:{acc};border:5px solid #111;padding:4px 22px;box-shadow:6px 6px 0 #111"
        num = f"font-family:FTHead;font-size:46px;color:#111;background:{acc2};border:5px solid #111;padding:2px 18px;box-shadow:6px 6px 0 #111;transform:rotate(-4deg)"
        cap = "background:#fff;color:#111;border:5px solid #111;box-shadow:8px 8px 0 #111"
    elif fam == "line":
        h1 = f"font-family:FTHead;font-weight:700;{up}line-height:1.1;color:{ink};letter-spacing:-1px"
        accs = f".h1 .acc{{color:{acc}}}" + (f" .h1 .acc .w{{border-bottom:6px solid {acc}}}" if S.get("chalk") else "")
        tag = f"font-family:FTBody;font-size:26px;letter-spacing:4px;text-transform:uppercase;color:{acc};border:3px solid {acc};padding:8px 18px"
        num = f"font-family:FTHead;font-size:28px;color:#0B3F86;background:{ink};padding:8px 14px" if not S.get("chalk") else f"font-family:FTHead;font-size:30px;color:#173226;background:{acc};padding:8px 16px;border-radius:4px"
        cap = f"background:rgba(0,0,0,.55);color:{ink};border:2px solid {ink}"
    else:
        light = S.get("light")
        h1 = f"font-family:FTHead;font-weight:700;line-height:1.05;color:{ink};letter-spacing:-2px"
        accs = (f".h1 .acc .w{{background:{hl};color:#1E2452;padding:0 10px;border-radius:8px}}" if light else
                f".h1 .acc{{color:{acc2}}}")
        tag = f"font-family:FTHead;font-weight:700;font-size:28px;letter-spacing:3px;text-transform:uppercase;color:{'#fff' if light else '#0B1020'};background:{acc};padding:10px 22px;border-radius:999px"
        num = f"font-family:FTHead;font-weight:700;font-size:30px;color:{ink};border:3px solid {ink if light else 'rgba(255,255,255,.5)'};padding:7px 18px;border-radius:999px"
        cap = "background:#1E2452;color:#FFFFFF" if light else "background:rgba(5,7,15,.75);color:#F8FAFC"
    return f"""
.h1{{{h1}}} {accs}
.tag{{{tag}}} .num{{{num}}}
.src{{font-family:FTBody;font-weight:600;font-size:26px;color:{sub}}}
.pt{{color:{ink}}} .pt .pi{{background:{acc}}} .pt .pi svg{{stroke:{'#111' if fam == 'ink' else ('#fff' if S.get('light') else '#0B1020')}}}
.stat .sv{{color:{acc if fam != 'line' else acc}}} .stat .sl{{color:{sub}}}
.capbox{{{cap}}}
.kick{{color:{acc}}} .ttl{{color:{ink}}} .date{{color:{sub}}} .tz .tn{{color:{acc}}} .tz{{color:{ink}}}
.hud{{color:{ink}}} .hud .hp{{background:{acc};color:{'#fff' if S.get('light') or fam=='ink' else '#0B1020'}}}
.bignum{{color:{acc2}}}
"""

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#000}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;font-family:FTBody,sans-serif}
#bg{position:absolute;inset:0}
.par{position:absolute;left:-3000px;top:-3000px;width:20000px;height:20000px}
#cam{position:absolute;inset:0;overflow:hidden}
#world{position:absolute;left:0;top:0;width:10px;height:10px;transform-origin:0 0}
.stn{position:absolute;width:1920px;height:1080px;transform-origin:50% 50%}
.stcard{position:absolute;inset:40px}
.row{position:absolute;top:150px;display:flex;gap:18px;align-items:center}
.hl{position:absolute;top:235px;width:860px}
.w{display:inline-block}
.pts{position:absolute;width:860px}
.pt{display:flex;align-items:center;gap:22px;font-family:FTBody;font-weight:800;font-size:40px;line-height:1.15;margin-bottom:30px}
.pt .pi{flex:0 0 58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.ill{position:absolute}
.ill svg{width:100%;height:100%;overflow:hidden}
.stat{position:absolute;text-align:center}
.stat .sv{font-family:FTHead;font-weight:700;font-size:124px;line-height:1}
.stat .sl{font-family:FTBody;font-weight:800;font-size:32px;margin-top:8px}
.srcline{position:absolute;top:970px}
.bignum{position:absolute;font-family:FTHead;font-weight:700;font-size:900px;line-height:1;opacity:.10}
.cap{position:absolute;left:0;right:0;display:flex;justify-content:center;z-index:15}
.capbox{max-width:1500px;text-align:center;font-family:FTBody;font-weight:800;font-size:44px;line-height:1.2;padding:12px 28px;border-radius:16px}
.capbox .cw{display:inline-block}
.hud{position:absolute;z-index:16;font-family:FTHead;font-weight:700}
#brand{left:40px;top:30px;display:flex;align-items:center;gap:12px;font-size:28px}
#showchip{right:40px;top:34px;display:flex;align-items:center;gap:12px;font-size:24px;letter-spacing:3px}
.hud .hp{padding:6px 14px;border-radius:8px;letter-spacing:2px}
#ticker{position:absolute;left:0;right:0;bottom:0;height:54px;background:#FF3B5C;z-index:16;overflow:hidden;display:flex;align-items:center}
#ticker .tl{flex:0 0 auto;background:#0B1020;color:#fff;font-family:FTHead;font-weight:700;font-size:24px;letter-spacing:3px;padding:0 24px;height:54px;display:flex;align-items:center;z-index:2}
#ticker .tt{white-space:nowrap;font-family:FTBody;font-weight:800;font-size:26px;color:#fff;padding-left:30px}
#bothud{position:absolute;right:40px;bottom:120px;z-index:17;display:flex;align-items:flex-end;gap:16px}
#bubble{max-width:640px;background:#F8FAFC;color:#0A0F1F;font-family:FTBody;font-weight:800;font-size:36px;line-height:1.2;padding:22px 28px;border-radius:28px 28px 6px 28px;box-shadow:0 20px 40px rgba(0,0,0,.35)}
#bubble .bt{display:block;font-family:FTHead;font-weight:700;font-size:20px;letter-spacing:3px;color:#0FA3C2;margin-bottom:6px}
#logo{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:20}
#endcard{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;z-index:21;background:radial-gradient(circle at 50% 45%,#101a3a,#05070F 70%)}
#endcard .et{font-family:FTSpace;font-weight:700;font-size:46px;letter-spacing:5px;color:#F3EBDD}
#endcard .eh{font-family:FTSpace;font-weight:700;font-size:34px;color:#22D3EE}
.intro .kick{position:absolute;left:0;right:0;top:150px;text-align:center;font-family:FTHead;font-weight:700;font-size:34px;letter-spacing:8px}
.intro .ttl{position:absolute;left:160px;right:160px;top:200px;text-align:center;font-family:FTHead;font-weight:700;font-size:96px;line-height:1.02}
.intro .date{position:absolute;left:0;right:0;top:330px;text-align:center;font-family:FTBody;font-weight:800;font-size:32px}
.intro .tz{position:absolute;left:300px;right:300px;font-family:FTBody;font-weight:800;font-size:38px;display:flex;gap:24px;align-items:center}
.intro .tz .tn{font-family:FTHead;font-weight:700;font-size:40px;min-width:60px}
"""

# ============================================================ layouts (station top-left X, Y, rotation)
def layout(kind, n):
    out = []
    for i in range(n):
        if kind == "line": out.append((i * 2500, 0, 0))
        elif kind == "drop": out.append(((i % 2) * 700 - 350, i * 1600, 0))
        elif kind == "snake":
            r, c = divmod(i, 3); c = c if r % 2 == 0 else 2 - c; out.append((c * 2300, r * 1500, 0))
        elif kind == "zigzag": out.append((i * 2200, -i * 500 - (i % 2) * 650, 0))
        elif kind == "circle":
            R = max(2600, n * 560); a = -math.pi / 2 + i * 2 * math.pi / n
            out.append((R * math.cos(a) - 960, R * math.sin(a) - 540, 0))
        elif kind == "board": out.append((i * 2060, 0, 0))
        else:  # scatter
            jit = [(0, 0, -3), (2300, 520, 4), (4500, -360, -5), (6800, 300, 3), (9000, -480, -4), (11200, 420, 5), (13400, -200, -3), (15600, 380, 4), (17800, -300, -5), (20000, 200, 3)]
            out.append(jit[i % len(jit)] if i < len(jit) else (i * 2250, 0, 0))
    return out

def wpt(stn, lx, ly):
    X, Y, r = stn; rad = math.radians(r); dx, dy = lx - 960, ly - 540
    return X + 960 + dx * math.cos(rad) - dy * math.sin(rad), Y + 540 + dx * math.sin(rad) + dy * math.cos(rad)

# ============================================================ audio
TTS_CACHE = BASE / ".ttscache"
def tts(k, s, v, sp):
    import hashlib
    TTS_CACHE.mkdir(exist_ok=True); f = TTS_CACHE / (hashlib.md5(f"{v}|{sp}|{s}".encode()).hexdigest() + ".npy")
    if f.exists(): return np.load(f)
    a, _ = k.create(s, voice=v, speed=sp, lang="en-us"); a = a.astype(np.float32); np.save(f, a); return a

def narrate(k, text, voice):
    v, sp = voice
    sents = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]
    parts, words, t = [], [], 0.0
    for s in sents:
        a = tts(k, s.replace("freshtechupdates", "fresh tech updates"), v, sp); d = len(a) / SR
        ws = s.split(); wt = [len(w) + 2 + (3 if re.search(r"[,.!?;:]$", w) else 0) for w in ws]
        tot = sum(wt); span = max(.1, d - .16); c = t + .07
        for w, x in zip(ws, wt):
            dd = span * x / tot; words.append((w, c, c + dd)); c += dd
        parts += [a, np.zeros(int(.12 * SR), np.float32)]; t += d + .12
    return np.concatenate(parts), words

def tone(f, d, amp=.3, decay=6.0, timbre="sine"):
    t = np.arange(int(d * SR)) / SR; ph = 2 * np.pi * f * t
    if timbre == "square": w = np.sign(np.sin(ph)) * .5 + .2 * np.sin(ph)
    elif timbre == "saw": w = 2 * ((f * t) % 1) - 1
    elif timbre == "pluck": w = np.sin(ph) + .5 * np.sin(2 * ph) + .25 * np.sin(3 * ph)
    else: w = np.sin(ph)
    return (amp * w * np.exp(-t * decay)).astype(np.float32)

PROGS = [[(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7)],   # Am F C G
         [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)],   # C G Am F
         [(293.7, 349.2, 440.0), (233.1, 293.7, 349.2), (261.6, 329.6, 392.0), (220.0, 277.2, 329.6)],   # Dm Bb C A
         [(164.8, 196.0, 246.9), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (146.8, 185.0, 220.0)],   # Em C G D
         [(196.0, 246.9, 293.7), (164.8, 196.0, 246.9), (130.8, 164.8, 196.0), (146.8, 185.0, 220.0)]]   # G Em C D

def bgm(total, cfg, seed):
    n = int(total * SR); out = np.zeros(n + SR * 4, np.float32); step = 60 / cfg["bpm"] / 2
    prog = PROGS[seed % len(PROGS)]; rng = np.random.default_rng(seed)
    def add(sig, at):
        i = int(at * SR); e = min(len(out), i + len(sig)); out[i:e] += sig[:e - i]
    s = 0
    while s * step < total:
        t0 = s * step; bar = s // 8; chord = prog[bar % 4]; k8 = s % 8
        if cfg["kick"][k8]:
            tt = np.arange(int(.25 * SR)) / SR; add((.5 * np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)).astype(np.float32), t0)
        if cfg["snare"][k8]:
            nz = rng.standard_normal(int(.18 * SR)).astype(np.float32); add(.12 * nz * np.exp(-np.arange(len(nz)) / SR * 22), t0)
        if k8 % 2 == 1:
            hh = rng.standard_normal(int(.04 * SR)).astype(np.float32); hh = np.diff(hh, prepend=0) * np.exp(-np.arange(len(hh)) / SR * 80); add(.05 * hh, t0)
        if k8 == 0:
            d = step * 8; tt = np.arange(int(d * SR)) / SR; env = np.minimum(1, tt / .5) * np.minimum(1, (d - tt) / .7)
            add((sum(np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt) for f in chord) * env * .03).astype(np.float32), t0)
        if k8 in (0, 3, 6): add(tone(chord[0] / 2, step * 1.6, .2, 4, "sine"), t0)
        if k8 in (2, 5, 7) and (bar % 2 == 1 or cfg["timbre"] != "sine"):
            add(tone(chord[(k8 + bar) % 3] * 2, step * 1.2, .045 if cfg["timbre"] != "square" else .03, 8, cfg["timbre"]), t0)
        s += 1
    tail = np.linspace(1, 0, int(2.5 * SR)); out[n - len(tail):n] *= tail
    return out[:n]

def whoosh(d=.5, seed=1):
    rng = np.random.default_rng(seed); n = int(d * SR); x = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2; y = np.zeros(n, np.float32); a = 0.0
    for i in range(n):
        c = .02 + .3 * (i / n); a += c * (x[i] - a); y[i] = a
    y = y - np.convolve(y, np.ones(40) / 40, "same"); return .6 * env * y / (np.abs(y).max() + 1e-6)

def ching():
    a = tone(1318, .6, .18, 5); b = np.pad(tone(1760, .5, .12, 5), (int(.05 * SR), 0)); b = np.pad(b, (0, max(0, len(a) - len(b))))[:len(a)]
    return a + b

def pop():
    t = np.arange(int(.18 * SR)) / SR; f = 900 * np.exp(-t * 25) + 300
    return (.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)).astype(np.float32)

# ============================================================ helpers
def icon(name, size, stroke, sw="2.6"):
    p = NM / "lucide-static/icons" / f"{name}.svg"
    s = p.read_text() if p.exists() else (NM / "lucide-static/icons/check.svg").read_text()
    s = re.sub(r'width="\d+"', f'width="{size}"', s, count=1); s = re.sub(r'height="\d+"', f'height="{size}"', s, count=1)
    s = s.replace('stroke="currentColor"', f'stroke="{stroke}"').replace('stroke-width="2"', f'stroke-width="{sw}"')
    return re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()

def words_html(text, pid):
    out, i = [], 0
    for tok in re.findall(r"\*[^*]+\*|\S+", text):
        acc = tok.startswith("*"); ws = tok.strip("*").split()
        spans = " ".join(f'<span id="{pid}-{i+j}" class="w">{E(w)}</span>' for j, w in enumerate(ws)); i += len(ws)
        out.append(f'<span class="acc">{spans}</span>' if acc else spans)
    return " ".join(out), i

def words_js(pid, n, t, fam, gap=.07):
    if fam == "ink": return [f'tl.fromTo("#{pid}-{k}",{{scale:2.2,opacity:0,rotation:-8}},{{scale:1,opacity:1,rotation:0,duration:.18,ease:"back.out(2)"}},{T(t+k*gap)})' for k in range(n)]
    if fam == "line": return [f'tl.fromTo("#{pid}-{k}",{{opacity:0,x:-14}},{{opacity:1,x:0,duration:.12,ease:"none"}},{T(t+k*gap)})' for k in range(n)]
    return [f'tl.fromTo("#{pid}-{k}",{{y:50,opacity:0,rotation:5}},{{y:0,opacity:1,rotation:0,duration:.35,ease:"back.out(2)"}},{T(t+k*gap)})' for k in range(n)]

def hsize(text, big=84):
    n = len(re.sub(r"\*", "", text))
    return big if n <= 28 else big - 10 if n <= 42 else big - 20 if n <= 58 else big - 28

def stat_parts(v):
    m = re.match(r"^(.*?)(\d[\d,]*(?:\.\d+)?)(.*)$", v.strip())
    if not m: return None
    num = float(m.group(2).replace(",", "")); dec = len(m.group(2).split(".")[1]) if "." in m.group(2) else 0
    return m.group(1), num, dec, m.group(3), "," in m.group(2)

def plain(t): return re.sub(r"\*", "", t)

def bot_hud():
    pins = "".join(f'<line x1="{a*70}" y1="{yy}" x2="{a*88}" y2="{yy}" stroke="#8B5CF6" stroke-width="7" stroke-linecap="round"/>' for yy in (-72, -44, -16) for a in (-1, 1))
    return (f'<svg width="230" height="270" viewBox="-115 -160 230 270"><g id="hb"><line x1="0" y1="-98" x2="0" y2="-126" stroke="#F3EBDD" stroke-width="8"/>'
            f'<circle cx="0" cy="-134" r="13" fill="#A3E635"/>{pins}<rect x="-72" y="-102" width="144" height="112" rx="28" fill="#22D3EE" stroke="#0A0F1F" stroke-width="5"/>'
            f'<rect x="-52" y="-84" width="104" height="72" rx="18" fill="#0A0F1F"/>'
            f'<ellipse id="hbeL" cx="-22" cy="-58" rx="10" ry="12" fill="#A3E635"/><ellipse id="hbeR" cx="22" cy="-58" rx="10" ry="12" fill="#A3E635"/>'
            f'<rect id="hbm" x="-16" y="-36" width="32" height="9" rx="4.5" fill="#A3E635"/>'
            f'<rect x="-44" y="18" width="88" height="72" rx="18" fill="#8B5CF6" stroke="#0A0F1F" stroke-width="5"/><circle cx="0" cy="54" r="12" fill="#A3E635"/>'
            f'<line x1="-44" y1="36" x2="-84" y2="80" stroke="#F3EBDD" stroke-width="10" stroke-linecap="round"/><circle cx="-84" cy="80" r="13" fill="#A3E635"/>'
            f'<line id="hbaR" x1="44" y1="36" x2="84" y2="80" stroke="#F3EBDD" stroke-width="10" stroke-linecap="round"/><circle id="hbhR" cx="84" cy="80" r="13" fill="#A3E635"/></g></svg>')

# ============================================================ build
def build(data, proj, show_no, date=None):
    from kokoro_onnx import Kokoro
    S = SHOWS[show_no]; fam = S["family"]; st = FAM_ST[fam]
    date = date or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).date()
    seed = date.toordinal()
    k = Kokoro(str(BASE / "kokoro-v1.0.onnx"), str(BASE / "voices-v1.0.bin"))
    proj = pathlib.Path(proj); (proj / "assets/fonts").mkdir(parents=True, exist_ok=True); (proj / "assets/lib").mkdir(parents=True, exist_ok=True)
    shutil.copy(NM / "gsap/dist/gsap.min.js", proj / "assets/lib/gsap.min.js")
    ff = ""
    for fam_name, (src, wt) in (("FTHead", S["head"]), ("FTBody", S["body"]), ("FTSpace", F_SG)):
        dst = pathlib.Path(src).name; shutil.copy(NM / src, proj / "assets/fonts" / dst)
        ff += f"@font-face{{font-family:{fam_name};font-weight:100 900;src:url('assets/fonts/{dst}')}}\n"

    stories = data["stories"][:8]
    order = list(range(len(stories)))[::-1] if S.get("reverse") else list(range(len(stories)))
    n = len(stories)
    segs = [("intro", None)] + [("story", stories[i]) for i in order] + [("outro", None)]
    pos = layout(S["layout"], len(segs))
    TR = {"whip": .75, "zoom": 1.5, "pan": 1.15, "hop": 1.1, "arc": 1.5, "slide": .9, "rotate": 1.2}[S["trans"]]

    # ---------------- voice + timing
    STING = 2.3
    t = STING; plan = []; vo_parts = []; botamp = []
    for si, (kind, s) in enumerate(segs):
        arrive = t
        if kind == "intro": host_txt = data.get("hook_voice", "Here are today's biggest AI and tech updates.")
        elif kind == "outro": host_txt = data.get("outro_voice", "Which update surprised you most? Tell me in the comments, and subscribe for daily AI and tech updates.")
        else: host_txt = s["voice"]
        ha, hw = narrate(k, host_txt, HOST); h0 = arrive + .35
        vo_parts.append((h0, ha)); hd = len(ha) / SR
        words = [("host", [(w, h0 + b, h0 + e) for w, b, e in hw])]
        bot = None; end = h0 + hd
        if kind == "story" and s.get("bot"):
            ba, bw = narrate(k, s["bot"], BOT); b0 = end + .25; vo_parts.append((b0, ba)); bd = len(ba) / SR
            for f in range(0, int(bd * FPS), 2):
                ch = ba[int(f / FPS * SR):int((f + 2) / FPS * SR)]
                botamp.append((b0 + f / FPS, float(np.sqrt(np.mean(ch ** 2))) if len(ch) else 0.0))
            bot = (b0, bd, s["bot"]); end = b0 + bd
        tail = 1.0 if kind == "intro" else .7
        leave = end + tail
        plan.append(dict(kind=kind, s=s, a=arrive, d=leave - arrive, h0=h0, hd=hd, bot=bot, words=words, stn=pos[si], idx=si))
        t = leave + TR
    ENDC = 3.2
    total = round((plan[-1]["a"] + plan[-1]["d"] + ENDC) * FPS) / FPS
    end_at = plan[-1]["a"] + plan[-1]["d"]

    # ---------------- audio mix
    N = int(total * SR) + SR
    vo = np.zeros(N, np.float32)
    for st0, a in vo_parts: i = int(st0 * SR); vo[i:i + len(a)] += a[:N - i]
    mus = bgm(total, S["music"], seed)[:N]; mus = np.pad(mus, (0, max(0, N - len(mus))))
    env = np.convolve((np.abs(vo) > .01).astype(np.float32), np.ones(int(.3 * SR)) / (.3 * SR), "same")
    mus *= (.6 - .42 * np.clip(env * 3, 0, 1)).astype(np.float32)
    sfx = np.zeros(N, np.float32)
    def put(sig, at, g=1.0):
        i = int(at * SR); e = min(N, i + len(sig)); sfx[i:e] += g * sig[:e - i]
    put(whoosh(.6, 1), .2); put(tone(55, .8, .6, 4), .85); put(ching(), 1.05, .5); put(whoosh(.6, 2), 2.1)
    for j, p in enumerate(plan[1:], 1):
        put(whoosh(min(1.0, TR + .1), 10 + j), p["a"] - TR, 1.1)
        if S["trans"] == "hop": put(pop(), p["a"] - .05, 1.0)
        put(pop(), p["a"] + .35, .5)
    put(whoosh(.7, 99), end_at - .1); put(tone(55, .8, .5, 4), end_at + .3); put(ching(), end_at + .45, .45)
    mix = vo + .5 * mus + .65 * sfx
    mix = (mix / max(1.0, np.abs(mix).max() / .95)).astype(np.float32)[:int(total * SR)]
    sf.write(str(proj / "assets/mix.wav"), mix, SR)

    # ---------------- world + timeline
    js, html_st, connectors = [], [], []
    pre = []
    def cam(at, dur, wx, wy, s, rot=0.0, ease="power2.inOut", blur=0):
        th = math.radians(rot)
        x = 960 - s * (wx * math.cos(th) - wy * math.sin(th)); y = 540 - s * (wx * math.sin(th) + wy * math.cos(th))
        js.append(f'tl.to("#world",{{x:{x:.1f},y:{y:.1f},scale:{s:.4f},rotation:{rot:.2f},duration:{T(dur)},ease:"{ease}"}},{T(at)})')
        js.append(f'tl.to("#par1",{{x:{x*.15:.1f},y:{y*.15:.1f},duration:{T(dur)},ease:"{ease}"}},{T(at)})')
        if blur:
            js.append(f'tl.fromTo("#cam",{{filter:"blur(0px)"}},{{filter:"blur({blur}px)",duration:{T(dur*.45)},ease:"power2.in"}},{T(at)})')
            js.append(f'tl.to("#cam",{{filter:"blur(0px)",duration:{T(dur*.55)},ease:"power2.out"}},{T(at+dur*.45)})')
    def setcam(wx, wy, s, rot=0.0):
        th = math.radians(rot)
        x = 960 - s * (wx * math.cos(th) - wy * math.sin(th)); y = 540 - s * (wx * math.sin(th) + wy * math.cos(th))
        js.append(f'tl.set("#world",{{x:{x:.1f},y:{y:.1f},scale:{s:.4f},rotation:{rot:.2f}}},0); tl.set("#par1",{{x:{x*.15:.1f},y:{y*.15:.1f}}},0)')

    p0 = plan[0]; c0 = wpt(p0["stn"], 960, 540); setcam(*c0, 1.18, -p0["stn"][2])
    cam(STING - .1, p0["d"] * .9, *c0, 1.0, -p0["stn"][2], "sine.inOut")

    chap = []
    for p in plan:
        X, Y, r = p["stn"]; i = p["idx"]; a, d = p["a"], p["d"]; sid = f"st{i}"
        mir = S.get("mirror") and (i % 2 == 0)
        tx, ix = (930, 70) if mir else (150, 990)
        inner = ""
        if p["kind"] == "intro":
            teas = [plain(stories[j]["headline"]) for j in order]
            rows = ""; top0 = 410; gap = 66 if len(teas) <= 6 else 54
            for j, tt in enumerate(teas):
                lab = S["label"](j + 1, n)
                rows += f'<div class="tz" id="{sid}-t{j}" style="top:{top0+j*gap}px"><span class="tn">{E(lab.split()[-1] if not lab.startswith("#") else lab)}</span><span>{E(tt)}</span></div>'
            title = data.get("intro_title", "Today's top *AI & tech* updates")
            tw, tn = words_html(title, f"{sid}-h")
            inner = (f'<div class="intro"><div class="kick" id="{sid}-k">{E(S["name"])}</div><div class="ttl h1" style="font-size:{64 if fam == "line" else 96}px">{tw}</div>'
                     f'<div class="date" id="{sid}-dt">{E(date.strftime("%A, %d %B %Y"))}</div>{rows}</div>')
            js.append(f'tl.fromTo("#{sid}-k",{{opacity:0,y:-30,scale:1.6}},{{opacity:1,y:0,scale:1,duration:.7,ease:"expo.out"}},{T(STING-.05)})')
            js += words_js(f"{sid}-h", tn, STING + .1, fam, .09)
            js.append(f'tl.fromTo("#{sid}-dt",{{opacity:0}},{{opacity:1,duration:.4}},{T(STING+.7)})')
            span = max(1.0, p["hd"] - .6)
            for j in range(len(teas)):
                js.append(f'tl.fromTo("#{sid}-t{j}",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:.45,ease:"back.out(1.6)"}},{T(p["h0"]+.3+j*span/len(teas))})')
            chap.append((0.0, "Intro"))
        elif p["kind"] == "outro":
            q = data.get("question", "Which update *surprised* you most?")
            qw, qn = words_html(q, f"{sid}-h")
            inner = (f'<div class="hl" style="left:260px;width:1400px;top:150px;text-align:center"><div class="h1" style="font-size:96px">{qw}</div></div>'
                     f'<div class="ill sc" style="left:710px;top:350px;width:500px;height:333px"><svg viewBox="0 0 600 400">{bot_svg(sid, 300, 260, 1.5, st)}</svg></div>'
                     f'<div class="row" id="{sid}-cta" style="left:0;right:0;top:730px;justify-content:center;gap:30px">'
                     f'<span class="tag" style="font-size:34px">Comment below</span><span class="num" style="font-size:34px;display:flex;align-items:center;gap:12px">'
                     f'{icon("bell", 34, S["ink"])}Subscribe</span></div>')
            js += words_js(f"{sid}-h", qn, a + .3, fam, .08) + ent(st, [f"{sid}-botb"], a + .2) + bot_js(sid, a, d, a + .9, "wave")
            js.append(f'tl.fromTo("#{sid}-cta",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:"back.out(2)"}},{T(a+1.2)})')
            chap.append((a, "Your turn"))
        else:
            s = p["s"]; num_lab = S["label"](i, n)
            shape = scene_for(s); svg, sj = SCENES[shape](sid, a, d, st)
            hw, hn = words_html(s["headline"], f"{sid}-h")
            pts = s.get("points", [])[:3]; stat = s.get("stat") if isinstance(s.get("stat"), dict) and s["stat"].get("value") else None
            hs = hsize(s["headline"], 82 if fam != "ink" else 96)
            pts_top = 245 + int(hs * 1.08 * min(3, math.ceil(len(plain(s["headline"])) / (860 / (hs * .5))))) + 70
            pts_html = "".join(f'<div class="pt" id="{sid}-p{j}"><span class="pi">{icon("check" if fam != "ink" else "zap", 34, "#fff")}</span><span>{E(pt)}</span></div>' for j, pt in enumerate(pts))
            ill_top, ill_w = (150, 800) if stat else (215, 880)
            stat_html = ""
            if stat:
                sp = stat_parts(stat["value"])
                stat_html = (f'<div class="stat" id="{sid}-stat" style="left:{ix}px;top:640px;width:860px">'
                             f'<div class="sv" id="{sid}-sv">{E(stat["value"] if not sp else sp[0] + "0" + sp[3])}</div><div class="sl">{E(stat.get("label", ""))}</div></div>')
            big = f'<div class="bignum" style="left:{ix+120}px;top:40px">{E(num_lab.lstrip("#"))}</div>' if S.get("bignum") else ""
            inner = (f'{big}<div class="row" id="{sid}-row" style="left:{tx}px"><span class="num">{E(num_lab)}</span><span class="tag">{E(s["category"])}</span><span class="src">Source: {E(s["source"])}</span></div>'
                     f'<div class="hl" style="left:{tx}px"><div class="h1" style="font-size:{hs}px">{hw}</div></div>'
                     f'<div class="pts" style="left:{tx}px;top:{pts_top}px">{pts_html}</div>'
                     f'<div class="ill sc" id="{sid}-ill" style="left:{ix + (860-ill_w)//2}px;top:{ill_top}px;width:{ill_w}px;height:{int(ill_w*640/1080)}px"><svg viewBox="0 0 1080 640">{svg}</svg></div>'
                     f'{stat_html}')
            js += sj
            js.append(f'tl.fromTo("#{sid}-row",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{T(a+.05)})')
            js += words_js(f"{sid}-h", hn, a + .2, fam)
            v0, vd = p["h0"], p["hd"]
            for j in range(len(pts)):
                js.append(f'tl.fromTo("#{sid}-p{j}",{{opacity:0,x:{-90 if not mir else 90}}},{{opacity:1,x:0,duration:.5,ease:"back.out(1.7)"}},{T(v0+vd*(.42+j*.17))})')
            if stat:
                sp = stat_parts(stat["value"]); t_st = v0 + vd * .3
                js.append(f'tl.fromTo("#{sid}-stat",{{opacity:0,scale:.6,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:.45,ease:"back.out(2)"}},{T(t_st)})')
                if sp:
                    pre.append(f"const C{i}={{v:0}};")
                    fmt = f'(C{i}.v).toLocaleString("en-US",{{minimumFractionDigits:{sp[2]},maximumFractionDigits:{sp[2]},useGrouping:{"true" if sp[4] or sp[1] >= 10000 else "false"}}})'
                    js.append(f'tl.to(C{i},{{v:{sp[1]},duration:1.4,ease:"power2.out",onUpdate:()=>{{document.getElementById("{sid}-sv").textContent={json.dumps(sp[0])}+{fmt}+{json.dumps(sp[3])}}}}},{T(t_st+.1)})')
                    js.append(f'tl.fromTo("#{sid}-sv",{{scale:1}},{{scale:1.12,duration:.12,yoyo:true,repeat:1,transformOrigin:"50% 50%"}},{T(t_st+1.5)})')
            # camera choreography inside the station (never static)
            rr = -r
            w_ = wpt(p["stn"], 960, 540); ill_c = wpt(p["stn"], ix + 430, ill_top + 260); txt_c = wpt(p["stn"], tx + 430, (pts_top + 150) if pts else 420)
            stat_c = wpt(p["stn"], ix + 430, 720)
            k1 = v0 + vd * .28; k2 = v0 + vd * .52
            lerp = lambda P, f: (w_[0] + (P[0] - w_[0]) * f, w_[1] + (P[1] - w_[1]) * f)
            ill_t = lerp(ill_c, .1); txt_t = lerp(txt_c if pts else stat_c, .1)
            cam(a, max(.3, k1 - a), *w_, 1.03, rr, "sine.inOut")
            cam(k1, .9, *ill_t, 1.06, rr + (1.2 if i % 2 else -1.2), "power2.inOut")
            cam(k1 + .9, max(.3, k2 - k1 - .9), *ill_t, 1.09, rr + (1.8 if i % 2 else -1.8), "none")
            if pts or stat:
                cam(k2, .9, *txt_t, 1.05, rr - (.8 if i % 2 else -.8), "power2.inOut")
                cam(k2 + .9, max(.3, (p["bot"][0] if p["bot"] else a + d) - k2 - .9), *txt_t, 1.08, rr - (1.2 if i % 2 else -1.2), "none")
            if p["bot"]:
                b0, bd, btxt = p["bot"]
                cam(b0 - .2, .8, *w_, .97, rr, "power2.inOut")
                cam(b0 + .6, max(.3, a + d - b0 - .6), *w_, 1.0, rr, "none")
            chap.append((a - TR * .5, plain(s["headline"])))
        cls = "stn"
        html_st.append(f'<div class="{cls}" id="{sid}" style="left:{X:.0f}px;top:{Y:.0f}px;transform:rotate({r}deg)">'
                       f'<div class="stcard">{S["cardx"]}</div>{inner}</div>')
        # visibility window (perf)
        vis_from = a - TR - 1.5; vis_to = a + d + TR + 1.5
        if vis_from > 0: js.append(f'tl.set("#{sid}",{{visibility:"hidden"}},0); tl.set("#{sid}",{{visibility:"visible"}},{T(vis_from)})')
        if vis_to < total: js.append(f'tl.set("#{sid}",{{visibility:"hidden"}},{T(vis_to)})')

    # transitions + connectors
    for j in range(1, len(plan)):
        pa, pb = plan[j - 1], plan[j]; A = wpt(pa["stn"], 960, 540); B = wpt(pb["stn"], 960, 540)
        t0 = pa["a"] + pa["d"]; ra, rb = -pa["stn"][2], -pb["stn"][2]; tr = S["trans"]
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2; dist = math.hypot(B[0] - A[0], B[1] - A[1])
        cp = f"M{A[0]:.0f},{A[1]:.0f} L{B[0]:.0f},{B[1]:.0f}"
        if tr == "whip": cam(t0, TR, *B, 1.03, rb, "power4.inOut", 16)
        elif tr == "slide": cam(t0, TR, *B, 1.03, rb, "power3.inOut", 7)
        elif tr == "pan": cam(t0, TR, *B, 1.03, rb, "power3.inOut", 2)
        elif tr == "zoom":
            cam(t0, TR * .5, mx, my, .3, 0, "power2.in", 3); cam(t0 + TR * .5, TR * .5, *B, 1.03, rb, "power2.out", 3)
        elif tr == "hop":
            cam(t0, TR * .45, mx, my - 650, .55, -4, "power2.out"); cam(t0 + TR * .45, TR * .55, *B, 1.03, rb, "back.out(1.3)")
            cp = f"M{A[0]:.0f},{A[1]:.0f} Q{mx:.0f},{my-900:.0f} {B[0]:.0f},{B[1]:.0f}"
        elif tr == "arc":
            nx, ny = -(B[1] - A[1]) / max(1, dist), (B[0] - A[0]) / max(1, dist)
            qx, qy = mx + nx * dist * .35, my + ny * dist * .35
            cam(t0, TR * .5, (A[0] + qx) / 2 * .5 + qx * .5, (A[1] + qy) / 2 * .5 + qy * .5, .4, 0, "power2.in")
            cam(t0 + TR * .5, TR * .5, *B, 1.03, rb, "power2.out")
            cp = f"M{A[0]:.0f},{A[1]:.0f} Q{qx:.0f},{qy:.0f} {B[0]:.0f},{B[1]:.0f}"
        else:  # rotate
            cam(t0, TR * .5, mx, my, .62, (ra + rb) / 2 + (8 if j % 2 else -8), "power2.in"); cam(t0 + TR * .5, TR * .5, *B, 1.03, rb, "power2.out")
        connectors.append(f'<path id="cn{j}" d="{cp}" pathLength="1" style="stroke-dasharray:1 1;stroke-dashoffset:1"/>')
        js.append(f'tl.fromTo("#cn{j}",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{T(TR)},ease:"power2.inOut"}},{T(t0-.05)})')
    cstroke = S["acc"] if S["family"] != "ink" else "#111"
    conn_svg = (f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="10" height="10">'
                f'<g fill="none" stroke="{cstroke}" stroke-width="{14 if S["family"]=="ink" else 8}" stroke-linecap="round" opacity=".55">{"".join(connectors)}</g></svg>')

    # logo sting + end card
    js += ['tl.fromTo("#lgF",{x:-700,opacity:0},{x:0,opacity:1,duration:.55,ease:"power4.out"},.15)',
           'tl.fromTo("#lgT",{x:700,opacity:0},{x:0,opacity:1,duration:.55,ease:"power4.out"},.45)',
           'tl.fromTo("#lgL",{x:300,y:-300,opacity:0},{x:0,y:0,opacity:1,duration:.4,ease:"back.out(2)"},.8)',
           'tl.fromTo("#lgword",{opacity:0,y:30},{opacity:1,y:0,duration:.45,ease:"expo.out"},1.0)',
           'tl.fromTo(".spd",{scaleX:0,transformOrigin:"100% 50%"},{scaleX:1,duration:.4,ease:"power3.out",stagger:.06},.2)',
           'tl.to(".spd",{opacity:0,duration:.3},1.2)',
           f'tl.to("#logo",{{scale:9,x:1500,y:900,opacity:0,duration:.7,ease:"power3.in",transformOrigin:"50% 50%"}},{T(STING-.3)})',
           f'tl.fromTo("#cam",{{opacity:0}},{{opacity:1,duration:.5}},{T(STING-.2)})',
           f'tl.fromTo(".hud,#ticker",{{opacity:0}},{{opacity:1,duration:.4}},{T(STING)})',
           f'tl.to(".hud,#ticker,.cap",{{opacity:0,duration:.3}},{T(end_at)})',
           f'tl.fromTo("#endcard",{{opacity:0}},{{opacity:1,duration:.35}},{T(end_at)})',
           f'tl.fromTo("#enF",{{x:-500,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power4.out"}},{T(end_at+.1)})',
           f'tl.fromTo("#enT",{{x:500,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power4.out"}},{T(end_at+.3)})',
           f'tl.fromTo("#enL",{{y:-200,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"back.out(2)"}},{T(end_at+.55)})',
           f'tl.fromTo("#endcard .et,#endcard .eh",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,stagger:.15}},{T(end_at+.8)})']

    # HUD progress label
    for p in plan:
        if p["kind"] == "story":
            lab = S["label"](p["idx"], n) + ("" if S.get("reverse") else f" / {n}")
            js.append(f'tl.set("#hudp",{{textContent:{json.dumps(lab)}}},{T(p["a"]-.2)})')
            js.append(f'tl.fromTo("#hudp",{{scale:1.4}},{{scale:1,duration:.3,ease:"back.out(2)"}},{T(p["a"]-.2)})')
        else:
            js.append(f'tl.set("#hudp",{{textContent:{json.dumps("INTRO" if p["kind"]=="intro" else "WRAP-UP")}}},{T(max(0, p["a"]-.2))})')

    # FT Bot HUD
    for p in plan:
        if not p["bot"]: continue
        b0, bd, btxt = p["bot"]; bid = f"bb{p['idx']}"
        js.append(f'tl.set("#bubtxt",{{textContent:{json.dumps(btxt)}}},{T(b0-.4)})')
        js.append(f'tl.fromTo("#bothud",{{y:420}},{{y:0,duration:.5,ease:"back.out(1.6)"}},{T(b0-.4)})')
        js.append(f'tl.fromTo("#bubble",{{scale:.3,opacity:0,transformOrigin:"100% 100%"}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{T(b0-.15)})')
        js.append(f'tl.to("#hbaR",{{attr:{{x2:80,y2:-20}},duration:.25}},{T(b0)}); tl.to("#hbhR",{{attr:{{cx:80,cy:-20}},duration:.25}},{T(b0)})')
        js.append(f'tl.to("#hbaR",{{attr:{{x2:84,y2:80}},duration:.25}},{T(b0+bd)}); tl.to("#hbhR",{{attr:{{cx:84,cy:80}},duration:.25}},{T(b0+bd)})')
        js.append(f'tl.to("#bothud",{{y:420,duration:.45,ease:"power2.in"}},{T(b0+bd+.35)})')
        js.append(f'tl.to("#st{p["idx"]}-stat",{{opacity:.12,duration:.3}},{T(b0-.4)})') if (p["s"].get("stat") or {}).get("value") else None
    for at, amp in botamp:
        js.append(f'tl.set("#hbm",{{attr:{{height:{9+min(16, amp*160):.1f},y:{-36-min(8, amp*80):.1f}}}}},{T(at)})')
    js.append('tl.fromTo("#hb",{y:0},{y:-10,duration:.45,ease:"sine.inOut",repeat:-1,yoyo:true},0)'.replace("repeat:-1", f"repeat:{int(total/.45)}"))

    # captions (host only; bot speaks in the bubble)
    caps = []; cap_bottom = 110 if S.get("ticker") else 56
    for p in plan:
        for spk, ws in p["words"]:
            groups, g = [], []
            for w in ws:
                g.append(w)
                if len(g) >= 6 or re.search(r"[,.!?;:]$", w[0]): groups.append(g); g = []
            if g: groups.append(g)
            for gi, gr in enumerate(groups):
                cs = gr[0][1]; ce = groups[gi + 1][0][1] if gi + 1 < len(groups) else gr[-1][2] + .3
                cid = f"c{p['idx']}_{gi}"
                spans = " ".join(f'<span id="{cid}-{wi}" class="cw">{E(w[0])}</span>' for wi, w in enumerate(gr))
                caps.append(f'<div id="{cid}" class="clip cap" style="bottom:{cap_bottom}px" data-start="{cs:.3f}" data-duration="{max(.2, ce-cs):.3f}" data-track-index="3"><div class="capbox">{spans}</div></div>')
                for wi, w in enumerate(gr):
                    js.append(f'tl.fromTo("#{cid}-{wi}",{{opacity:.4}},{{opacity:1,duration:.08}},{T(w[1])})')

    ticker = ""
    if S.get("ticker"):
        tt = "   ●   ".join(plain(stories[j]["headline"]) for j in order) + "   ●   SUBSCRIBE @FRESHTECHUPDATES   ●   "
        ticker = f'<div id="ticker"><div class="tl">DAILY BRIEF</div><div class="tt" id="tkt">{E(tt * 3)}</div></div>'
        js.append(f'tl.fromTo("#tkt",{{x:0}},{{x:{-int(len(tt)*14.5)},duration:{T(len(tt)*14.5/90)},ease:"none",repeat:{int(total/(len(tt)*14.5/90))+1}}},0)')

    spd = "".join(f'<rect class="spd" x="{x}" y="{y}" width="{w}" height="18" rx="9" fill="#22D3EE" opacity=".8"/>' for x, y, w in ((-20, 520, 260), (30, 610, 200), (0, 700, 210)))
    defs = ('<svg width="0" height="0" style="position:absolute"><defs><filter id="ps" x="-20%" y="-20%" width="140%" height="160%">'
            '<feDropShadow dx="0" dy="9" stdDeviation="0" flood-color="#000" flood-opacity=".25"/></filter></defs></svg>')
    css = BASE_CSS + scene_css(S) + show_css(S) + f".stcard{{{S['card']}}} #bg{{background:{S['bg']}}} #par1{{background:{S['pat']}}}"
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="assets/lib/gsap.min.js"></script>
<style>{ff}{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
{defs}
<div id="bg"></div>
<div id="cam"><div id="par1" class="par"></div><div id="world">{conn_svg}{''.join(html_st)}</div></div>
<div id="brand" class="hud">{logo_svg(64, uid="hb_l")}<span><span style="color:{S['acc2'] if not S.get('light') and S['family']!='ink' else S['acc']}">fresh</span>techupdates</span></div>
<div id="showchip" class="hud"><span>{E(S['name'])}</span><span class="hp" id="hudp">INTRO</span></div>
{ticker}
<div id="bothud"><div id="bubble"><span class="bt">FT BOT</span><span id="bubtxt"></span></div>{bot_hud()}</div>
{''.join(caps)}
<div id="logo"><svg width="1200" height="760" viewBox="-80 300 1220 760" style="overflow:visible">{spd}{logo_inner("lg", ids=True)}
<text id="lgword" x="611" y="1010" text-anchor="middle" font-family="FTSpace" font-weight="700" font-size="74" fill="#F3EBDD" letter-spacing="10">FRESH TECH UPDATES</text></svg></div>
<div id="endcard" class="clip" data-start="{T(end_at)}" data-duration="{T(total-end_at)}" data-track-index="5">
<svg width="620" height="400" viewBox="150 340 935 595">{logo_inner("en", ids=True)}</svg>
<div class="et">SUBSCRIBE FOR DAILY AI &amp; TECH UPDATES</div><div class="eh">@freshtechupdates</div></div>
<audio id="mix" class="clip" src="assets/mix.wav" data-start="0" data-duration="{total}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(pre)}
tl.set("#bothud",{{y:420}},0);
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body></html>"""
    (proj / "index.html").write_text(doc)
    return dict(total=total, chapters=chap, show=S, order=order, stories=stories, seed=seed, date=date)

# ============================================================ thumbnail + youtube metadata
def thumbnail(data, info, out_png):
    from playwright.sync_api import sync_playwright
    S = info["show"]; st = FAM_ST[S["family"]]; top = info["stories"][0]
    svg, _ = SCENES[scene_for(top)]("th", 0, 5, st)
    txt = data.get("thumb_text") or top["headline"]
    tw, _ = words_html(txt, "tt")
    fonts = "".join(f"@font-face{{font-family:{f};font-weight:100 900;src:url('file://{NM / s}')}}" for f, (s, w) in (("FTHead", S["head"]), ("FTBody", S["body"])))
    light = S.get("light"); fam = S["family"]
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1280px;height:720px;overflow:hidden;position:relative;background:{S['bg']}}}
#pat{{position:absolute;inset:0;background:{S['pat']}}}
{scene_css(S)} {show_css(S)}
.h1{{position:absolute;left:56px;top:150px;width:690px;font-size:{108 if len(plain(txt)) < 22 else 92}px;line-height:1.0;{'text-transform:uppercase;' if fam=='line' else ''}}}
.h1 .w{{display:inline-block}}
.ill{{position:absolute;right:-30px;top:120px;width:640px;height:380px}} .ill svg{{width:100%;height:100%;overflow:visible}}
.brand{{position:absolute;left:52px;top:44px;display:flex;align-items:center;gap:14px;font-family:FTHead;font-weight:700;font-size:30px;color:{S['ink']}}}
.chip{{position:absolute;left:56px;bottom:52px;font-family:FTHead;font-weight:700;font-size:30px;letter-spacing:4px;padding:10px 22px;border-radius:10px;background:{S['acc']};color:{'#fff' if light or fam=='ink' else '#0B1020'}}}
.more{{position:absolute;right:50px;bottom:52px;font-family:FTHead;font-weight:700;font-size:34px;color:{S['ink']}}}
</style></head><body><div id="pat"></div>
<svg width="0" height="0" style="position:absolute"><defs><filter id="ps"><feDropShadow dx="0" dy="9" stdDeviation="0" flood-color="#000" flood-opacity=".25"/></filter></defs></svg>
<div class="brand">{logo_svg(70, uid="tl")}<span>freshtechupdates</span></div>
<div class="h1">{tw}</div><div class="ill sc"><svg viewBox="0 0 1080 640">{svg}</svg></div>
<div class="chip">{E(S['name'])}</div><div class="more">+{len(info['stories'])-1} more updates</div>
</body></html>"""
    tmp = pathlib.Path(out_png).with_suffix(".html"); tmp.write_text(page)
    import os
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH", "/usr/bin/google-chrome"), args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1280, "height": 720}); pg.goto(f"file://{tmp.resolve()}"); pg.wait_for_timeout(400)
        pg.screenshot(path=str(out_png)); b.close()
    tmp.unlink()

def ts(sec):
    sec = int(max(0, sec)); return f"{sec//60}:{sec%60:02d}"

def metadata(data, info, out_txt):
    chap = info["chapters"]; lines = []
    title = data.get("title") or f"Today's AI & tech updates: {plain(info['stories'][0]['headline'])}"
    lines.append(f"TITLE:\n{title[:100]}\n")
    desc = [data.get("summary", "Today's biggest AI and tech updates, explained simply."), "", "Chapters:"]
    for t, name in chap: desc.append(f"{ts(t)} {name}")
    desc += ["", "Sources:"] + [f"- {plain(s['headline'])}: {s['source']}" for s in info["stories"]]
    desc += ["", "Subscribe to @freshtechupdates for daily AI & tech updates.", "Instagram: @freshtechupdates", "", "#AI #TechNews #freshtechupdates"]
    lines.append("DESCRIPTION:\n" + "\n".join(desc) + "\n")
    tags = data.get("tags") or []
    tags = list(dict.fromkeys(tags + ["AI news", "tech updates", "artificial intelligence", "daily tech", "freshtechupdates"] + [s["category"] for s in info["stories"]]))
    lines.append("TAGS:\n" + ", ".join(tags)[:480] + "\n")
    lines.append(f"SHOW: {info['show']['name']}   LENGTH: {ts(info['total'])}")
    pathlib.Path(out_txt).write_text("\n".join(lines))

if __name__ == "__main__":
    data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    show = int(sys.argv[3]) if len(sys.argv) > 3 else ist.isoweekday()
    info = build(data, sys.argv[2], show)
    out = BASE / "out"; out.mkdir(exist_ok=True)
    metadata(data, info, out / "youtube.txt")
    thumbnail(data, info, out / "thumbnail.png")
    print(f"built {sys.argv[2]} · show {show} {info['show']['name']} · {info['total']:.1f}s ({ts(info['total'])}) · chapters: {len(info['chapters'])}")
