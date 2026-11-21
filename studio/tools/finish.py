#!/usr/bin/env python3
"""After the render: thumbnails / cover + the post texts that zernio_post.py reads, copied into the engine's out/.

  python3 tools/finish.py storyboard.json out/props.json out/video.mp4 --kind daily-long|daily-short|trend

storyboard.json needs a "meta" block (written by the director):
  "meta": {"title": "...", "description": "2-4 sentences", "tags": ["..."],
           "thumb_text": "max 5 words, *accent* word", "thumb_beat": 2,
           "thumb_text_b": "other angle, max 4 words", "thumb_beat_b": 4,
           "cover_text": "Short cover line, max 6 words, *accent*",
           "ig_caption": "full Instagram caption incl. hashtags",
           "sources": ["https://..."]}
Outputs in ../out (engine): long -> freshtechupdates-episode.mp4, thumbnail.png (A), thumbnail-B.png, thumbnail-C.png, youtube.txt
                            short -> freshtechupdates-reel.mp4, short-cover.png, short.txt, ig-caption.txt
                            trend -> trend-reel.mp4, trend-cover.png, trend-short.txt, trend-ig-caption.txt
"""
import argparse, json, pathlib, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
ENGINE_OUT = HERE.parent / "out"
BROWSER = ["--browser-executable=/usr/bin/google-chrome", "--gl=angle", "--log=error"]


def settled(plan, i):
    cat = json.loads((HERE / "catalog/catalog.json").read_text())
    nat = next((c["length"] for c in cat if c["name"] == plan["beats"][i]["component"]), "")
    b = plan["beats"][i]
    n = int(nat) if str(nat).isdigit() else b["frames"] // 2
    return min(n, b["frames"] - 1)


def still(plan, beat, text, out, layout, w, h, scale=0.82):
    beat = max(0, min(beat, len(plan["beats"]) - 1))
    props = {"plan": plan, "beat": beat, "frame": settled(plan, beat), "text": text, "layout": layout, "w": w, "h": h, "scale": scale}
    pf = HERE / "out/thumb-props.json"; pf.write_text(json.dumps(props))
    subprocess.run(["npx", "remotion", "still", "src/index.ts", "Thumb", str(out), f"--props={pf}", f"--frame={props['frame']}", *BROWSER],
                   cwd=HERE, check=True, stdout=subprocess.DEVNULL)


def humanize(text):
    tool = HERE.parent / "tools/ig/humanize.py"
    if not tool.exists():
        return text
    r = subprocess.run([sys.executable, str(tool), "-"], input=text, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard"); ap.add_argument("props"); ap.add_argument("video")
    ap.add_argument("--kind", required=True, choices=["daily-long", "daily-short", "trend"])
    a = ap.parse_args()
    sb = json.loads(pathlib.Path(a.storyboard).read_text()); meta = sb.get("meta") or {}
    plan = json.loads(pathlib.Path(a.props).read_text())["plan"]
    ENGINE_OUT.mkdir(exist_ok=True)
    srcs = meta.get("sources") or []
    plain = lambda t: (t or "").replace("*", "")
    if a.kind == "daily-long":
        shutil.copy(a.video, ENGINE_OUT / "freshtechupdates-episode.mp4")
        still(plan, meta.get("thumb_beat", 1), meta.get("thumb_text", meta.get("title", "")), ENGINE_OUT / "thumbnail.png", "left", 1280, 720)
        still(plan, meta.get("thumb_beat_b", 2), meta.get("thumb_text_b", meta.get("thumb_text", "")), ENGINE_OUT / "thumbnail-B.png", "left", 1280, 720)
        still(plan, meta.get("thumb_beat", 1), "", ENGINE_OUT / "thumbnail-C.png", "none", 1280, 720, 1.0)
        chapters = (HERE / "out/chapters.txt").read_text().strip().splitlines() if (HERE / "out/chapters.txt").exists() else []
        if chapters and not chapters[0].startswith("0:00"):
            chapters.insert(0, "0:00 Intro")
        desc = [humanize(meta.get("description", "")), ""]
        if len(chapters) >= 3:
            desc += ["Chapters:"] + chapters + [""]
        if srcs:
            desc += ["Sources:"] + [f"- {s}" for s in srcs] + [""]
        desc += ["New AI & tech updates every day. Subscribe: @freshtechupdates"]
        (ENGINE_OUT / "youtube.txt").write_text(f"TITLE:\n{plain(meta.get('title', ''))[:100]}\n\nDESCRIPTION:\n" + "\n".join(desc)
                                                + f"\n\nTAGS:\n{', '.join(meta.get('tags', []))}\n")
        print("FINISH daily-long: freshtechupdates-episode.mp4 thumbnail.png thumbnail-B.png thumbnail-C.png youtube.txt")
    else:
        trend = a.kind == "trend"
        mp4, cover, txt, cap = (("trend-reel.mp4", "trend-cover.png", "trend-short.txt", "trend-ig-caption.txt") if trend else
                                ("freshtechupdates-reel.mp4", "short-cover.png", "short.txt", "ig-caption.txt"))
        shutil.copy(a.video, ENGINE_OUT / mp4)
        still(plan, meta.get("cover_beat", 0), meta.get("cover_text", ""), ENGINE_OUT / cover,
              "bottom" if meta.get("cover_text") else "none", 1080, 1920, 1.0)
        desc = [humanize(meta.get("description", "")), ""]
        if srcs:
            desc += ["Sources:"] + [f"- {s}" for s in srcs] + [""]
        desc += [("A new AI & tech explainer every day, plus daily updates: @freshtechupdates" if trend
                  else "Full episode with all of today's updates on our channel: @freshtechupdates"), "",
                 "#shorts #AI #tech #freshtechupdates" + (" #explained" if trend else "")]
        (ENGINE_OUT / txt).write_text(f"TITLE:\n{plain(meta.get('title', ''))[:95]}\n\nDESCRIPTION:\n" + "\n".join(desc) + "\n")
        caption = humanize(meta.get("ig_caption", ""))
        if trend and "#explained" not in caption:
            caption += " #explained"
        if "#freshtechupdates" not in caption:
            caption += " #freshtechupdates"
        (ENGINE_OUT / cap).write_text(caption.strip() + "\n")
        print(f"FINISH {a.kind}: {mp4} {cover} {txt} {cap}")


if __name__ == "__main__":
    main()
