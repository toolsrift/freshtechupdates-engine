#!/usr/bin/env python3
"""freshtechupdates daily Reel v3 -> HyperFrames project (1080x1920, 30fps, ~30-40s).
Usage: python3 hfreel.py reel.json <project_dir> [seed]
Then:  npx hyperframes render <project_dir> -o out.mp4
reel.json: {"hook":{"headline":"<the single most surprising fact, max 7 words, *accent*>","more":"+2 more AI & tech updates","voice":"..."},
            "stories":[{"category","shape","headline"(4-6 words, *accent*),"source","voice"} x3],
            "outro_question":"Which update surprised you most?","outro_voice":"..."}
shape: rocket | robot | shield | phone | bolt | chip | globe  (3D object that matches the story)
Scene layouts rotate by seed (kinetic | rise | card) and camera moves differ per layout.
Needs in this folder: node_modules (gsap, three, @fontsource/space-grotesk, @fontsource/inter),
kokoro-v1.0.onnx + voices-v1.0.bin, python packages kokoro-onnx soundfile numpy.
"""
import json, sys, re, html, pathlib, shutil, random
import numpy as np, soundfile as sf

BASE = pathlib.Path(__file__).resolve().parent
NM = BASE / "node_modules"
FPS, SR = 30, 24000
VOICE, SPEED = "af_heart", 1.15
ACC, LIME, VIO, INK = "#22D3EE", "#A3E635", "#8B5CF6", "#F8FAFC"
SHAPE_WORDS = [("rocket", "fund|ipo|invest|rais|launch|valuation|business|startup|market|stock"),
               ("robot", "robot|agent|humanoid|automation"),
               ("shield", "secur|privacy|breach|hack|scam|regulat|law|ban|court|policy"),
               ("phone", "phone|gadget|device|iphone|pixel|galaxy|wearable|watch|glasses|laptop"),
               ("bolt", "energy|power|electric|battery|data cent"),
               ("globe", "india|global|world|government|upi|telecom")]

def pick_shape(s):
    if s.get("shape") in ("rocket", "robot", "shield", "phone", "bolt", "chip", "globe"): return s["shape"]
    txt = (s.get("category", "") + " " + s.get("headline", "")).lower()
    for shp, pat in SHAPE_WORDS:
        if re.search(pat, txt): return shp
    return "chip"

import itertools
from ftlogo import logo_svg
_LID = itertools.count()
def chip_svg(size):
    return logo_svg(round(size * 1.45), uid=f"lg{next(_LID)}")

def words_html(text, pid):
    out, i = [], 0
    for tok in re.findall(r"\*[^*]+\*|\S+", text):
        acc = tok.startswith("*")
        for w in tok.strip("*").split():
            out.append(f'<span id="{pid}-{i}" class="w{" acc" if acc else ""}">{html.escape(w)}</span>'); i += 1
    return " ".join(out), i

# ------------------------------------------------------------------ audio
def synth(k, text):
    s, _ = k.create(text.replace("freshtechupdates", "fresh tech updates"), voice=VOICE, speed=SPEED, lang="en-us")
    return s.astype(np.float32)

def narrate(k, text):
    sents = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]
    parts, words, t = [], [], 0.0
    for s in sents:
        a = synth(k, s); d = len(a) / SR
        ws = s.split(); wt = [len(w) + 2 + (3 if re.search(r"[,.!?;:]$", w) else 0) for w in ws]
        tot = sum(wt); span = max(0.1, d - 0.16); c = t + 0.07
        for w, x in zip(ws, wt):
            dd = span * x / tot; words.append((w, c, c + dd)); c += dd
        parts += [a, np.zeros(int(0.08 * SR), np.float32)]; t += d + 0.08
    return np.concatenate(parts), words

def whoosh(dur=0.42, seed=1):
    rng = np.random.default_rng(seed); n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32); env = np.sin(np.linspace(0, np.pi, n)) ** 2
    y = np.zeros(n, np.float32); a = 0.0
    for i in range(n):
        c = 0.02 + 0.25 * (i / n); a += c * (x[i] - a); y[i] = a
    y = y - np.convolve(y, np.ones(40) / 40, "same")
    return 0.55 * env * y / (np.abs(y).max() + 1e-6)

def hit(dur=0.35):
    t = np.arange(int(dur * SR)) / SR; f = 120 * np.exp(-t * 18) + 45
    return (0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)).astype(np.float32)

