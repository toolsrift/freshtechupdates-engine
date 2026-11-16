"""freshtechupdates illustration library v2.

Every scene is an animated SVG (viewBox 0 0 1080 640) built from extruded "3D sticker" shapes,
gloss highlights, a lit stage (backdrop disc, rotating rings, floating particles, ground shadow)
and simple characters. Styling comes from CSS classes, so one scene renders in three families:
  flat (filled colours + depth), ink (comic: black outlines), line (blueprint: line drawing).
Scene signature: fn(p, a, d, st) -> (svg, js)   p = id prefix, a = start time, d = duration,
st = "paper" (flat) | "comic" (ink) | "blueprint" (line).
"""
import math, re

def T(x): return f"{x:.3f}"
def rep(d, per): return max(1, int(d / per))

def _h():  # lazy import (styreel imports this module)
    import styreel
    return styreel

# ------------------------------------------------------------------ primitives ({c} = class slot)
def R(x, y, w, h, rx=0, c="{c}", extra=""): return f'<rect class="{c}" pathLength="1" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}"{extra}/>'
def C(cx, cy, r, c="{c}", extra=""): return f'<circle class="{c}" pathLength="1" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"{extra}/>'
def EL(cx, cy, rx, ry, c="{c}", extra=""): return f'<ellipse class="{c}" pathLength="1" cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"{extra}/>'
def P(d, c="{c}", extra=""): return f'<path class="{c}" pathLength="1" d="{d}"{extra}/>'
def L(x1, y1, x2, y2, c="ln", extra=""): return f'<line class="{c} d" pathLength="1" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{extra}/>'
def TX(x, y, s, size=60, c="tx", anchor="middle", extra=""): return f'<text class="{c}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" style="font-size:{size}px"{extra}>{s}</text>'

def slab(tpl, n, depth=12, steps=4):
    """Extruded shape: dark copies stacked down-right, then the lit front face. n = 1..5 or 'dk'."""
    out = []
    for k in range(steps, 0, -1):
        o = depth * k / steps
        out.append(f'<g transform="translate({o*.7:.1f} {o:.1f})">{tpl.replace("{c}", f"k{n} {"kd" if k == steps else "km"}")}</g>')
    out.append(tpl.replace("{c}", f"f{n} d"))
    return "".join(out)

def flat(tpl, cls): return tpl.replace("{c}", cls)
def hi(tpl): return tpl.replace("{c}", "hi")

def stage(p, cx=540, cy=300, r=255, gy=590, gw=320):
    pts = [(-1.15, -.55, 0), (1.12, -.62, 1), (-1.25, .25, 2), (1.22, .3, 1), (-.7, -1.0, 2), (.75, -.98, 0), (-1.0, .85, 1), (1.05, .8, 2)]
    parts = ""
    for k, (fx, fy, kind) in enumerate(pts):
        x, y = cx + fx * r, cy + fy * r * .9
        if kind == 0: sh = C(x, y, 9, "pt")
        elif kind == 1: sh = P(f"M{x-12:.0f},{y:.0f} L{x+12:.0f},{y:.0f} M{x:.0f},{y-12:.0f} L{x:.0f},{y+12:.0f}", "ptl")
        else: sh = P(f"M{x:.0f},{y-14:.0f} L{x+5:.0f},{y-4:.0f} L{x+15:.0f},{y:.0f} L{x+5:.0f},{y+4:.0f} L{x:.0f},{y+14:.0f} L{x-5:.0f},{y+4:.0f} L{x-15:.0f},{y:.0f} L{x-5:.0f},{y-4:.0f} Z", "pt")
        parts += f'<g id="{p}-pt{k}">{sh}</g>'
    svg = (EL(cx, gy, gw, 24, "gs") + C(cx, cy, r, "bd", f' id="{p}-bd"') +
           f'<g id="{p}-rg1">{C(cx, cy, r * 1.12, "rg")}</g><g id="{p}-rg2">{C(cx, cy, r * .82, "rg rg2")}</g>' + parts)
    return svg

def stage_js(p, a, d, cx=540, cy=300):
    js = [f'tl.fromTo("#{p}-bd",{{scale:0,svgOrigin:"{cx} {cy}"}},{{scale:1,duration:.6,ease:"back.out(1.6)"}},{T(a)})',
          f'tl.fromTo("#{p}-rg1",{{rotation:0,svgOrigin:"{cx} {cy}"}},{{rotation:90,duration:{T(d)},ease:"none"}},{T(a)})',
          f'tl.fromTo("#{p}-rg2",{{rotation:0,svgOrigin:"{cx} {cy}"}},{{rotation:-120,duration:{T(d)},ease:"none"}},{T(a)})']
    for k in range(8):
        js.append(f'tl.fromTo("#{p}-pt{k}",{{y:0,opacity:0}},{{y:{-14 if k % 2 else 14},opacity:1,duration:{1.4 + (k % 3) * .3:.2f},ease:"sine.inOut",repeat:{rep(d, 1.5)},yoyo:true}},{T(a + .3 + k * .07)})')
    return js

def person(p, x, y, s=1.0, shirt=2, hair="hr", flip=False):
    """Rounded character standing at foot point (x, y). Ids: {p}-g (whole), {p}-arm (right arm)."""
    f = -1 if flip else 1
    return (f'<g id="{p}-g"><g transform="translate({x} {y}) scale({s*f} {s})">'
            + L(-58, -140, -84, -60, "lnS") + flat(C(-84, -60, 14), "sk")
            + slab(P("M-62,0 L-58,-120 Q-56,-170 0,-172 Q56,-170 58,-120 L62,0 Z"), shirt, 8, 3)
            + flat(R(-14, -196, 28, 30, 8), "sk d") + flat(C(0, -238, 52), "sk d")
            + flat(P("M-54,-240 Q-56,-300 0,-298 Q56,-300 54,-240 Q40,-268 0,-266 Q-40,-268 -54,-240 Z"), f"{hair} d")
            + flat(C(-18, -236, 6), "eye") + flat(C(18, -236, 6), "eye") + flat(P("M-14,-212 Q0,-202 14,-212"), "lnE d")
            + f'<g id="{p}-arm">{L(58, -140, 96, -70, "lnS")}{flat(C(96, -70, 14), "sk")}</g></g></g>')

def sfx(p, x, y, word, st): return _h().sfx_svg(p, x, y, word, st)
def ent(st, gids, t, stg=.08): return _h().ent(st, gids, t, stg)
def sfxjs(p, t, st): return _h().sfx_js(p, t, st)
def bob(sel, a, d, amp=10, per=1.2, origin=None):
    return f'tl.fromTo("{sel}",{{y:0}},{{y:{-amp},duration:{per/2:.2f},ease:"sine.inOut",repeat:{rep(d, per/2)},yoyo:true}},{T(a)})'

# ------------------------------------------------------------------ scenes
def sc_rocket(p, a, d, st):
    bars = "".join(f'<g id="{p}-b{k}">{slab(R(110 + k*70, 560 - h, 50, h, 8), 1 if k % 2 else 4, 10, 3)}</g>' for k, h in enumerate((90, 150, 120, 210)))
    rocket = (f'<g id="{p}-rk"><g transform="translate(600 300) rotate(18)">'
              f'<path id="{p}-fl" class="flame" d="M-34,118 Q0,250 34,118 Z"/><path class="flame2" d="M-18,118 Q0,200 18,118 Z"/>'
              + slab(P("M-52,-60 L-96,96 L-48,84 Z"), 2, 10, 3) + slab(P("M52,-60 L96,96 L48,84 Z"), 2, 10, 3)
              + slab(P("M0,-200 C62,-140 66,40 52,118 L-52,118 C-66,40 -62,-140 0,-200 Z"), 3, 14, 4)
              + flat(P("M0,-200 C30,-172 46,-130 54,-96 L-54,-96 C-46,-130 -30,-172 0,-200 Z"), "f2 d")
              + slab(C(0, -20, 34), "dk", 6, 2) + flat(C(0, -20, 24), "f1 d") + hi(P("M-14,-34 Q-4,-44 10,-38"))
              + hi(P("M-34,-80 C-40,-20 -38,40 -32,100 L-24,100 C-28,40 -30,-20 -24,-80 Z"))
              + '</g></g>')
    smoke = "".join(f'<g id="{p}-sm{k}">{flat(C(560 + dx, 470 + dy, 34), "f3 d")}</g>' for k, (dx, dy) in enumerate(((0, 0), (-50, 25), (50, 22), (-20, 45), (30, 48))))
    svg = stage(p) + bars + smoke + rocket + sfx(p, 860, 110, "LIFT-OFF!", st)
    js = stage_js(p, a, d) + [f'tl.fromTo("#{p}-b{k}",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:.5,ease:"back.out(1.7)"}},{T(a+.3+k*.1)})' for k in range(4)]
    js += ent(st, [f"{p}-rk"], a + .5)
    lt = a + min(2.0, d * .3)
    js += [f'tl.fromTo("#{p}-fl",{{scaleY:.7,transformOrigin:"50% 0%"}},{{scaleY:1.3,duration:.08,ease:"none",repeat:{rep(d, .08)},yoyo:true}},{T(a+.6)})',
           f'tl.to("#{p}-rk",{{x:-6,duration:.05,repeat:7,yoyo:true}},{T(lt-.45)})',
           f'tl.to("#{p}-rk",{{x:70,y:-110,duration:1.2,ease:"power2.inOut"}},{T(lt)})',
           bob(f"#{p}-rk", lt + 1.2, d - (lt - a) - 1.2, 12, 1.4)]
    for k in range(5):
        js.append(f'tl.fromTo("#{p}-sm{k}",{{scale:.2,opacity:1,transformOrigin:"50% 50%"}},{{scale:1.6,opacity:0,duration:1.3,ease:"power2.out",repeat:{rep(d, 1.6)},repeatDelay:.3}},{T(lt-.4+k*.12)})')
    return svg, js + sfxjs(p, lt + .2, st)

