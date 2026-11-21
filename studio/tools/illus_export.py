#!/usr/bin/env python3
"""Export a freshtechupdates illustration scene (engine/illus.py: 17 animated 3D-sticker scenes + the FT Bot
mascot) as a bundle the Remotion studio can play: {svg, js, css, viewBox}. The GSAP timeline in `js` is
seeked frame by frame by src/ftu/IllusScene.tsx, so renders stay deterministic.

  python3 tools/illus_export.py robot --family flat --seconds 5 --accent "#22D3EE"     (prints JSON; for testing)

Scenes: rocket robot shield phone bolt chip globe chat cloud car money law media code space search glasses
Families: flat (filled 3D stickers), ink (comic, black outlines), line (blueprint line drawing)
"""
import argparse, json, re, sys, pathlib

ENGINE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE))

FAM_ST = {"flat": "paper", "ink": "comic", "line": "blueprint"}
SCENE_NAMES = ["rocket", "robot", "shield", "phone", "bolt", "chip", "globe", "chat", "cloud", "car", "money",
               "law", "media", "code", "space", "search", "glasses"]


def palette(look):
    """Five sticker fills that sit well with the look of the day: accent first."""
    acc = look["accent"].upper()
    sets = {
        "#22D3EE": ["#22D3EE", "#FF4D6D", "#F4F6FB", "#FFD166", "#7C83FD"],
        "#A3E635": ["#A3E635", "#22D3EE", "#F3EBDD", "#FFB347", "#FF6B6B"],
        "#F59E0B": ["#F59E0B", "#22D3EE", "#FAFAF9", "#FDE68A", "#FB7185"],
        "#FF5A5F": ["#FF5A5F", "#22D3EE", "#FFF7ED", "#FFD166", "#A78BFA"],
        "#7C83FF": ["#7C83FF", "#2DD4BF", "#F5F5FF", "#FFD166", "#FF6B8B"],
        "#2DD4BF": ["#2DD4BF", "#F472B6", "#F0FDFA", "#FDE047", "#818CF8"],
        "#F472B6": ["#F472B6", "#22D3EE", "#FDF2F8", "#FDE047", "#A3E635"],
    }
    return sets.get(acc, [acc, "#22D3EE", look.get("ink", "#F8FAFC"), "#FFD166", "#FF6B6B"])


def bundle(scene, prefix, seconds, look, family="flat", bot=False, pose="cheer", font="sans-serif", label=None):
    """label: replace the scene's sticker word (e.g. "RANKED!" on `search`); "" hides the sticker."""
    import illus, longform, styreel
    if scene not in illus.SCENES:
        raise SystemExit(f"ILLUS_ERROR unknown scene '{scene}' (one of: {' '.join(SCENE_NAMES)})")
    st = FAM_ST[family]
    svg, js = illus.SCENES[scene](prefix, 0.0, float(seconds), st)
    if bot:
        m = prefix + "m"   # own id prefix: scenes like `robot` already use {prefix}-aL etc.
        svg += styreel.bot_svg(m, 975, 545, .55, st)
        js += styreel.ent(st, [f"{m}-botb"], .9) + styreel.bot_js(m, 0.0, float(seconds), 1.5, pose)
    fills = look.get("fills") or palette(look)
    light = bool(look.get("light"))
    S = {"family": family, "fills": fills if family != "line" else None, "line": look.get("line") or look.get("ink", "#F8FAFC"),
         "acc": look["accent"], "light": light}
    css = longform._scene_css(S) + illus.css(family, S["fills"], S["line"], S["acc"], light)
    if family == "line":
        css = ".sc svg .f1,.sc svg .f2,.sc svg .f3,.sc svg .f5{fill:rgba(255,255,255,.05)}" + css
    css = re.sub(r"\bFTHead\b|\bFTBody\b", f"'{font}'", css)
    # scope to this beat so beats with different families can share the page during transitions
    css = css.replace(".sc svg", f".sc-{prefix} svg")
    if label is not None:
        if label == "":
            css += f"#{prefix}-sfx{{display:none}}"
        else:
            import html as _h
            svg = re.sub(rf'(<g id="{re.escape(prefix)}-sfx">.*?<text class="sfxtxt"[^>]*>)[^<]*(</text>)',
                         lambda m: m.group(1) + _h.escape(label.upper()[:16]) + m.group(2), svg, count=1, flags=re.S)
    defs = ('<defs><filter id="ps" x="-20%" y="-20%" width="140%" height="160%">'
            '<feDropShadow dx="0" dy="9" stdDeviation="0" flood-color="#000" flood-opacity=".3"/></filter></defs>')
    return {"svg": defs + svg, "js": js, "css": css, "viewBox": "0 0 1080 640", "prefix": prefix, "scene": scene, "family": family}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene"); ap.add_argument("--family", default="flat"); ap.add_argument("--seconds", type=float, default=5)
    ap.add_argument("--accent", default="#22D3EE"); ap.add_argument("--bot", action="store_true")
    a = ap.parse_args()
    b = bundle(a.scene, "t1", a.seconds, {"accent": a.accent, "ink": "#F8FAFC"}, a.family, a.bot)
    print(json.dumps({k: (v if k != "svg" else v[:200] + "...") for k, v in b.items() if k != "js"} | {"js_lines": len(b["js"])}, indent=1))


if __name__ == "__main__":
    main()