# ------------------------------------------------------------------ look
CSS = """
@font-face{font-family:FTSpace;font-weight:500;src:url('assets/fonts/sg-500.woff2')}
@font-face{font-family:FTSpace;font-weight:700;src:url('assets/fonts/sg-700.woff2')}
@font-face{font-family:FTInter;font-weight:700;src:url('assets/fonts/inter-700.woff2')}
@font-face{font-family:FTInter;font-weight:800;src:url('assets/fonts/inter-800.woff2')}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#05070F}
#root{position:relative;width:100%;height:100%;font-family:FTInter,sans-serif;color:#F8FAFC;overflow:hidden}
#bg{position:absolute;inset:0;background:radial-gradient(circle at 85% 12%,rgba(34,211,238,.30),transparent 38%),radial-gradient(circle at 8% 82%,rgba(139,92,246,.34),transparent 44%),linear-gradient(180deg,#0A0F1F,#05070F)}
#grid{position:absolute;left:-60px;top:-120px;width:1200px;height:2160px;background:linear-gradient(rgba(34,211,238,.06) 2px,transparent 2px) 0 0/60px 60px,linear-gradient(90deg,rgba(34,211,238,.06) 2px,transparent 2px) 0 0/60px 60px}
#floor{position:absolute;left:-540px;width:2160px;top:1360px;height:620px;perspective:1100px;overflow:hidden;-webkit-mask-image:linear-gradient(180deg,transparent,#000 25%);mask-image:linear-gradient(180deg,transparent,#000 25%)}
#floorp{position:absolute;left:0;top:0;width:2160px;height:1400px;transform:rotateX(72deg);transform-origin:50% 0;background:linear-gradient(rgba(34,211,238,.6) 3px,transparent 3px) 0 0/70px 70px,linear-gradient(90deg,rgba(139,92,246,.65) 3px,transparent 3px) 0 0/70px 70px}
#horizon{position:absolute;left:0;right:0;top:1352px;height:4px;background:linear-gradient(90deg,transparent,#22D3EE,#A3E635,#22D3EE,transparent);box-shadow:0 0 30px #22D3EE}
#gl{position:absolute;left:0;top:360px;width:1080px;height:540px}
.scene{position:absolute;inset:0}
.inner{position:absolute;inset:0}
.w{display:inline-block}
.acc{color:#22D3EE}
.lime{color:#A3E635}
#top{position:absolute;left:0;top:0;width:1080px;height:300px}
.bars{position:absolute;left:72px;right:72px;top:188px;display:flex;gap:10px}
.bar{flex:1;height:8px;border-radius:8px;background:rgba(255,255,255,.16);overflow:hidden}
.fill{height:100%;width:100%;background:linear-gradient(90deg,#22D3EE,#A3E635);transform-origin:0 50%}
.brand{position:absolute;left:72px;top:216px;display:flex;align-items:center;gap:16px;font-family:FTSpace;font-weight:700;font-size:36px;letter-spacing:-1px}
.cap{position:absolute;left:0;right:0;top:1190px;display:flex;justify-content:center}
.capbox{max-width:900px;text-align:center;font-family:FTInter;font-weight:800;font-size:52px;line-height:1.15;padding:14px 26px;border-radius:22px;background:rgba(5,7,15,.78);border:2px solid rgba(34,211,238,.3)}
.capbox .cw{display:inline-block}
.pill{display:inline-block;font-family:FTSpace;font-weight:700;font-size:26px;letter-spacing:4px;text-transform:uppercase;color:#A3E635;border:2px solid rgba(163,230,53,.6);border-radius:999px;padding:9px 24px;background:rgba(163,230,53,.07)}
.num{font-family:FTSpace;font-weight:700;font-size:34px;color:#0A0F1F;background:linear-gradient(145deg,#22D3EE,#8B5CF6);border-radius:14px;padding:6px 16px}
.src{font-family:FTInter;font-weight:700;font-size:24px;color:#7C8AA5}
.h1{font-family:FTSpace;font-weight:700;letter-spacing:-2px;line-height:1.04}
"""

def toprow(sid, i, total, s):
    return (f'<div id="{sid}-top" style="position:absolute;left:72px;right:72px;top:300px;display:flex;gap:16px;align-items:center">'
            f'<span class="num">{i:02d}/{total:02d}</span><span class="pill">{html.escape(s["category"])}</span>'
            f'<span class="src" style="margin-left:auto">Source: {html.escape(s["source"])}</span></div>')