def sc_robot(p, a, d, st):
    robot = (f'<g id="{p}-rob"><g transform="translate(730 560)">'
             + slab(R(-34, -40, 26, 40, 8), "dk", 6, 2) + slab(R(8, -40, 26, 40, 8), "dk", 6, 2)
             + slab(R(-80, -210, 160, 172, 34), 2, 12, 4) + slab(C(0, -128, 26), 4, 4, 2) + hi(R(-62, -196, 18, 120, 9))
             + f'<g id="{p}-rarm"><line class="ln d" pathLength="1" x1="80" y1="-180" x2="128" y2="-110"/>{flat(C(128, -110, 18), "f4 d")}</g>'
             + '<line class="ln d" pathLength="1" x1="-80" y1="-180" x2="-118" y2="-110"/>' + flat(C(-118, -110, 18), "f4 d")
             + slab(R(-96, -372, 192, 150, 40), 1, 12, 4) + flat(R(-74, -350, 148, 98, 26), "dk d")
             + f'<g id="{p}-eyes">{flat(EL(-30, -300, 15, 18), "eyeG")}{flat(EL(30, -300, 15, 18), "eyeG")}</g>'
             + flat(P("M-22,-268 Q0,-254 22,-268"), "lnA d") + hi(R(-80, -362, 70, 14, 7))
             + '<line class="ln d" pathLength="1" x1="0" y1="-372" x2="0" y2="-410"/>' + f'<g id="{p}-ant">{flat(C(0, -420, 14), "f4 d")}</g>'
             + '</g></g>')
    holo = (f'<g id="{p}-holo">{flat(R(390, 120, 170, 120, 16), "scr d")}'
            + "".join(L(410, 150 + j * 26, 410 + (130 if j != 2 else 80), 150 + j * 26, "lnT") for j in range(4)) + '</g>')
    svg = stage(p) + person(p + "h", 290, 580, 1.0, 5) + holo + robot + sfx(p, 540, 70, "WATCH & LEARN", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}h-g", f"{p}-rob"], a + .3, .2)
    js.append(f'tl.fromTo("#{p}-holo",{{opacity:0,scale:.3,transformOrigin:"50% 100%"}},{{opacity:1,scale:1,duration:.5,ease:"back.out(2)"}},{T(a+1.0)})')
    for k in range(rep(d - 1.5, .9)):
        up = k % 2 == 0
        js.append(f'tl.to("#{p}h-arm",{{rotation:{-70 if up else 0},svgOrigin:"348 440",duration:.35,ease:"sine.inOut"}},{T(a+1.2+k*.9)})')
        js.append(f'tl.to("#{p}-rarm",{{rotation:{-70 if up else 0},svgOrigin:"810 380",duration:.35,ease:"sine.inOut"}},{T(a+1.6+k*.9)})')
    js += [f'tl.fromTo("#{p}-eyes",{{scaleY:1,transformOrigin:"50% 50%"}},{{scaleY:.1,duration:.07,repeat:{rep(d, 2.4)*2-1},yoyo:true,repeatDelay:2.3}},{T(a+1.5)})',
           f'tl.fromTo("#{p}-ant",{{scale:1,transformOrigin:"50% 50%"}},{{scale:1.4,duration:.3,repeat:{rep(d, .6)},yoyo:true}},{T(a+.8)})',
           bob(f"#{p}-holo", a + 1.5, d - 1.5, 8, 1.6)]
    return svg, js + sfxjs(p, a + 1.0, st)

def sc_shield(p, a, d, st):
    shield = (f'<g id="{p}-sh"><g transform="translate(460 310)">'
              + slab(P("M0,-200 Q110,-178 172,-160 L172,14 Q158,134 0,214 Q-158,134 -172,14 L-172,-160 Q-110,-178 0,-200 Z"), 1, 16, 4)
              + flat(P("M0,-160 Q84,-144 132,-130 L132,10 Q120,104 0,168 Q-120,104 -132,10 L-132,-130 Q-84,-144 0,-160 Z"), "f3 d")
              + slab(R(-56, -22, 112, 90, 18), 4, 8, 3)
              + f'<path id="{p}-shk" class="lnD d" pathLength="1" d="M-34,-22 L-34,-60 Q-34,-100 0,-100 Q34,-100 34,-60 L34,-22"/>'
              + flat(C(0, 16, 12), "dk") + flat(R(-5, 16, 10, 28, 4), "dk")
              + hi(P("M-140,-120 Q-90,-140 -40,-148 L-44,-120 Q-90,-112 -120,-100 Z")) + '</g></g>')
    hacker = (f'<g id="{p}-hk"><g transform="translate(900 580)">'
              + slab(P("M-90,0 L-80,-130 Q-70,-210 0,-214 Q70,-210 80,-130 L90,0 Z"), "dk", 8, 3)
              + flat(P("M-70,-150 Q-70,-250 0,-252 Q70,-250 70,-150 Q60,-120 0,-118 Q-60,-120 -70,-150 Z"), "dk d")
              + flat(EL(0, -176, 40, 34), "void") + flat(C(-14, -180, 6), "f2") + flat(C(14, -180, 6), "f2")
              + slab(R(-70, -90, 140, 80, 10), 5, 6, 2) + '</g></g>')
    bugs = "".join(f'<g id="{p}-bug{k}" transform="translate(800 420)"><g>{flat(EL(0, 0, 18, 22), "f2 d")}{flat(C(0, -24, 11), "f2 d")}'
                   + "".join(f'<line class="lnB" x1="{s*14}" y1="{yy}" x2="{s*30}" y2="{yy+6}"/>' for yy in (-8, 4, 14) for s in (-1, 1)) + '</g></g>' for k in range(4))
    rings = "".join(f'<circle id="{p}-rp{k}" class="rp" cx="630" cy="{330 + k * 10}" r="40" opacity="0"/>' for k in range(2))
    svg = stage(p, 520) + hacker + bugs + rings + shield + sfx(p, 260, 80, "BLOCKED!", st)
    js = stage_js(p, a, d, 520) + ent(st, [f"{p}-sh", f"{p}-hk"], a + .3, .2)
    for k in range(min(8, rep(d - 1.6, 1.1))):
        b = k % 4; t0 = a + 1.4 + k * 1.1; yy = 300 + (k % 3) * 60
        js.append(f'tl.fromTo("#{p}-bug{b}",{{x:820,y:470,scale:.6,opacity:1,rotation:0}},{{x:650,y:{yy},scale:1,rotation:-90,duration:.55,ease:"power2.in"}},{T(t0)})')
        js.append(f'tl.to("#{p}-bug{b}",{{x:{760 + (k%2)*80},y:{yy+200},rotation:-300,opacity:0,duration:.6,ease:"power2.out"}},{T(t0+.55)})')
        js.append(f'tl.fromTo("#{p}-rp{k%2}",{{opacity:1,scale:.4,transformOrigin:"50% 50%"}},{{opacity:0,scale:2.4,duration:.6}},{T(t0+.55)})')
        js.append(f'tl.fromTo("#{p}-sh",{{x:0}},{{x:-8,duration:.05,repeat:3,yoyo:true}},{T(t0+.55)})')
    js += [f'tl.fromTo("#{p}-shk",{{y:-26}},{{y:0,duration:.3,ease:"bounce.out"}},{T(a+1.1)})', bob(f"#{p}-hk", a + 1, d - 1, 5, 1.0)]
    return svg, js + sfxjs(p, a + 2.0, st)

