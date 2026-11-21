#!/usr/bin/env python3
"""Storyboard -> renderable Remotion props. No fixed template: every beat names its own Remocn component.

  python3 tools/build.py storyboard.json --repo ../remocn      -> out/props.json, public/audio/mix.wav, src/generated/registry.ts
  then: ./render.sh out/props.json out/video.mp4

storyboard.json (written per video by the director, see the skill in .claude/skills/ftu-video):
{
  "format": "short" | "long",                 # short = 1080x1920 (max 60 s), long = 1920x1080
  "look": {"accent": "#22D3EE", "ink": "#F8FAFC", "background": "#0A0F1E", "font": "Manrope"},   # optional: default = look of the day
  "captions": "caption-karaoke" | null,       # a Remocn caption-* component for the voice, or null
  "music": true,
  "beats": [
    {"component": "hook-punch", "props": {...},   # props exactly as in `catalog.py show <component>`
     "voice": "what is said over this beat",      # optional; sets the beat length
     "captions": true,                            # show voice captions on this beat (default: true unless the beat is text-led)
     "hold": 0.4,                                 # seconds to hold after the voice ends (default 0.35)
     "minFrames": 90,                             # optional floor; default = the component's natural length
     "transition": "fade" | "slide" | "wipe" | "flip" | "clock" | "none" | "<remocn transition component>",
     "tag": "AI models", "source": "theverge.com",  # small on-screen chrome (optional)
     "chapter": "Anthropic lists on Nasdaq"       # long format: YouTube chapter title (optional)
    }
  ]
}
"""
import argparse, datetime, hashlib, json, math, pathlib, re, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent.parent          # studio/
ENGINE = HERE.parent
SR, FPS = 24000, 30
BUILTIN_TRANSITIONS = {"fade", "slide", "wipe", "flip", "clock", "none"}
LOOKS = [  # brand-safe looks: the FT logo colours lead, the rest rotate by date
    {"accent": "#22D3EE", "ink": "#F8FAFC", "background": "#0A0F1E", "font": "Manrope"},
    {"accent": "#A3E635", "ink": "#F3EBDD", "background": "#0D0F0A", "font": "Sora"},
    {"accent": "#F59E0B", "ink": "#FAFAF9", "background": "#14110C", "font": "Inter"},
    {"accent": "#FF5A5F", "ink": "#FFF7ED", "background": "#120B0E", "font": "HankenGrotesk"},
    {"accent": "#7C83FF", "ink": "#F5F5FF", "background": "#0B0B18", "font": "InstrumentSans"},
    {"accent": "#2DD4BF", "ink": "#F0FDFA", "background": "#061412", "font": "BricolageGrotesque"},
    {"accent": "#F472B6", "ink": "#FDF2F8", "background": "#12080F", "font": "SchibstedGrotesk"},
]
BRAND_PROPS = {"accent", "ink", "background", "fontFamily", "showLogo", "logo"}


def look_of_the_day(seed=None):
    d = seed or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")
    return dict(LOOKS[int(hashlib.md5(d.encode()).hexdigest(), 16) % len(LOOKS)])


def pascal(name):
    return "".join(p.capitalize() for p in re.split(r"[-_]", name))


def export_name(path, name, lower=False):
    src = path.read_text()
    names = re.findall(r"export\s+(?:const|function)\s+(\w+)", src)
    want = pascal(name)
    if lower:
        want = want[0].lower() + want[1:]
        cands = [n for n in names if n[0].islower() and not n.startswith("use")]
    else:
        cands = [n for n in names if n[0].isupper()]
    if want in names:
        return want
    return cands[0] if cands else None


def catalog():
    p = HERE / "catalog" / "catalog.json"
    return {c["name"]: c for c in json.loads(p.read_text())} if p.exists() else {}


def natural_frames(c, default=75):
    try:
        return int(re.match(r"\d+", str(c.get("length", ""))).group(0))
    except Exception:
        return default


# ------------------------------------------------------------------ voice (free, offline Kokoro)
_K = None
def tts(text, voice, speed):
    global _K
    from kokoro_onnx import Kokoro
    if _K is None:
        _K = Kokoro(str(ENGINE / "kokoro-v1.0.onnx"), str(ENGINE / "voices-v1.0.bin"))
    sents = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]
    parts, words, t = [], [], 0.0
    for s in sents:
        a, _ = _K.create(s.replace("freshtechupdates", "fresh tech updates"), voice=voice, speed=speed, lang="en-us")
        a = a.astype(np.float32); d = len(a) / SR
        ws = s.split(); wt = [len(w) + 2 + (3 if re.search(r"[,.!?;:]$", w) else 0) for w in ws]
        tot = sum(wt); span = max(0.1, d - 0.16); c = t + 0.07
        for w, x in zip(ws, wt):
            dd = span * x / tot; words.append((w, c, c + dd)); c += dd
        parts += [a, np.zeros(int(0.1 * SR), np.float32)]; t += d + 0.1
    return (np.concatenate(parts) if parts else np.zeros(1, np.float32)), words