def lay_kinetic(i, total, s, a, d):
    sid = f"s{i}"; hw, nw = words_html(s["headline"], f"{sid}-h")
    m = (f'<div class="inner" id="{sid}-in">'
         f'<div id="{sid}-ghost" class="h1" style="position:absolute;right:40px;top:380px;font-size:460px;color:transparent;-webkit-text-stroke:3px rgba(163,230,53,.18)">{i:02d}</div>'
         + toprow(sid, i, total, s) +
         f'<div class="h1" style="position:absolute;left:72px;right:72px;top:920px;font-size:96px">{hw}</div></div>')
    js = [f'tl.fromTo("#{sid}-top",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.45,ease:"expo.out"}},{a+.05})',
          f'tl.fromTo("#{sid}-ghost",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:.8,ease:"expo.out"}},{a})']
    for k in range(nw):
        js.append(f'tl.fromTo("#{sid}-h-{k}",{{opacity:0,scale:1.6,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.2,ease:"power4.out"}},{a+.3+k*.09:.3f})')
    js.append(f'tl.fromTo("#{sid}-in",{{x:0,filter:"blur(0px)"}},{{x:-300,filter:"blur(16px)",opacity:0,duration:.22,ease:"power3.in"}},{a+d-.24:.3f})')
    return m, js

def lay_rise(i, total, s, a, d):
    sid = f"s{i}"; hw, nw = words_html(s["headline"], f"{sid}-h")
    m = (f'<div class="inner" id="{sid}-in">' + toprow(sid, i, total, s) +
         f'<div id="{sid}-ring" style="position:absolute;left:190px;top:380px;width:700px;height:500px;border-radius:50%;border:2px solid rgba(34,211,238,.22)"></div>'
         f'<div class="h1" style="position:absolute;left:60px;right:60px;top:920px;font-size:92px;text-align:center">{hw}</div></div>')
    js = [f'tl.fromTo("#{sid}-top",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{a+.05})',
          f'tl.fromTo("#{sid}-ring",{{scale:.5,opacity:0}},{{scale:1.08,opacity:1,duration:{d},ease:"power1.out"}},{a})']
    for k in range(nw):
        js.append(f'tl.fromTo("#{sid}-h-{k}",{{opacity:0,y:70,rotationX:-70}},{{opacity:1,y:0,rotationX:0,duration:.45,ease:"expo.out"}},{a+.35+k*.07:.3f})')
    js.append(f'tl.fromTo("#{sid}-in",{{scale:1,filter:"blur(0px)"}},{{scale:1.2,filter:"blur(14px)",opacity:0,duration:.22,ease:"power3.in"}},{a+d-.24:.3f})')
    return m, js

def lay_card(i, total, s, a, d):
    sid = f"s{i}"; hw, nw = words_html(s["headline"], f"{sid}-h")
    m = (f'<div class="inner" id="{sid}-in" style="perspective:1400px">' + toprow(sid, i, total, s) +
         f'<div id="{sid}-card" style="position:absolute;left:72px;right:72px;top:890px;padding:34px 44px;border-radius:36px;overflow:hidden;'
         f'background:linear-gradient(150deg,rgba(139,92,246,.32),rgba(17,24,51,.94) 55%,rgba(34,211,238,.18));border:2px solid rgba(255,255,255,.18);box-shadow:0 40px 100px rgba(0,0,0,.5),0 0 70px rgba(34,211,238,.16)">'
         f'<div class="h1" style="font-size:80px">{hw}</div>'
         f'<div id="{sid}-sweep" style="position:absolute;top:-30%;left:0;width:220px;height:160%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.16),transparent);transform:rotate(14deg)"></div></div></div>')
    js = [f'tl.fromTo("#{sid}-top",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{a+.05})',
          f'tl.fromTo("#{sid}-card",{{rotationX:75,y:120,opacity:0,transformOrigin:"50% 100%"}},{{rotationX:0,y:0,opacity:1,duration:.7,ease:"expo.out"}},{a+.25})',
          f'tl.fromTo("#{sid}-sweep",{{x:-400}},{{x:1300,duration:1.0,ease:"power2.inOut"}},{a+.8})']
    for k in range(nw):
        js.append(f'tl.fromTo("#{sid}-h-{k}",{{opacity:.12}},{{opacity:1,duration:.16,ease:"power2.out"}},{a+.45+k*.08:.3f})')
    js.append(f'tl.fromTo("#{sid}-in",{{clipPath:"circle(150% at 50% 40%)"}},{{clipPath:"circle(0% at 50% 40%)",duration:.28,ease:"power3.in"}},{a+d-.3:.3f})')
    return m, js

LAYOUTS = {"kinetic": lay_kinetic, "rise": lay_rise, "card": lay_card}
CAMS = {"kinetic": "dolly", "rise": "orbit", "card": "tilt"}