def sc_phone(p, a, d, st):
    tiles = "".join(f'<g id="{p}-t{k}">{flat(R(472 + (k % 3) * 52, 190 + (k // 3) * 56, 40, 40, 11), f"f{(1, 2, 4, 5, 1, 4, 2, 5, 1)[k]} d")}</g>' for k in range(9))
    phone = (f'<g id="{p}-ph">' + slab(R(440, 80, 200, 400, 38), "dk", 16, 4) + flat(R(456, 100, 168, 360, 26), "scr2 d")
             + flat(R(510, 108, 60, 14, 7), "dk") + tiles + flat(R(472, 370, 136, 60, 14), "f3 d")
             + flat(L(488, 392, 590, 392, "lnE"), "lnE d") + flat(L(488, 410, 560, 410, "lnE"), "lnE d")
             + hi(P("M456,140 L520,100 L548,100 L456,190 Z")) + '</g>')
    watch = (f'<g id="{p}-wt">' + slab(R(196, 200, 60, 260, 24), 5, 8, 3) + slab(R(170, 250, 112, 130, 30), "dk", 10, 3)
             + flat(R(182, 262, 88, 106, 22), "f1 d") + f'<path id="{p}-hr" class="lnE d" pathLength="1" d="M196,318 L216,318 L226,296 L238,340 L248,318 L258,318"/></g>')
    buds = (f'<g id="{p}-bd2">' + slab(R(800, 300, 150, 120, 46), 3, 10, 3) + flat(L(875, 300, 875, 420, "lnT"), "lnT d")
            + slab(C(838, 260, 26), 3, 6, 2) + slab(C(912, 260, 26), 3, 6, 2) + '</g>')
    notes = "".join(f'<g id="{p}-n{k}">{slab(R(660, 120 + k * 70, 150, 52, 16), (4, 1, 2)[k], 6, 2)}{flat(L(682, 140 + k*70, 780, 140 + k*70, "lnE"), "lnE d")}</g>' for k in range(3))
    svg = stage(p) + watch + buds + phone + notes + sfx(p, 540, 590, "NEW DROP!", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-ph", f"{p}-wt", f"{p}-bd2"], a + .3, .15)
    js.append(f'tl.fromTo("#{p}-ph",{{rotation:-6,svgOrigin:"540 280"}},{{rotation:4,duration:{T(d)},ease:"sine.inOut"}},{T(a)})')
    for k in range(9):
        js.append(f'tl.fromTo("#{p}-t{k}",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,duration:.3,ease:"back.out(3)"}},{T(a+.9+k*.06)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-n{k}",{{opacity:0,x:-60,scale:.6,transformOrigin:"0% 50%"}},{{opacity:1,x:0,scale:1,duration:.4,ease:"back.out(2)"}},{T(a+1.6+k*.6)})')
    js += [f'tl.fromTo("#{p}-hr",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.8,repeat:{rep(d, 1.2)},repeatDelay:.4,ease:"none"}},{T(a+1)})',
           bob(f"#{p}-bd2", a + 1, d - 1, 10, 1.3), bob(f"#{p}-wt", a + 1.2, d - 1.2, 8, 1.7)]
    return svg, js + sfxjs(p, a + 1.5, st)

def rack(p, k, x, y, h=230, w=120, n=1):
    leds = "".join(f'<g id="{p}-led{k}{j}">{flat(C(x + w - 24, y + 30 + j * 46, 7), "f4")}</g>' for j in range(int(h / 46)))
    slots = "".join(flat(R(x + 14, y + 18 + j * 46, w - 50, 24, 6), "f3 d") for j in range(int(h / 46)))
    return slab(R(x, y, w, h, 14), "dk", 12, 4) + slots + leds

def sc_bolt(p, a, d, st):
    racks = "".join(rack(p, k, 150 + k * 140, 330, 230) for k in range(2))
    batt = (f'<g id="{p}-bt">' + slab(R(620, 160, 200, 380, 34), 3, 16, 4) + slab(R(680, 130, 80, 34, 10), 3, 6, 2)
            + flat(R(640, 180, 160, 340, 22), "dk d") + f'<rect id="{p}-lv" class="f4" x="652" y="192" width="136" height="316" rx="14"/>'
            + hi(R(636, 176, 22, 300, 11)) + '</g>')
    bolt = f'<g id="{p}-bolt">{slab(P("M748,210 L668,350 L716,350 L690,470 L780,320 L730,320 Z"), 1, 8, 3)}</g>'
    cable = '<path id="{p}-cb" class="beam" d="M410,450 C480,450 520,520 620,500"/>'.replace("{p}", p)
    svg = stage(p, 520) + racks + cable + batt + bolt + sfx(p, 300, 120, "POWER UP!", st)
    js = stage_js(p, a, d, 520) + ent(st, [f"{p}-bt"], a + .3)
    js += [f'tl.fromTo("#{p}-lv",{{scaleY:.08,transformOrigin:"50% 100%"}},{{scaleY:1,duration:{T(min(4, d*.5))},ease:"power1.inOut"}},{T(a+.8)})',
           f'tl.fromTo("#{p}-bolt",{{scale:0,svgOrigin:"724 340"}},{{scale:1,duration:.4,ease:"back.out(3)"}},{T(a+1.0)})',
           f'tl.to("#{p}-bolt",{{scale:1.12,svgOrigin:"724 340",duration:.3,repeat:{rep(d, .6)},yoyo:true,ease:"sine.inOut"}},{T(a+1.5)})',
           f'tl.fromTo("#{p}-cb",{{strokeDashoffset:0}},{{strokeDashoffset:-200,duration:{T(d)},ease:"none"}},{T(a)})']
    for k in range(2):
        for j in range(5):
            js.append(f'tl.fromTo("#{p}-led{k}{j}",{{opacity:1}},{{opacity:.15,duration:.16,repeat:{rep(d, .5)},yoyo:true,repeatDelay:{.1 + ((k*5+j) % 4) * .07:.2f}}},{T(a+.5+(k+j)*.06)})')
    return svg, js + sfxjs(p, a + 1.3, st)

def sc_chip(p, a, d, st):
    pins = "".join(L(x1, y1, x2, y2, "lnT") for k in range(6) for (x1, y1, x2, y2) in
                   ((430 + k * 44, 170, 430 + k * 44, 136), (430 + k * 44, 470, 430 + k * 44, 504), (380, 210 + k * 44, 346, 210 + k * 44), (700, 210 + k * 44, 734, 210 + k * 44)))
    tr = [((734, 254), (840, 254), (880, 160), (990, 160)), ((734, 386), (860, 386), (900, 470), (1000, 470)), ((346, 254), (230, 254), (190, 150), (90, 150)),
          ((346, 386), (220, 386), (180, 480), (80, 480)), ((540, 504), (540, 570), (680, 600)), ((474, 136), (474, 60), (330, 40))]
    traces = "".join(f'<polyline id="{p}-tr{k}" class="lnA" pathLength="1" style="stroke-dasharray:1 1" points="{" ".join(f"{x},{y}" for x, y in t)}"/>'
                     f'<g id="{p}-te{k}">{flat(C(t[-1][0], t[-1][1], 13), "f4 d")}</g>' for k, t in enumerate(tr))
    pulses = "".join(f'<circle id="{p}-pu{k}" class="pulse" cx="{tr[k][0][0]}" cy="{tr[k][0][1]}" r="9"/>' for k in range(len(tr)))
    chip = (f'<g id="{p}-ch">{pins}' + slab(R(380, 170, 320, 300, 36), "dk", 18, 5) + flat(R(400, 190, 280, 260, 26), "k1 d")
            + f'<g id="{p}-core">{slab(R(460, 240, 160, 160, 24), 1, 8, 3)}{hi(R(470, 250, 140, 26, 13))}</g>'
            + TX(540, 345, "AI", 76, "tx2") + '</g>')
    glow = f'<circle id="{p}-gl" class="glow" cx="540" cy="320" r="120"/>'
    svg = stage(p) + traces + pulses + glow + chip + sfx(p, 820, 590, "NEW MODEL!", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-ch"], a + .3)
    for k, t in enumerate(tr):
        js.append(f'tl.fromTo("#{p}-tr{k}",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.6,ease:"power2.out"}},{T(a+.8+k*.1)})')
        js.append(f'tl.fromTo("#{p}-te{k}",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,duration:.3,ease:"back.out(3)"}},{T(a+1.3+k*.1)})')
        seg = " ".join(f'tl.to("#{p}-pu{k}",{{attr:{{cx:{x},cy:{y}}},duration:{.9/(len(t)-1):.2f},ease:"none"}},{T(a+1.6+k*.25+j*.9/(len(t)-1))});' for j, (x, y) in enumerate(t[1:]))
        js.append(seg)
        js.append(f'tl.fromTo("#{p}-pu{k}",{{opacity:0}},{{opacity:1,duration:.1}},{T(a+1.6+k*.25)})')
        js.append(f'tl.to("#{p}-pu{k}",{{opacity:0,duration:.2}},{T(a+2.5+k*.25)})')
    js += [f'tl.fromTo("#{p}-gl",{{scale:.8,opacity:.3,transformOrigin:"50% 50%"}},{{scale:1.25,opacity:.7,duration:.8,repeat:{rep(d, .8)},yoyo:true,ease:"sine.inOut"}},{T(a+.9)})',
           f'tl.fromTo("#{p}-core",{{scale:1,svgOrigin:"540 320"}},{{scale:1.06,duration:.5,repeat:{rep(d, .5)},yoyo:true}},{T(a+1.2)})']
    return svg, js + sfxjs(p, a + 1.4, st)

def sc_globe(p, a, d, st):
    cont = ('M-120,-60 Q-80,-120 -20,-100 Q10,-60 -30,-30 Q-60,0 -100,-10 Z M30,-120 Q90,-130 120,-80 Q100,-40 60,-50 Q30,-80 30,-120 Z '
            'M-60,40 Q0,20 40,60 Q30,120 -20,130 Q-70,100 -60,40 Z M80,20 Q130,30 140,80 Q110,110 80,80 Z')
    globe = (f'<defs><clipPath id="{p}-clip"><circle cx="540" cy="300" r="190"/></clipPath></defs>'
             f'<g id="{p}-gb">' + slab(C(540, 300, 190), "k1", 14, 4) + flat(C(540, 300, 190), "f1 d")
             + f'<g clip-path="url(#{p}-clip)"><g id="{p}-ct" transform="translate(540 300)">{flat(P(cont), "f4 d")}<g transform="translate(-400 0)">{flat(P(cont), "f4 d")}</g></g></g>'
             + "".join(EL(540, 300, rx, 190, "lnT", ' style="opacity:.5"') for rx in (70, 140))
             + "".join(L(540 - math.sqrt(190**2 - y**2), 300 + y, 540 + math.sqrt(190**2 - y**2), 300 + y, "lnT", ' style="opacity:.5"') for y in (-110, 0, 110))
             + hi(P("M400,200 Q440,140 520,122 Q470,160 440,220 Z")) + '</g>')
    pins = "".join(f'<g id="{p}-pn{k}">{slab(P(f"M{x},{y} C{x-30},{y-36} {x-24},{y-74} {x},{y-74} C{x+24},{y-74} {x+30},{y-36} {x},{y} Z"), 2, 5, 2)}{flat(C(x, y - 48, 10), "f3")}</g>'
                   for k, (x, y) in enumerate(((470, 250), (610, 300), (520, 410), (650, 200))))
    orbit = EL(540, 300, 320, 90, "lnA", ' style="opacity:.8"')
    plane = f'<g id="{p}-pl"><g transform="translate(860 300)">{slab(P("M-30,0 L24,-12 Q36,0 24,12 Z M-6,-4 L-20,-30 L-8,-30 L10,-6 Z M-6,4 L-20,30 L-8,30 L10,6 Z"), 3, 4, 2)}</g></g>'
    svg = stage(p) + orbit + globe + pins + plane + sfx(p, 540, 590, "WORLDWIDE", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-gb"], a + .3)
    js.append(f'tl.fromTo("#{p}-ct",{{x:540}},{{x:940,duration:{T(d)},ease:"none"}},{T(a)})')
    for k in range(4):
        js.append(f'tl.fromTo("#{p}-pn{k}",{{scale:0,y:-50,transformOrigin:"50% 100%"}},{{scale:1,y:0,duration:.5,ease:"bounce.out"}},{T(a+1.0+k*.3)})')
    n = 24; per = max(.1, (d - .5) / n)
    for k in range(1, n + 1):
        t = 2 * math.pi * k / n; x, y = 320 * math.cos(t) - 320, 90 * math.sin(t)
        js.append(f'tl.to("#{p}-pl",{{x:{x:.0f},y:{y:.0f},rotation:{math.degrees(math.atan2(90*math.cos(t), -320*math.sin(t))):.0f},transformOrigin:"50% 50%",duration:{per:.2f},ease:"none"}},{T(a+.3+(k-1)*per)})')
    return svg, js + sfxjs(p, a + 1.6, st)

def sc_chat(p, a, d, st):
    lap = (f'<g id="{p}-lp">' + slab(R(300, 90, 480, 320, 24), "dk", 14, 4) + flat(R(320, 110, 440, 280, 14), "scr2 d")
           + slab(P("M240,420 L840,420 L800,470 L280,470 Z"), "dk", 10, 3) + hi(P("M320,110 L420,110 L320,220 Z")) + '</g>')
    bub = [(350, 140, 230, 1, False), (520, 210, 210, 2, True), (350, 280, 260, 1, False)]
    bubbles = "".join(f'<g id="{p}-b{k}">{slab(R(x, y, w, 52, 22), c, 6, 2)}{flat(L(x+22, y+20, x+w-60, y+20, "lnE"), "lnE d")}{flat(L(x+22, y+34, x+w-110, y+34, "lnE"), "lnE d")}</g>'
                      for k, (x, y, w, c, r) in enumerate(bub))
    dots = "".join(f'<g id="{p}-td{k}">{flat(C(560 + k * 30, 365, 9), "f4")}</g>' for k in range(3))
    star = f'<g id="{p}-st"><g transform="translate(840 150)">{slab(P("M0,-60 L14,-14 L60,0 L14,14 L0,60 L-14,14 L-60,0 L-14,-14 Z"), 4, 8, 3)}</g></g>'
    floaty = "".join(f'<g id="{p}-fb{k}">{slab(R(x, y, 110, 70, 26), c, 8, 3)}{flat(C(x + 34, y + 35, 7), "dkf")}{flat(C(x + 56, y + 35, 7), "dkf")}{flat(C(x + 78, y + 35, 7), "dkf")}</g>'
                     for k, (x, y, c) in enumerate(((120, 200, 5), (880, 330, 1))))
    svg = stage(p) + floaty + lap + bubbles + dots + star + sfx(p, 200, 580, "AI CHAT", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-lp"], a + .3)
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-b{k}",{{opacity:0,scale:.3,transformOrigin:"{"0% 100%" if k != 1 else "100% 100%"}"}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2.2)"}},{T(a+.9+k*.8)})')
        js.append(f'tl.fromTo("#{p}-td{k}",{{y:0}},{{y:-14,duration:.24,repeat:{rep(d, .48)},yoyo:true,ease:"sine.inOut"}},{T(a+.6+k*.1)})')
    js += [f'tl.fromTo("#{p}-st",{{rotation:0,scale:0,svgOrigin:"840 150"}},{{rotation:360,scale:1,duration:.8,ease:"back.out(1.5)"}},{T(a+.7)})',
           f'tl.to("#{p}-st",{{rotation:450,svgOrigin:"840 150",duration:{T(d-1.5)},ease:"none"}},{T(a+1.5)})',
           bob(f"#{p}-fb0", a + .6, d - .6, 14, 1.6), bob(f"#{p}-fb1", a + .9, d - .9, 12, 1.9)]
    js += ent(st, [f"{p}-fb0", f"{p}-fb1"], a + .5, .2)
    return svg, js + sfxjs(p, a + 1.2, st)

def sc_cloud(p, a, d, st):
    cloud = f'<g id="{p}-cl">{slab(P("M330,250 C240,250 228,140 318,130 C326,50 460,26 504,96 C548,18 712,30 720,128 C820,118 840,250 742,250 Z"), 3, 14, 4)}{hi(P("M330,230 C280,226 270,160 320,150 C300,180 310,210 340,220 Z"))}</g>'
    racks = "".join(f'<g id="{p}-rk{k}">{rack(p, k, 300 + k * 170, 360, 200, 120)}</g>' for k in range(3))
    wires = "".join(f'<path class="beam" id="{p}-w{k}" d="M{360 + k*170},252 L{360 + k*170},360"/>' for k in range(3))
    pk = "".join(f'<g id="{p}-pk{k}">{slab(R(346 + k*170, 330, 28, 28, 6), (1, 4, 2)[k], 4, 2)}</g>' for k in range(3))
    svg = stage(p, 540, 330) + wires + racks + pk + cloud + sfx(p, 880, 100, "THE CLOUD", st)
    js = stage_js(p, a, d, 540, 330) + ent(st, [f"{p}-cl", f"{p}-rk0", f"{p}-rk1", f"{p}-rk2"], a + .3, .12)
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-pk{k}",{{y:0,opacity:1}},{{y:-90,opacity:.2,duration:.8,repeat:{rep(d, .8)},ease:"power1.in"}},{T(a+1+k*.25)})')
        js.append(f'tl.fromTo("#{p}-w{k}",{{strokeDashoffset:0}},{{strokeDashoffset:-120,duration:{T(d)},ease:"none"}},{T(a)})')
        for j in range(4):
            js.append(f'tl.fromTo("#{p}-led{k}{j}",{{opacity:1}},{{opacity:.15,duration:.18,repeat:{rep(d, .5)},yoyo:true,repeatDelay:{.1+((k*4+j)%4)*.08:.2f}}},{T(a+.6+(k+j)*.07)})')
    js.append(bob(f"#{p}-cl", a + 1, d - 1, 10, 2.0))
    return svg, js + sfxjs(p, a + 1.0, st)

def sc_car(p, a, d, st):
    city = "".join(slab(R(80 + k * 125, 400 - h, 96, h, 8), (2, 5, 1, 2, 5, 1, 2, 5)[k], 8, 2)
                   + "".join(flat(R(96 + k * 125 + (j % 2) * 36, 418 - h + (j // 2) * 40, 22, 22, 4), "win") for j in range(min(6, int(h / 40) * 2)))
                   for k, h in enumerate((160, 240, 130, 270, 190, 150, 220, 180)))
    road = flat(R(0, 470, 1080, 120, 0), "road d") + f'<g id="{p}-ln">' + "".join(flat(R(k * 160, 524, 90, 12, 6), "f3") for k in range(9)) + '</g>'
    car = (f'<g id="{p}-car">' + slab(P("M250,470 L290,390 Q320,346 400,344 L600,344 Q660,346 700,400 L790,420 Q830,430 832,470 L832,500 L250,500 Z"), 1, 12, 4)
           + flat(P("M330,402 L364,366 L478,366 L478,404 Z"), "f3 d") + flat(P("M500,366 L590,366 Q622,370 650,404 L500,404 Z"), "f3 d")
           + hi(P("M300,400 Q330,360 400,356 L420,356 Q350,370 320,410 Z")) + flat(R(806, 444, 26, 18, 6), "f4")
           + f'<g id="{p}-ld">{slab(R(460, 318, 70, 30, 12), 4, 4, 2)}</g>'
           + "".join(f'<g transform="translate({x} 505)"><g id="{p}-wh{k}">{slab(C(0, 0, 46), "dk", 6, 2)}{flat(C(0, 0, 20), "f3")}'
                     f'<line class="lnT" x1="-30" y1="0" x2="30" y2="0"/><line class="lnT" x1="0" y1="-30" x2="0" y2="30"/></g></g>' for k, x in enumerate((360, 700))) + '</g>')
    waves = "".join(f'<path id="{p}-sw{k}" class="lnA" d="M{560 - 40 - k*50},{300 - k*30} Q495,{260 - k*44} {430 + 40 + k*50},{300 - k*30}" opacity="0"/>' for k in range(3))
    beam = f'<path id="{p}-bm" class="beamf" d="M832,452 L1080,400 L1080,520 Z"/>'
    svg = (EL(540, 600, 400, 20, "gs") + city + road + beam + waves + car + sfx(p, 200, 90, "SELF-DRIVING", st))
    js = ent(st, [f"{p}-car"], a + .3) + [f'tl.fromTo("#{p}-ln",{{x:0}},{{x:-160,duration:.32,repeat:{rep(d, .32)},ease:"none"}},{T(a)})',
                                          bob(f"#{p}-car", a + .8, d - .8, 4, .36)]
    for k in range(2):
        js.append(f'tl.fromTo("#{p}-wh{k}",{{rotation:0}},{{rotation:{int(360 * d / .5)},duration:{T(d)},ease:"none",transformOrigin:"50% 50%"}},{T(a)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-sw{k}",{{opacity:0,scale:.6,transformOrigin:"50% 100%"}},{{opacity:1,scale:1,duration:.4,repeat:{rep(d, 1.2)},yoyo:true,repeatDelay:.4}},{T(a+1.0+k*.18)})')
    js.append(f'tl.fromTo("#{p}-bm",{{opacity:.15}},{{opacity:.5,duration:.6,repeat:{rep(d, .6)},yoyo:true}},{T(a+.6)})')
    return svg, js + sfxjs(p, a + 1.3, st)

def sc_money(p, a, d, st):
    bank = (f'<g id="{p}-bk">' + slab(P("M560,190 L760,110 L960,190 Z"), 2, 10, 3) + slab(R(580, 190, 360, 30, 6), 3, 6, 2)
            + "".join(slab(R(600 + k * 82, 230, 46, 220, 8), 3, 8, 3) for k in range(4)) + slab(R(560, 450, 400, 36, 6), 3, 8, 2)
            + TX(760, 176, "$", 54, "tx2") + '</g>')
    coins = "".join(f'<g id="{p}-c{k}">{slab(EL(230 + (k % 2) * 140, 520 - (k // 2) * 34, 70, 22), 4, 8, 3)}{TX(230 + (k % 2) * 140, 530 - (k // 2) * 34, "$", 26, "tx")}</g>' for k in range(8))
    bars = "".join(f'<g id="{p}-b{k}">{slab(R(430 + k * 40, 380 - h, 28, h, 6), 1, 6, 2)}</g>' for k, h in enumerate((40, 70, 110)))
    arrow = f'<g id="{p}-ar">{slab(P("M420,330 L520,230 L500,220 L560,200 L548,262 L532,244 L432,344 Z"), 5, 8, 3)}</g>'
    svg = stage(p, 560, 300) + bank + coins + bars + arrow + sfx(p, 300, 110, "BIG MONEY", st)
    js = stage_js(p, a, d, 560, 300) + ent(st, [f"{p}-bk"], a + .3)
    for k in range(8):
        js.append(f'tl.fromTo("#{p}-c{k}",{{y:-420,opacity:0}},{{y:0,opacity:1,duration:.6,ease:"bounce.out"}},{T(a+.8+k*.18)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-b{k}",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:.45,ease:"back.out(2)"}},{T(a+1.2+k*.15)})')
    js += [f'tl.fromTo("#{p}-ar",{{scale:0,transformOrigin:"0% 100%"}},{{scale:1,duration:.5,ease:"back.out(2.5)"}},{T(a+1.8)})',
           bob(f"#{p}-ar", a + 2.3, d - 2.3, 10, 1.2)]
    return svg, js + sfxjs(p, a + 2.0, st)

def sc_law(p, a, d, st):
    scales = (f'<g id="{p}-sc">' + slab(R(270, 470, 140, 30, 8), 5, 6, 2) + L(340, 470, 340, 170, "ln") + slab(C(340, 160, 16), 4, 4, 2)
              + f'<g id="{p}-beam">{L(220, 190, 460, 190, "ln")}'
              + L(220, 190, 190, 300, "lnT") + L(220, 190, 250, 300, "lnT") + slab(P("M170,300 L270,300 Q264,340 220,342 Q176,340 170,300 Z"), 4, 6, 2)
              + L(460, 190, 430, 300, "lnT") + L(460, 190, 490, 300, "lnT") + slab(P("M410,300 L510,300 Q504,340 460,342 Q416,340 410,300 Z"), 4, 6, 2) + '</g></g>')
    doc = (f'<g id="{p}-doc">' + slab(R(560, 150, 230, 300, 14), 3, 10, 3) + "".join(flat(L(590, 200 + j * 36, 760 - (j % 3) * 40, 200 + j * 36, "lnE"), "lnE d") for j in range(6))
           + f'<g id="{p}-stp"><g transform="rotate(-12 680 380)">{flat(R(600, 350, 170, 56, 10), "stamp")}{TX(685, 391, "RULING", 32, "stamptx")}</g></g></g>')
    gavel = (f'<g id="{p}-gv">' + slab(R(820, 470, 170, 36, 10), 5, 8, 2)
             + f'<g id="{p}-gh">{slab(R(880, 200, 26, 200, 10), 5, 6, 2)}{slab(R(820, 150, 150, 74, 20), 2, 10, 3)}{hi(R(830, 158, 130, 12, 6))}</g></g>')
    svg = stage(p) + scales + doc + gavel + sfx(p, 540, 590, "ORDER!", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-sc", f"{p}-doc", f"{p}-gv"], a + .3, .15)
    js.append(f'tl.fromTo("#{p}-beam",{{rotation:-8,svgOrigin:"340 190"}},{{rotation:8,duration:1.4,repeat:{rep(d, 1.4)},yoyo:true,ease:"sine.inOut"}},{T(a+.8)})')
    for k in range(min(6, rep(d - 1.5, 1.6))):
        t0 = a + 1.3 + k * 1.6
        js.append(f'tl.to("#{p}-gh",{{rotation:-28,svgOrigin:"893 400",duration:.3,ease:"power2.out"}},{T(t0)})')
        js.append(f'tl.to("#{p}-gh",{{rotation:6,svgOrigin:"893 400",duration:.12,ease:"power3.in"}},{T(t0+.35)})')
        js.append(f'tl.to("#{p}-gh",{{rotation:0,svgOrigin:"893 400",duration:.25,ease:"back.out(3)"}},{T(t0+.47)})')
    js.append(f'tl.fromTo("#{p}-stp",{{scale:2.5,opacity:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,duration:.25,ease:"power4.in"}},{T(a+1.8)})')
    return svg, js + sfxjs(p, a + 1.5, st)

def sc_media(p, a, d, st):
    frame = (f'<g id="{p}-fr">' + slab(R(330, 110, 420, 320, 20), "dk", 14, 4) + flat(R(350, 130, 380, 280, 10), "sky d")
             + f'<defs><clipPath id="{p}-cp"><rect x="350" y="130" width="380" height="280" rx="10"/></clipPath></defs><g clip-path="url(#{p}-cp)">'
             + f'<g id="{p}-sun">{flat(C(640, 230, 40), "f4 d")}</g>' + flat(P("M330,420 L450,250 L560,420 Z"), "f1 d") + flat(P("M480,420 L600,280 L760,420 Z"), "f2 d") + '</g>'
             + hi(P("M350,130 L460,130 L350,240 Z")) + '</g>')
    play = f'<g id="{p}-pl">{slab(C(540, 300, 56), 2, 8, 3)}{flat(P("M522,270 L572,300 L522,330 Z"), "f3 d")}</g>'
    film = f'<g id="{p}-fm">' + slab(R(780, 160, 120, 300, 10), "dk", 8, 3) + "".join(flat(R(792, 176 + j * 46, 16, 22, 4), "f3") + flat(R(872, 176 + j * 46, 16, 22, 4), "f3") for j in range(6)) + '</g>'
    brush = f'<g id="{p}-br"><g transform="rotate(-35 220 330)">{slab(R(200, 230, 34, 180, 12), 5, 6, 2)}{slab(R(196, 200, 42, 40, 6), 3, 4, 2)}{flat(P("M198,200 Q217,140 236,200 Z"), "f1 d")}</g></g>'
    sp = "".join(f'<g id="{p}-sp{k}">{flat(P(f"M{x},{y-18} L{x+6},{y-6} L{x+18},{y} L{x+6},{y+6} L{x},{y+18} L{x-6},{y+6} L{x-18},{y} L{x-6},{y-6} Z"), "f4 d")}</g>' for k, (x, y) in enumerate(((310, 110), (770, 120), (300, 460), (760, 470))))
    svg = stage(p) + film + brush + frame + play + sp + sfx(p, 540, 590, "CREATE!", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-fr", f"{p}-fm", f"{p}-br"], a + .3, .15)
    js += [f'tl.fromTo("#{p}-sun",{{y:150}},{{y:0,duration:1.2,ease:"power2.out"}},{T(a+.8)})',
           f'tl.fromTo("#{p}-pl",{{scale:0,svgOrigin:"540 300"}},{{scale:1,duration:.4,ease:"back.out(3)"}},{T(a+1.5)})',
           f'tl.to("#{p}-pl",{{scale:1.1,svgOrigin:"540 300",duration:.4,repeat:{rep(d, .8)},yoyo:true}},{T(a+2.0)})',
           f'tl.fromTo("#{p}-fm",{{y:0}},{{y:-46,duration:.5,repeat:{rep(d, .5)},ease:"none"}},{T(a+1)})',
           bob(f"#{p}-br", a + 1, d - 1, 12, 1.5)]
    for k in range(4):
        js.append(f'tl.fromTo("#{p}-sp{k}",{{scale:0,rotation:0,transformOrigin:"50% 50%"}},{{scale:1.2,rotation:90,duration:.5,repeat:{rep(d, 1.0)},yoyo:true}},{T(a+.6+k*.25)})')
    return svg, js + sfxjs(p, a + 1.2, st)

def sc_code(p, a, d, st):
    cols = [(1, 120), (2, 200), (4, 90), (1, 240), (5, 150), (2, 110), (4, 210)]
    lines = "".join(f'<g id="{p}-cl{k}">{flat(R(330 + (k in (2, 3, 5)) * 30, 160 + k * 36, w, 16, 8), f"f{c} d")}</g>' for k, (c, w) in enumerate(cols))
    ed = (f'<g id="{p}-ed">' + slab(R(300, 90, 440, 360, 22), "dk", 16, 4) + flat(R(300, 90, 440, 46, 22), "k1 d")
          + flat(C(330, 113, 8), "f2") + flat(C(356, 113, 8), "f4") + flat(C(382, 113, 8), "f1") + lines
          + f'<rect id="{p}-cur" class="f3" x="560" y="400" width="14" height="24"/>' + '</g>')
    tag = f'<g id="{p}-tag"><g transform="translate(850 220)">{slab(R(-90, -60, 180, 120, 30), 4, 10, 3)}{TX(0, 22, "&lt;/&gt;", 62, "tx2")}</g></g>'
    gear = (f'<g id="{p}-gr"><g transform="translate(210 400)">' + slab(P(" ".join(
        f"{'M' if k == 0 else 'L'}{(70 if k % 2 == 0 else 56) * math.cos(k * math.pi / 8):.0f},{(70 if k % 2 == 0 else 56) * math.sin(k * math.pi / 8):.0f}" for k in range(16)) + " Z"), 3, 8, 3)
            + flat(C(0, 0, 22), "dk") + '</g></g>')
    term = f'<g id="{p}-tm">{slab(R(760, 380, 200, 120, 16), "dk", 8, 3)}{TX(790, 450, "&gt;_", 44, "tx3", "start")}</g>'
    svg = stage(p) + gear + ed + tag + term + sfx(p, 540, 590, "SHIP IT!", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-ed", f"{p}-tag", f"{p}-gr", f"{p}-tm"], a + .3, .12)
    for k in range(len(cols)):
        js.append(f'tl.fromTo("#{p}-cl{k}",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:.35,ease:"power2.out"}},{T(a+.9+k*.3)})')
    js += [f'tl.fromTo("#{p}-cur",{{opacity:1}},{{opacity:0,duration:.25,repeat:{rep(d, .5)*2},yoyo:true,ease:"steps(1)"}},{T(a+.8)})',
           f'tl.fromTo("#{p}-gr",{{rotation:0,svgOrigin:"210 400"}},{{rotation:360,duration:{T(d)},ease:"none"}},{T(a)})',
           bob(f"#{p}-tag", a + 1, d - 1, 12, 1.6)]
    return svg, js + sfxjs(p, a + 1.4, st)

def sc_space(p, a, d, st):
    earth = flat(P("M-60,640 Q540,420 1140,640 Z"), "f1 d") + flat(P("M120,600 Q300,540 420,570 Q360,610 200,620 Z M640,560 Q780,520 900,560 Q820,600 700,600 Z"), "f4 d")
    dish = (f'<g id="{p}-ds"><g transform="translate(250 520)">' + slab(R(-12, -100, 24, 100, 6), 3, 4, 2)
            + f'<g id="{p}-dh">{slab(P("M-90,-150 Q0,-60 90,-150 Q40,-190 -10,-190 Q-60,-186 -90,-150 Z"), 3, 8, 3)}{L(0, -120, 30, -190, "lnT")}</g></g></g>')
    sat = (f'<g id="{p}-sat"><g transform="translate(700 210) rotate(-15)">'
           + slab(R(-200, -40, 130, 80, 6), 1, 6, 2) + "".join(L(-200 + j * 32, -40, -200 + j * 32, 40, "lnT") for j in range(1, 4))
           + slab(R(70, -40, 130, 80, 6), 1, 6, 2) + "".join(L(70 + j * 32, -40, 70 + j * 32, 40, "lnT") for j in range(1, 4))
           + L(-70, 0, -40, 0, "ln") + L(40, 0, 70, 0, "ln") + slab(R(-44, -56, 88, 112, 16), 3, 10, 3) + slab(C(0, 70, 20), 4, 4, 2)
           + hi(R(-36, -48, 16, 90, 8)) + '</g></g>')
    waves = "".join(f'<path id="{p}-wv{k}" class="lnA" d="M{330 + k*60},{390 - k*40} Q{390 + k*50},{330 - k*60} {460 + k*40},{360 - k*70}" opacity="0"/>' for k in range(3))
    svg = stage(p, 540, 260, 230, 700, 1) + earth + dish + waves + sat + sfx(p, 860, 560, "SIGNAL!", st)
    js = stage_js(p, a, d, 540, 260) + ent(st, [f"{p}-sat", f"{p}-ds"], a + .3, .2)
    js += [bob(f"#{p}-sat", a + .9, d - .9, 16, 2.2), f'tl.fromTo("#{p}-dh",{{rotation:-8,svgOrigin:"250 400"}},{{rotation:8,duration:1.6,repeat:{rep(d, 1.6)},yoyo:true,ease:"sine.inOut"}},{T(a+.8)})']
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-wv{k}",{{opacity:0}},{{opacity:1,duration:.3,repeat:{rep(d, 1.0)},yoyo:true,repeatDelay:.4}},{T(a+1.0+k*.2)})')
    return svg, js + sfxjs(p, a + 1.4, st)

def sc_search(p, a, d, st):
    bar = (f'<g id="{p}-bar">' + slab(R(200, 80, 680, 92, 46), 3, 12, 4) + flat(C(256, 126, 22), "lnD d") + flat(L(272, 142, 290, 160, "lnD"), "lnD d")
           + f'<rect id="{p}-q" class="f1" x="310" y="114" width="300" height="24" rx="12"/>' + slab(R(760, 92, 104, 68, 34), 2, 4, 2) + '</g>')
    res = "".join(f'<g id="{p}-r{k}"><g transform="translate(0 {k*92})">{slab(R(240, 210, 520, 72, 18), 3, 8, 3)}{flat(C(282, 246, 20), f"f{(1, 2, 4)[k]} d")}'
                  f'{flat(L(320, 236, 640 - k * 60, 236, "lnE"), "lnE d")}{flat(L(320, 258, 560, 258, "lnE"), "lnE d")}</g></g>' for k in range(3))
    mag = (f'<g id="{p}-mg"><g transform="translate(860 400)">' + slab(R(30, 40, 40, 140, 16), "dk", 8, 3) + slab(C(0, 0, 90), "dk", 12, 4)
           + flat(C(0, 0, 66), "glass d") + hi(P("M-44,-30 Q-30,-56 0,-62 Q-24,-40 -32,-10 Z")) + '</g></g>')
    svg = stage(p, 540, 330) + bar + res + mag + sfx(p, 860, 590, "RANKED!", st)
    js = stage_js(p, a, d, 540, 330) + ent(st, [f"{p}-bar", f"{p}-mg"], a + .3, .2)
    js.append(f'tl.fromTo("#{p}-q",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:1.0,ease:"steps(12)"}},{T(a+.8)})')
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-r{k}",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:.4,ease:"back.out(1.8)"}},{T(a+1.6+k*.2)})')
    sw = a + min(3.6, d * .5)
    js += [f'tl.to("#{p}-r2",{{y:-184,duration:.6,ease:"power3.inOut"}},{T(sw)})', f'tl.to("#{p}-r0",{{y:92,duration:.6,ease:"power3.inOut"}},{T(sw)})',
           f'tl.to("#{p}-r1",{{y:92,duration:.6,ease:"power3.inOut"}},{T(sw)})',
           f'tl.fromTo("#{p}-mg",{{x:0,y:0}},{{x:-40,y:-30,duration:1.4,repeat:{rep(d, 1.4)},yoyo:true,ease:"sine.inOut"}},{T(a+1)})']
    return svg, js + sfxjs(p, sw + .4, st)

def sc_glasses(p, a, d, st):
    gl = (f'<g id="{p}-gl">' + slab(P("M160,250 L210,236 L220,250 L170,266 Z"), "dk", 8, 3) + slab(P("M920,250 L870,236 L860,250 L910,266 Z"), "dk", 8, 3)
          + slab(R(200, 200, 300, 200, 70), "dk", 14, 4) + slab(R(580, 200, 300, 200, 70), "dk", 14, 4) + slab(R(490, 250, 100, 30, 14), "dk", 8, 3)
          + flat(R(222, 222, 256, 156, 56), "glass d") + flat(R(602, 222, 256, 156, 56), "glass d")
          + f'<defs><clipPath id="{p}-lc"><rect x="222" y="222" width="256" height="156" rx="56"/><rect x="602" y="222" width="256" height="156" rx="56"/></clipPath></defs>'
          + f'<g clip-path="url(#{p}-lc)"><rect id="{p}-gn" class="hi" x="120" y="180" width="60" height="260" transform="skewX(-25)"/></g>'
          + f'<g id="{p}-hud">{flat(C(730, 300, 34), "lnA d")}{L(696, 300, 764, 300, "lnA")}{L(730, 266, 730, 334, "lnA")}'
          + flat(R(250, 250, 110, 16, 8), "f4") + flat(R(250, 278, 160, 12, 6), "f3") + flat(R(250, 300, 80, 12, 6), "f3") + '</g></g>')
    cards = "".join(f'<g id="{p}-cd{k}">{slab(R(x, y, 150, 86, 18), c, 8, 3)}{flat(L(x+20, y+30, x+120, y+30, "lnE"), "lnE d")}{flat(L(x+20, y+54, x+90, y+54, "lnE"), "lnE d")}</g>'
                    for k, (x, y, c) in enumerate(((140, 440, 1), (460, 460, 4), (780, 440, 2))))
    waves = "".join(f'<path id="{p}-sw{k}" class="lnA" d="M{940 + k*30},{200 - k*12} Q{970 + k*36},250 {940 + k*30},{300 + k*12}" opacity="0"/>' for k in range(3))
    svg = stage(p) + cards + gl + waves + sfx(p, 540, 110, "SMART GLASSES", st)
    js = stage_js(p, a, d) + ent(st, [f"{p}-gl"], a + .3)
    js += [f'tl.fromTo("#{p}-gn",{{x:0}},{{x:900,duration:1.2,repeat:{rep(d, 2.4)},repeatDelay:1.2,ease:"power2.inOut"}},{T(a+1)})',
           f'tl.fromTo("#{p}-hud",{{opacity:0}},{{opacity:1,duration:.4}},{T(a+1.2)})',
           bob(f"#{p}-gl", a + 1, d - 1, 8, 2.0)]
    for k in range(3):
        js.append(f'tl.fromTo("#{p}-cd{k}",{{opacity:0,y:60}},{{opacity:1,y:0,duration:.45,ease:"back.out(2)"}},{T(a+1.4+k*.3)})')
        js.append(f'tl.fromTo("#{p}-sw{k}",{{opacity:0}},{{opacity:1,duration:.3,repeat:{rep(d, 1.0)},yoyo:true,repeatDelay:.4}},{T(a+1.0+k*.15)})')
    return svg, js + sfxjs(p, a + 1.6, st)

SCENES = {"rocket": sc_rocket, "robot": sc_robot, "shield": sc_shield, "phone": sc_phone, "bolt": sc_bolt, "chip": sc_chip,
          "globe": sc_globe, "chat": sc_chat, "cloud": sc_cloud, "car": sc_car, "money": sc_money, "law": sc_law,
          "media": sc_media, "code": sc_code, "space": sc_space, "search": sc_search, "glasses": sc_glasses}
SFX = {"rocket": "LIFT-OFF!", "robot": "WATCH & LEARN", "shield": "BLOCKED!", "phone": "NEW DROP!", "bolt": "POWER UP!", "chip": "NEW MODEL!",
       "globe": "WORLDWIDE", "chat": "AI CHAT", "cloud": "THE CLOUD", "car": "SELF-DRIVING", "money": "BIG MONEY", "law": "ORDER!",
       "media": "CREATE!", "code": "SHIP IT!", "space": "SIGNAL!", "search": "RANKED!", "glasses": "SMART GLASSES"}
KEYWORDS = [("law", r"regulat|court|lawsuit|sued|antitrust|\bban\b|banned|fine[ds]?\b|ruling|judge|policy|act\b|compliance"),
            ("shield", r"secur|privacy|breach|hack|scam|malware|phish|deepfake|leak|vulnerab"),
            ("glasses", r"glasses|wearable|headset|\bvr\b|\bar\b|\bxr\b|vision pro|quest"),
            ("car", r"\bcar\b|cars|tesla|waymo|\bev\b|evs|vehicle|driv|robotaxi"),
            ("robot", r"robot|humanoid|agent|automation|autonomous"),
            ("chat", r"chatbot|chatgpt|gemini app|assistant|copilot|claude|reply|conversation|voice mode"),
            ("media", r"image|video|photo|\bart\b|music|film|camera|creative|\bgif|sora|veo|midjourney|design"),
            ("search", r"search|seo|ranking|adsense|google discover|results"),
            ("code", r"developer|\bcode|coding|github|\bapi\b|programming|framework|next\.js|react|browser|software|open.source|sdk"),
            ("space", r"satellite|space|starlink|isro|nasa|telecom|\b5g\b|\b6g\b|spectrum|launch vehicle"),
            ("cloud", r"cloud|server|aws|azure|storage|outage"),
            ("bolt", r"energy|power|electric|battery|data cent|grid|nuclear"),
            ("money", r"fund|ipo|valuation|revenue|stock|invest|billion|deal|acqui|earnings|price|market"),
            ("phone", r"phone|iphone|pixel|galaxy|gadget|device|laptop|watch|tablet|earbuds|launch"),
            ("globe", r"india|global|world|government|upi|country|nation"),
            ("chip", r"chip|gpu|nvidia|model|\bllm|gpt|ai\b|processor|semiconductor")]

def pick(s):
    if s.get("scene") in SCENES: return s["scene"]
    if s.get("shape") in SCENES: return s["shape"]
    txt = (s.get("category", "") + " " + s.get("headline", "")).lower()
    for k, pat in KEYWORDS:
        if re.search(pat, txt): return k
    return "chip"

# ------------------------------------------------------------------ CSS
def _shade(h, f):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))

def css(family, fills=None, line="#F4F6FB", acc="#FFD84D", light=False):
    """Extra classes for v2 scenes. family: flat | ink | line."""
    if family == "line":
        return f"""
.sc svg .km,.sc svg .hi{{display:none}} .sc svg .kd{{fill:none;stroke-opacity:.35}}
.sc svg .gs{{fill:none;stroke-dasharray:6 10;stroke-opacity:.35}} .sc svg .bd{{fill:none;stroke-opacity:.18;stroke-dasharray:3 12}}
.sc svg .rg{{fill:none;stroke-opacity:.25;stroke-dasharray:2 16}} .sc svg .rg2{{stroke-dasharray:22 14}}
.sc svg .pt{{fill:{acc};stroke:none}} .sc svg .ptl{{stroke:{acc};fill:none}}
.sc svg .scr,.sc svg .scr2,.sc svg .sky,.sc svg .glass,.sc svg .win,.sc svg .road{{fill:rgba(255,255,255,.06)}}
.sc svg .void{{fill:none}} .sc svg .sk,.sc svg .hr{{fill:none}} .sc svg .dkf{{fill:{line};stroke:none}}
.sc svg .lnS{{stroke-width:9;fill:none}} .sc svg .lnB{{stroke:{acc};stroke-width:4}} .sc svg .lnD{{stroke-width:9;fill:none}}
.sc svg .pulse{{fill:{acc};stroke:none}} .sc svg .glow{{fill:none;stroke:{acc};stroke-opacity:.3;stroke-dasharray:4 8}}
.sc svg .flame2{{fill:none;stroke:{acc}}} .sc svg .rp{{fill:none;stroke:{acc};stroke-width:4}}
.sc svg .stamp{{fill:none;stroke:{acc};stroke-width:5}} .sc svg .stamptx{{font-family:FTHead;font-size:30px;fill:{acc};stroke:none;letter-spacing:3px}}
.sc svg .beamf{{fill:{acc};stroke:none;opacity:.2}}
.sc svg .tx{{font-family:FTHead;font-weight:700;fill:{line};stroke:none}} .sc svg .tx2{{font-family:FTHead;font-weight:700;fill:{acc};stroke:none}}
.sc svg .tx3{{font-family:FTHead;font-weight:700;fill:{acc};stroke:none}}"""
    f = fills
    k = [_shade(c, .62) for c in f]
    dk = "#1E2452" if light else "#2E3A73"
    kdk = _shade(dk, .6)
    base = f"""
.sc svg .k1{{fill:{k[0]}}} .sc svg .k2{{fill:{k[1]}}} .sc svg .k3{{fill:{k[2]}}} .sc svg .k4{{fill:{k[3]}}} .sc svg .k5{{fill:{k[4]}}}
.sc svg .fdk{{fill:{dk}}} .sc svg .kdk{{fill:{kdk}}} .sc svg .fsk{{fill:#F2C29B}} .sc svg .ksk{{fill:#C99572}}
.sc svg .sk{{fill:#F2C29B}} .sc svg .hr{{fill:#2B2118}}
.sc svg .hi{{fill:#FFFFFF;opacity:.38}}
.sc svg .gs{{fill:#000;opacity:{.12 if light else .28}}} .sc svg .bd{{fill:{f[0]};opacity:{.16 if light else .12}}}
.sc svg .rg{{fill:none;stroke:{f[0]};stroke-width:3;stroke-dasharray:3 16;opacity:.45}} .sc svg .rg2{{stroke:{f[3]};stroke-dasharray:24 16;opacity:.35}}
.sc svg .pt{{fill:{f[3]}}} .sc svg .ptl{{stroke:{f[0]};stroke-width:5;fill:none;stroke-linecap:round}}
.sc svg .scr{{fill:{f[0]};opacity:.28}} .sc svg .scr2{{fill:{_shade(f[0], .35) if not light else "#E8F3FF"}}} .sc svg .sky{{fill:{_shade(f[0], .55)}}}
.sc svg .glass{{fill:{f[0]};opacity:.45}} .sc svg .win{{fill:{f[3]};opacity:.7}} .sc svg .road{{fill:{dk}}} .sc svg .void{{fill:#05070F}}
.sc svg .dkf{{fill:{dk}}}
.sc svg .lnS{{stroke:#F2C29B;stroke-width:22;stroke-linecap:round;fill:none}}
.sc svg .lnB{{stroke:{f[1]};stroke-width:5;stroke-linecap:round}} .sc svg .lnD{{stroke:{dk};stroke-width:10;fill:none;stroke-linecap:round}}
.sc svg .pulse{{fill:#fff}} .sc svg .glow{{fill:{f[0]};opacity:.35}}
.sc svg .flame2{{fill:{f[3]}}} .sc svg .rp{{fill:none;stroke:{f[0]};stroke-width:6}}
.sc svg .stamp{{fill:none;stroke:{f[1]};stroke-width:6}} .sc svg .stamptx{{font-family:FTHead;font-weight:700;font-size:30px;fill:{f[1]};letter-spacing:3px}}
.sc svg .beamf{{fill:{f[3]};opacity:.25}}
.sc svg .tx{{font-family:FTHead;font-weight:700;fill:{_shade(f[3], .45)}}} .sc svg .tx2{{font-family:FTHead;font-weight:700;fill:#FFFFFF}} .sc svg .tx3{{font-family:FTHead;font-weight:700;fill:{f[3]}}}
"""
    if family == "ink":
        base += """
.sc svg .km{stroke:none} .sc svg .hi,.sc svg .gs,.sc svg .bd,.sc svg .pt,.sc svg .glow,.sc svg .pulse,.sc svg .beamf,.sc svg .scr{stroke:none}
.sc svg .rg{stroke:#111;opacity:.35} .sc svg .tx,.sc svg .tx2,.sc svg .tx3,.sc svg .stamptx{stroke:none}
.sc svg .bd{fill:#FFFFFF;opacity:.5}"""
    else:
        base += """
.sc svg .km,.sc svg .kd{stroke:none}"""
    return base