def whoosh(dur=0.38, seed=1):
    rng = np.random.default_rng(seed); n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    k = np.exp(-np.linspace(0, 6, 64)); x = np.convolve(x, k / k.sum(), "same")
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    return (x * env * 0.08).astype(np.float32)


def bed(total_s, seed):
    """Soft generated pad (no samples, no licence questions). Chords change with the date seed."""
    rng = np.random.default_rng(seed)
    roots = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59], [50, 53, 57], [48, 52, 55]]
    order = [roots[i] for i in rng.permutation(len(roots))[:4]]
    n = int(total_s * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    bar = 4.0
    for i in range(int(total_s / bar) + 1):
        ch = order[i % len(order)]; a, b = int(i * bar * SR), min(n, int((i + 1) * bar * SR + 0.5 * SR))
        if a >= n: break
        tt = t[a:b] - t[a]; env = np.minimum(1, tt / 0.8) * np.minimum(1, (b / SR - t[a:b]) / 0.8)
        for m in ch:
            f = 440 * 2 ** ((m - 69) / 12)
            out[a:b] += (0.5 * np.sin(2 * math.pi * f * tt) + 0.2 * np.sin(2 * math.pi * f * 2 * tt)) * env * 0.018
    return out


def build(sb, repo, seed=None):
    look = {**look_of_the_day(seed), **(sb.get("look") or {})}
    fmt = sb.get("format", "short")
    W, H = (1080, 1920) if fmt == "short" else (1920, 1080)
    voice, speed = sb.get("voice", "af_heart"), float(sb.get("speed", 1.1))
    cat = catalog()
    beats = sb["beats"]
    names = sorted({b["component"] for b in beats}
                   | ({sb["captions"]} if sb.get("captions") else set())
                   | {b["transition"] for b in beats if b.get("transition") and b["transition"] not in BUILTIN_TRANSITIONS})
    for n in names:
        if cat and n not in cat:
            sys.exit(f"BUILD_ERROR unknown component '{n}' (check with: python3 tools/catalog.py search ...)")
    subprocess.run([sys.executable, str(HERE / "tools/remocn_add.py"), "--repo", str(repo), *names], check=True)

    # font for chrome + captions: make sure a shim exists for it
    font_file = HERE / "src/fontshim" / f"{look['font']}.ts"
    if not font_file.exists():
        (HERE / "src/generated").mkdir(parents=True, exist_ok=True)
        (HERE / "src/generated/font-probe.ts").write_text(f'import "@remotion/google-fonts/{look["font"]}";\n')
        subprocess.run([sys.executable, str(HERE / "tools/remocn_add.py"), "--repo", str(repo), "--fonts-only"], check=True)

    # registry of the components this video uses
    imps, comps, trans = [], [], []
    for n in names:
        f = HERE / "src/components/remocn" / f"{n}.tsx"
        is_tr = n in {b.get("transition") for b in beats}
        ex = export_name(f, n, lower=is_tr) if f.exists() else None
        if not ex:
            sys.exit(f"BUILD_ERROR could not find the export in {f}")
        imps.append(f'import {{ {ex} }} from "@/components/remocn/{n}";')
        (trans if is_tr else comps).append(f'  "{n}": {ex},')
    gen = HERE / "src/generated"; gen.mkdir(parents=True, exist_ok=True)
    (gen / "registry.ts").write_text("// Generated by tools/build.py for the current storyboard.\n" + "\n".join(imps)
                                     + f'\nimport {{ loadFont }} from "@remotion/google-fonts/{look["font"]}";\n'
                                     + f'export const brandFont = loadFont("normal", {{ weights: ["400", "500", "600", "700"] }}).fontFamily;\n'
                                     + "export const COMPONENTS: Record<string, any> = {\n" + "\n".join(comps) + "\n};\n"
                                     + "export const TRANSITIONS: Record<string, any> = {\n" + "\n".join(trans) + "\n};\n")

    # timing + audio
    TR = 12
    plan, vo_parts, t_frames = [], [], 0
    for i, b in enumerate(beats):
        c = cat.get(b["component"], {})
        nat = int(b.get("minFrames") or natural_frames(c))
        audio, words = (tts(b["voice"], voice, speed) if b.get("voice") else (np.zeros(1, np.float32), []))
        lead = 0.25 if i else 0.15
        vo_s = len(audio) / SR if b.get("voice") else 0
        nxt = beats[i + 1] if i + 1 < len(beats) else None
        next_tr = 0 if (nxt is None or nxt.get("transition", "fade") == "none") else int(nxt.get("transitionFrames", TR))
        hold_f = int(round(float(b.get("hold", 0.35)) * FPS))
        # the component must finish its own animation and hold it before the next transition starts
        frames = max(nat + hold_f + next_tr, int(math.ceil((lead + vo_s + float(b.get("hold", 0.35))) * FPS)) + next_tr)
        tr = b.get("transition", "fade" if i else "none") if i else "none"
        tr_frames = 0 if tr == "none" else int(b.get("transitionFrames", TR))
        start = t_frames - tr_frames
        props = dict(b.get("props") or {})
        cprops = {p["name"] for p in c.get("props", [])}
        for k, v in (("accent", look["accent"]), ("ink", look["ink"]), ("showLogo", False)):
            if k in cprops and k not in props:
                props[k] = v
        for p_ in c.get("props", []):   # never show Remocn's own name/logo: swap any "remocn" default for our brand
            if p_["name"] not in props and "string" in p_["type"] and "remocn" in p_["default"].lower() and p_["name"] in ("name", "brand", "wordmark", "handle", "title"):
                props[p_["name"]] = "freshtechupdates"
        if "background" in cprops and "background" not in props and b.get("brandBackground", True):
            props["background"] = look["background"]
        caps = [{"text": (" " if j else "") + w, "startMs": int((lead + s) * 1000), "endMs": int((lead + e) * 1000),
                 "timestampMs": int((lead + (s + e) / 2) * 1000), "confidence": 1}
                for j, (w, s, e) in enumerate(words)]
        plan.append({"component": b["component"], "props": props, "frames": frames, "start": start,
                     "transition": tr, "transitionFrames": tr_frames,
                     "captions": caps if (sb.get("captions") and b.get("captions", True) and caps) else [],
                     "logoProp": "logo" in cprops, "logoSize": "big" if c.get("section") == "logo-stings" else "small", "tag": b.get("tag", ""), "source": b.get("source", ""),
                     "chapter": b.get("chapter", "")})
        vo_parts.append((start + int(lead * FPS) * 0, audio, lead))
        t_frames = start + frames
    total = t_frames
    if fmt == "short" and total > 60 * FPS:
        sys.exit(f"BUILD_ERROR Short is {total / FPS:.1f}s; the limit is 60 s. Cut voice lines or beats and run again.")

    n = int(total / FPS * SR) + SR
    mix = np.zeros(n, np.float32)
    for (st, audio, lead), p in zip(vo_parts, plan):
        a = int((st / FPS + lead) * SR); mix[a:a + len(audio)] += audio[:max(0, n - a)]
        if p["transition"] != "none":
            w = whoosh(seed=st); a2 = max(0, int(st / FPS * SR) - len(w) // 3); mix[a2:a2 + len(w)] += w[:max(0, n - a2)]
    if sb.get("music", True):
        mix += bed(n / SR, int(hashlib.md5(json.dumps(sb["beats"][0]).encode()).hexdigest(), 16) % 10000)[:n]
    mix = (mix / max(1.0, np.abs(mix).max() / 0.95)).astype(np.float32)
    import soundfile as sf
    (HERE / "public/audio").mkdir(parents=True, exist_ok=True)
    sf.write(str(HERE / "public/audio/mix.wav"), mix, SR)

    props = {"plan": {"format": fmt, "width": W, "height": H, "fps": FPS, "total": total, "look": look,
                      "captionsComponent": sb.get("captions"), "beats": plan,
                      "audio": "audio/mix.wav", "stamp": hashlib.md5(json.dumps(sb).encode()).hexdigest()[:8]}}
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out/props.json").write_text(json.dumps(props, indent=1, ensure_ascii=False))
    chapters, acc = [], 0
    for p in plan:
        if p["chapter"]:
            s = p["start"] // FPS
            chapters.append(f"{s // 60}:{s % 60:02d} {p['chapter']}")
    (HERE / "out/chapters.txt").write_text("\n".join(chapters) + ("\n" if chapters else ""))
    print(f"BUILD_OK {fmt} {W}x{H} {total / FPS:.1f}s {len(plan)} beats · look {look['font']} {look['accent']} · out/props.json")
    for i, p in enumerate(plan):
        print(f"  beat {i + 1:>2}: {p['component']:<24} {p['frames'] / FPS:5.1f}s  starts {p['start'] / FPS:6.1f}s  {p['transition']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard"); ap.add_argument("--repo", required=True); ap.add_argument("--seed")
    a = ap.parse_args()
    build(json.loads(pathlib.Path(a.storyboard).read_text()), pathlib.Path(a.repo).resolve(), a.seed)


if __name__ == "__main__":
    main()