def hook_scene(h, a, d):
    fw, nw = words_html(h["headline"], "hk")
    plain = html.escape(re.sub(r"\*", "", h["headline"]))
    m = ('<div class="inner" id="hook-in">'
         '<div style="position:absolute;left:0;right:0;top:330px;text-align:center"><span class="pill">Today in AI &amp; tech</span></div>'
         '<div style="position:absolute;left:60px;right:60px;top:420px;text-align:center" data-layout-allow-overlap>'
         f'<div id="hook-r" class="h1" style="position:absolute;left:0;right:0;font-size:124px;color:#ff2e88;mix-blend-mode:screen;opacity:0">{plain}</div>'
         f'<div id="hook-c" class="h1" style="position:absolute;left:0;right:0;font-size:124px;color:#22D3EE;mix-blend-mode:screen;opacity:0">{plain}</div>'
         f'<div id="hook-t" class="h1" style="position:relative;font-size:124px">{fw}</div></div>'
         f'<div id="hook-more" style="position:absolute;left:0;right:0;top:1010px;text-align:center"><span class="h1" style="font-size:52px;padding:14px 34px;border-radius:999px;background:#A3E635;color:#0A0F1F;letter-spacing:-1px">{html.escape(h.get("more","+2 more AI & tech updates"))}</span></div></div>')
    js = [f'tl.fromTo("#hook-t",{{scale:1}},{{scale:1.05,duration:{d},ease:"none"}},0)']
    rnd = random.Random(7)
    for t0 in (0.12, 0.85, 1.7):
        for j in range(4):
            dx = rnd.choice([-1, 1]) * rnd.randint(10, 26); tt = a + t0 + j * 0.05
            js.append(f'tl.set("#hook-r",{{x:{dx},opacity:.85}},{tt:.3f}); tl.set("#hook-c",{{x:{-dx},opacity:.85}},{tt:.3f}); tl.set("#hook-t",{{x:{dx//3},skewX:{rnd.randint(-7,7)}}},{tt:.3f})')
        js.append(f'tl.set(["#hook-r","#hook-c"],{{x:0,opacity:0}},{a+t0+0.2:.3f}); tl.set("#hook-t",{{x:0,skewX:0}},{a+t0+0.2:.3f})')
    js.append(f'tl.fromTo("#hook-more",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.45,ease:"back.out(2)"}},{a+min(1.4, d*.45):.3f})')
    js.append(f'tl.fromTo("#hook-in",{{y:0,filter:"blur(0px)"}},{{y:-280,filter:"blur(18px)",opacity:0,duration:.22,ease:"power3.in"}},{a+d-.24:.3f})')
    return m, js

def outro_scene(q, a, d):
    qw, nq = words_html(q, "oq")
    m = ('<div class="inner" id="out-in">'
         f'<div id="out-logo" style="position:absolute;left:460px;top:320px">{chip_svg(160)}</div>'
         f'<div class="h1" style="position:absolute;left:72px;right:72px;top:520px;text-align:center;font-size:96px">{qw}</div>'
         '<div id="out-c" style="position:absolute;left:0;right:0;top:880px;text-align:center"><span class="h1" style="font-size:46px;padding:14px 34px;border-radius:999px;background:#A3E635;color:#0A0F1F">Comment below</span></div>'
         '<div id="out-h" class="h1" style="position:absolute;left:0;right:0;top:1000px;text-align:center;font-size:58px">Follow @<span class="lime">fresh</span>techupdates</div></div>')
    js = [f'tl.fromTo("#out-logo",{{scale:0,rotation:-90}},{{scale:1,rotation:0,duration:.6,ease:"back.out(1.6)"}},{a+.05})']
    for k in range(nq):
        js.append(f'tl.fromTo("#oq-{k}",{{opacity:0,y:50}},{{opacity:1,y:0,duration:.35,ease:"expo.out"}},{a+.2+k*.07:.3f})')
    js += [f'tl.fromTo("#out-c",{{opacity:0,scale:.7}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}},{a+.8})',
           f'tl.fromTo("#out-h",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:"expo.out"}},{a+1.0})']
    return m, js

THREE_JS = r"""
<script type="importmap">{"imports":{"three":"./assets/lib/three/three.module.js","three/addons/":"./assets/lib/three/addons/"}}</script>
<script type="module">
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
const WINDOWS = __WINDOWS__;
const canvas = document.getElementById("gl");
const r = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true, preserveDrawingBuffer:true});
r.setPixelRatio(1); r.setSize(1080, 540, false); r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.1;
const scene = new THREE.Scene();
const pm = new THREE.PMREMGenerator(r); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
const cam = new THREE.PerspectiveCamera(30, 1080/540, 0.1, 100);
scene.add(new THREE.AmbientLight(0x223355, 0.5));
const key = new THREE.DirectionalLight(0xffffff, 2.0); key.position.set(3,4,5); scene.add(key);
const rim1 = new THREE.PointLight(0x22d3ee, 70, 30); rim1.position.set(-4,1,-2); scene.add(rim1);
const rim2 = new THREE.PointLight(0x8b5cf6, 70, 30); rim2.position.set(4,-2,-1); scene.add(rim2);
const P = (o)=>new THREE.MeshPhysicalMaterial(Object.assign({metalness:0.5, roughness:0.28, clearcoat:1, clearcoatRoughness:0.12, envMapIntensity:1}, o));
const M = {
  navy: P({color:0x1a2350, emissive:0x0a1030}),
  silver: P({color:0xdde4f2, metalness:0.85, roughness:0.22}),
  cyan: P({color:0x22d3ee, metalness:0.3, roughness:0.25}),
  violet: P({color:0x8b5cf6, metalness:0.35, roughness:0.3}),
  glowC: new THREE.MeshStandardMaterial({color:0x22d3ee, emissive:0x22d3ee, emissiveIntensity:1.6}),
  glowL: new THREE.MeshStandardMaterial({color:0xa3e635, emissive:0xa3e635, emissiveIntensity:1.6}),
  flame: new THREE.MeshBasicMaterial({color:0xa3e635, transparent:true, opacity:0.75, blending:THREE.AdditiveBlending, depthWrite:false}),
  edge: new THREE.LineBasicMaterial({color:0x22d3ee, transparent:true, opacity:0.6})
};
function rrect(w,h,rad){ const s=new THREE.Shape(), x=-w/2, y=-h/2;
  s.moveTo(x+rad,y); s.lineTo(x+w-rad,y); s.quadraticCurveTo(x+w,y,x+w,y+rad); s.lineTo(x+w,y+h-rad); s.quadraticCurveTo(x+w,y+h,x+w-rad,y+h);
  s.lineTo(x+rad,y+h); s.quadraticCurveTo(x,y+h,x,y+h-rad); s.lineTo(x,y+rad); s.quadraticCurveTo(x,y,x+rad,y); return s; }
function ext(shape, depth, bev){ const g=new THREE.ExtrudeGeometry(shape,{depth, bevelEnabled:true, bevelThickness:bev, bevelSize:bev, bevelSegments:6, curveSegments:24}); g.center(); return g; }
function build(kind){
  const g=new THREE.Group(); const add=(geo,mat,x=0,y=0,z=0)=>{const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); g.add(m); return m;};
  if(kind==="rocket"){
    add(new THREE.CylinderGeometry(0.42,0.46,1.5,48), M.silver);
    add(new THREE.ConeGeometry(0.42,0.75,48), M.cyan, 0,1.12,0);
    const win=add(new THREE.SphereGeometry(0.17,32,16), M.glowC, 0,0.35,0.38); win.scale.z=0.45;
    const ring=add(new THREE.TorusGeometry(0.19,0.035,12,40), M.violet, 0,0.35,0.4);
    const fs=new THREE.Shape(); fs.moveTo(0,0); fs.lineTo(0.42,-0.35); fs.lineTo(0.42,-0.75); fs.lineTo(0,-0.45); fs.closePath();
    for(let k=0;k<3;k++){ const f=new THREE.Mesh(ext(fs,0.05,0.02), M.violet); const ang=k*Math.PI*2/3; f.position.set(Math.sin(ang)*0.5,-0.4,Math.cos(ang)*0.5); f.rotation.y=ang-Math.PI/2; g.add(f); }
    const fl=add(new THREE.ConeGeometry(0.3,0.9,32), M.flame, 0,-1.25,0); fl.rotation.x=Math.PI; fl.name="flame";
    g.rotation.z=-0.55; g.userData.base=0.95;
  } else if(kind==="robot"){
    add(ext(rrect(1.7,1.35,0.32),0.8,0.08), M.silver);
    add(ext(rrect(1.35,0.85,0.2),0.05,0.02), M.navy, 0,0,0.5);
    add(new THREE.SphereGeometry(0.15,32,16), M.glowC, -0.32,0.08,0.56); add(new THREE.SphereGeometry(0.15,32,16), M.glowC, 0.32,0.08,0.56);
    add(new THREE.BoxGeometry(0.5,0.06,0.04), M.glowL, 0,-0.22,0.56);
    add(new THREE.CylinderGeometry(0.035,0.035,0.45,12), M.silver, 0,0.95,0); add(new THREE.SphereGeometry(0.11,24,12), M.glowL, 0,1.22,0);
    for(const s of [-1,1]){ const e=add(new THREE.CylinderGeometry(0.2,0.2,0.18,32), M.violet, s*0.98,0,0); e.rotation.z=Math.PI/2; }
    g.userData.base=1.0;
  } else if(kind==="shield"){
    const s=new THREE.Shape(); s.moveTo(0,1.1); s.quadraticCurveTo(0.6,0.98,1.0,0.88); s.lineTo(1.0,0.1); s.quadraticCurveTo(0.92,-0.72,0,-1.2);
    s.quadraticCurveTo(-0.92,-0.72,-1.0,0.1); s.lineTo(-1.0,0.88); s.quadraticCurveTo(-0.6,0.98,0,1.1);
    const sg=ext(s,0.28,0.08); add(sg, M.violet); g.add(new THREE.LineSegments(new THREE.EdgesGeometry(sg,30), M.edge));
    const path=new THREE.CatmullRomCurve3([new THREE.Vector3(-0.42,0.02,0.3),new THREE.Vector3(-0.12,-0.3,0.3),new THREE.Vector3(0.48,0.42,0.3)],false,"catmullrom",0.05);
    add(new THREE.TubeGeometry(path,40,0.09,16,false), M.glowL);
    g.userData.base=0.95;
  } else if(kind==="phone"){
    add(ext(rrect(1.1,2.15,0.2),0.12,0.04), M.navy);
    const cv=document.createElement("canvas"); cv.width=256; cv.height=512; const c=cv.getContext("2d");
    const gr=c.createLinearGradient(0,0,256,512); gr.addColorStop(0,"#22D3EE"); gr.addColorStop(1,"#8B5CF6"); c.fillStyle=gr; c.fillRect(0,0,256,512);
    c.fillStyle="rgba(10,15,31,.55)"; for(let k=0;k<5;k++){ c.beginPath(); c.roundRect(24,90+k*80,208,56,14); c.fill(); }
    c.fillStyle="#A3E635"; c.beginPath(); c.roundRect(24,30,120,30,12); c.fill();
    const tex=new THREE.CanvasTexture(cv); tex.colorSpace=THREE.SRGBColorSpace;
    add(new THREE.PlaneGeometry(0.98,2.0), new THREE.MeshBasicMaterial({map:tex}), 0,0,0.11);
    add(new THREE.SphereGeometry(0.05,16,8), M.glowL, 0.3,0.9,-0.11);
    g.userData.base=0.95;
  } else if(kind==="bolt"){
    const s=new THREE.Shape(); s.moveTo(0.25,1.25); s.lineTo(-0.62,-0.08); s.lineTo(-0.06,-0.08); s.lineTo(-0.32,-1.25); s.lineTo(0.62,0.18); s.lineTo(0.06,0.18); s.closePath();
    const bg=ext(s,0.3,0.06); add(bg, new THREE.MeshPhysicalMaterial({color:0x6d8f1d, emissive:0xa3e635, emissiveIntensity:0.55, metalness:0.3, roughness:0.25, clearcoat:1}));
    g.add(new THREE.LineSegments(new THREE.EdgesGeometry(bg,30), M.edge));
    g.userData.base=1.0;
  } else if(kind==="globe"){
    add(new THREE.SphereGeometry(1.0,64,32), M.navy);
    g.add(new THREE.LineSegments(new THREE.WireframeGeometry(new THREE.SphereGeometry(1.03,18,12)), M.edge));
    const ring=add(new THREE.TorusGeometry(1.45,0.04,12,120), M.glowL); ring.rotation.x=1.2; ring.rotation.y=0.3;
    add(new THREE.SphereGeometry(0.09,16,8), M.glowC, 1.45,0,0);
    g.userData.base=0.95;
  } else {
    add(new THREE.BoxGeometry(1.9,0.3,1.9), M.navy);
    add(new THREE.BoxGeometry(0.95,0.06,0.95), M.glowC, 0,0.18,0);
    for(let k=0;k<4;k++){ for(const s of [-1,1]){ add(new THREE.BoxGeometry(0.12,0.08,0.34), M.silver, -0.6+k*0.4,0,s*1.12); const q=add(new THREE.BoxGeometry(0.34,0.08,0.12), M.silver, s*1.12,0,-0.6+k*0.4); } }
    g.userData.base=0.9;
  }
  return g;
}
const objs={};
for(const w of WINDOWS){
  const grp=new THREE.Group(); const o=build(w.shape); grp.add(o);
  const N=150, pos=new Float32Array(N*3); let sd=w.seed>>>0;
  const rnd=()=>{sd|=0; sd=sd+0x6D2B79F5|0; let t=Math.imul(sd^sd>>>15,1|sd); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296;};
  for(let k=0;k<N;k++){const a=rnd()*Math.PI*2, rr=1.8+rnd()*1.0, y=(rnd()-0.5)*1.8; pos.set([Math.cos(a)*rr,y,Math.sin(a)*rr],k*3);}
  const pg=new THREE.BufferGeometry(); pg.setAttribute("position", new THREE.BufferAttribute(pos,3));
  const pts=new THREE.Points(pg, new THREE.PointsMaterial({color:0xa3e635, size:0.035, transparent:true, opacity:0.85})); grp.add(pts);
  grp.visible=false; scene.add(grp); objs[w.id]={grp, o, pts};
}
const ease=(x)=>{x=Math.min(Math.max(x,0),1); return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;};
const back=(x)=>{x=Math.min(Math.max(x,0),1); const c=1.5; return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);};
function renderAt(t){
  let any=false;
  for(const w of WINDOWS){
    const {grp,o,pts}=objs[w.id], lt=t-w.start, on=lt>=0 && lt<w.dur;
    grp.visible=on; if(!on) continue; any=true;
    const p=lt/w.dur, base=o.userData.base||1;
    grp.scale.setScalar(base*(0.15+0.85*back(lt/0.65)));
    pts.rotation.y=lt*0.25;
    if(w.shape==="rocket"){ o.position.set(0, -0.15+0.35*ease(p), 0); o.rotation.y=lt*0.9; const f=o.getObjectByName("flame"); if(f){ f.scale.set(1,0.85+0.25*Math.abs(Math.sin(lt*23)),1); } }
    else if(w.shape==="globe"){ o.rotation.y=lt*0.6; o.rotation.x=0.25; }
    else if(w.shape==="chip"){ o.rotation.set(0.55, lt*0.6, 0.1); }
    else { o.rotation.set(Math.sin(lt*0.9)*0.12, Math.sin(lt*0.7)*0.55, Math.sin(lt*0.5)*0.05); }
    if(w.cam==="orbit"){ const ang=-0.6+1.2*ease(p); cam.position.set(Math.sin(ang)*5.6, 0.5, Math.cos(ang)*5.6); }
    else if(w.cam==="tilt"){ const e=ease(lt/1.4); cam.position.set(0, 3.2-2.8*e, 4.2+1.2*e); }
    else { cam.position.set(Math.sin(lt*0.3)*0.5, 0.35, 6.6-1.5*ease(p)); }
    cam.lookAt(0,0,0);
    rim1.position.set(Math.cos(lt*0.8)*4,1,Math.sin(lt*0.8)*4-1);
  }
  if(any) r.render(scene, cam); else r.clear();
}
window.__hf=window.__hf||{}; window.__hf.buildReady=window.__hf.buildReady||{};
window.__hf.buildReady["ft3d"] = r.compileAsync ? r.compileAsync(scene, cam) : Promise.resolve();
window.addEventListener("hf-seek", (e)=>renderAt(e.detail.time));
renderAt(0);
</script>
"""

def build(data, proj, seed):
    from kokoro_onnx import Kokoro
    k = Kokoro(str(BASE / "kokoro-v1.0.onnx"), str(BASE / "voices-v1.0.bin"))
    proj = pathlib.Path(proj); (proj / "assets/fonts").mkdir(parents=True, exist_ok=True)
    lib = proj / "assets/lib"; (lib / "three/addons/environments").mkdir(parents=True, exist_ok=True)
    shutil.copy(NM / "gsap/dist/gsap.min.js", lib / "gsap.min.js")
    for f in ("three.module.js", "three.core.js"): shutil.copy(NM / "three/build" / f, lib / "three" / f)
    shutil.copy(NM / "three/examples/jsm/environments/RoomEnvironment.js", lib / "three/addons/environments/RoomEnvironment.js")
    for src, dst in [("@fontsource/space-grotesk/files/space-grotesk-latin-500-normal.woff2", "sg-500"), ("@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2", "sg-700"),
                     ("@fontsource/inter/files/inter-latin-700-normal.woff2", "inter-700"), ("@fontsource/inter/files/inter-latin-800-normal.woff2", "inter-800")]:
        shutil.copy(NM / src, proj / f"assets/fonts/{dst}.woff2")

    rng = random.Random(seed); order = ["kinetic", "rise", "card"]; rng.shuffle(order)
    stories = data["stories"][:3]; total_st = len(stories)
    plan = [("hook", data["hook"], data["hook"]["voice"])]
    plan += [(order[i % 3], s, s["voice"]) for i, s in enumerate(stories)]
    plan.append(("outro", None, data.get("outro_voice", "Which one surprised you most? Tell me in the comments, and follow fresh tech updates for daily AI & tech updates.")))

    audio, t, scenes = [], 0.0, []
    for st, s, v in plan:
        a, ws = narrate(k, v)
        lead, tail = 0.3, 0.35
        dur = round((lead + len(a) / SR + tail) * FPS) / FPS
        seg = np.zeros(int(round(dur * SR)), np.float32); seg[int(lead * SR):int(lead * SR) + len(a)] = a
        audio.append(seg); scenes.append(dict(style=st, s=s, start=round(t, 4), dur=dur, words=[(w, t + lead + b, t + lead + e) for w, b, e in ws])); t += dur
    total = round(t * FPS) / FPS
    vo = np.concatenate(audio)
    for j, sc in enumerate(scenes[1:], 1):
        p = int((sc["start"] - 0.2) * SR); w = whoosh(seed=j); vo[p:p + len(w)] += 0.5 * w[:len(vo) - p]
        q = int(sc["start"] * SR); hh = hit(); vo[q:q + len(hh)] += 0.35 * hh[:len(vo) - q]
    vo = (vo / max(1.0, np.abs(vo).max() / 0.95)).astype(np.float32)
    sf.write(str(proj / "assets/vo.wav"), vo, SR)

    body, js, windows, caps = [], [], [], []
    n = len(scenes)
    for i, sc in enumerate(scenes):
        a, d = sc["start"], sc["dur"]
        if sc["style"] == "hook": m, j = hook_scene(sc["s"], a, d)
        elif sc["style"] == "outro": m, j = outro_scene(data.get("outro_question", "Which update surprised you most?"), a, d)
        else:
            m, j = LAYOUTS[sc["style"]](i, total_st, sc["s"], a, d)
            windows.append(dict(id=f"s{i}", start=a, dur=d, shape=pick_shape(sc["s"]), cam=CAMS[sc["style"]], seed=seed * 31 + i))
            j += [f'tl.fromTo("#gl",{{opacity:0}},{{opacity:1,duration:.3,ease:"power2.out"}},{a})', f'tl.to("#gl",{{opacity:0,duration:.2,ease:"power2.in"}},{a+d-.22:.3f})']
        body.append(f'<div id="sc{i}" class="clip scene" data-start="{a}" data-duration="{d}" data-track-index="2" style="z-index:5">{m}</div>')
        js += j
        js.append(f'tl.fromTo("#fill{i}",{{scaleX:0}},{{scaleX:1,duration:{d},ease:"none"}},{a})')
        if sc["style"] in ("hook", "outro"): continue  # big on-screen text already says it
        ws = sc["words"]; g, groups = [], []
        for w in ws:
            g.append(w)
            if len(g) >= 3 or re.search(r"[.,!?;:]$", w[0]): groups.append(g); g = []
        if g: groups.append(g)
        for gi, gr in enumerate(groups):
            cs = gr[0][1]; ce = groups[gi + 1][0][1] if gi + 1 < len(groups) else min(gr[-1][2] + 0.35, a + d - 0.05)
            cid = f"c{i}_{gi}"
            spans = " ".join(f'<span id="{cid}-{wi}" class="cw">{html.escape(w[0])}</span>' for wi, w in enumerate(gr))
            caps.append(f'<div id="{cid}" class="clip cap" data-start="{cs:.3f}" data-duration="{max(0.2, ce - cs):.3f}" data-track-index="3" style="z-index:8"><div class="capbox">{spans}</div></div>')
            for wi, w in enumerate(gr):
                js.append(f'tl.fromTo("#{cid}-{wi}",{{opacity:.25,y:8}},{{opacity:1,y:0,color:"#A3E635",duration:.1,ease:"power2.out"}},{w[1]:.3f})')
                js.append(f'tl.to("#{cid}-{wi}",{{color:"#F8FAFC",duration:.12}},{w[2]:.3f})')
    bars = "".join(f'<div class="bar"><div id="fill{i}" class="fill"></div></div>' for i in range(n))
    top = (f'<div id="top" class="clip" data-start="0" data-duration="{total}" data-track-index="4" style="z-index:9">'
           f'<div class="bars">{bars}</div><div class="brand">{chip_svg(64)}<span><span class="lime">fresh</span>techupdates</span></div></div>')
    js.insert(0, f'tl.fromTo("#grid",{{y:0}},{{y:120,duration:{total},ease:"none"}},0)')
    js.insert(1, f'tl.fromTo("#floorp",{{backgroundPosition:"0px 0px, 0px 0px"}},{{backgroundPosition:"0px {int(total*90)}px, 0px 0px",duration:{total},ease:"none"}},0)')
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="assets/lib/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
<div id="bg"></div><div id="grid"></div><div id="floor"><div id="floorp"></div></div><div id="horizon"></div>
<canvas id="gl" width="1080" height="540" style="opacity:0;z-index:2"></canvas>
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
{THREE_JS.replace("__WINDOWS__", json.dumps(windows))}
</body></html>"""
    (proj / "index.html").write_text(doc)
    print(f"built {proj} · {total:.1f}s · layouts:", [sc["style"] for sc in scenes], "· 3D:", [(w["shape"], w["cam"]) for w in windows])

if __name__ == "__main__":
    data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    build(data, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
