#!/usr/bin/env python3
"""Visual QA (after Remocn's scene-reviewer): stills of every beat on one contact sheet to look at.

  python3 tools/review.py out/props.json            -> out/review/sheet-01.png, sheet-02.png ... (4 beats per sheet)

For each beat: entry (start + 8), settled (the component's natural length, or the middle) and end of
hold (end - 6). View each sheet with Read and check: text cut by the frame edge, text too small or low
contrast, empty or flat frames, captions or chrome covering the beat's own text, fallback fonts,
more than one accent colour, ALL-CAPS blocks, lorem/placeholder copy, the Remocn logo/name showing.
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent.parent


def main():
    props = pathlib.Path(sys.argv[1]).resolve()
    plan = json.loads(props.read_text())["plan"]
    cat = {}
    cp = HERE / "catalog/catalog.json"
    if cp.exists():
        cat = {c["name"]: c for c in json.loads(cp.read_text())}
    out = HERE / "out/review"; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"):
        f.unlink()
    rows = []
    for i, b in enumerate(plan["beats"]):
        nat = cat.get(b["component"], {}).get("length", "")
        nat = int(nat) if str(nat).isdigit() else b["frames"] // 2
        nxt = plan["beats"][i + 1]["transitionFrames"] if i + 1 < len(plan["beats"]) else 0
        end = b["start"] + b["frames"] - nxt - 3          # last frame before the next transition starts
        frames = [b["start"] + min(8, b["frames"] - 1), min(b["start"] + nat, end), end]
        frames = [max(0, min(plan["total"] - 1, f)) for f in frames]
        row = []
        for f in frames:
            png = out / f"b{i + 1:02d}-{f}.png"
            subprocess.run([str(HERE / "render.sh"), str(props), str(png), str(f)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            row.append(png)
        rows.append((i, row))
    short = plan["format"] == "short"
    w = 300 if short else 520
    for s in range(0, len(rows), 4):
        chunk = rows[s:s + 4]
        inputs, filt, labels = [], [], []
        k = 0
        for i, row in chunk:
            for png in row:
                inputs += ["-i", str(png)]
                filt.append(f"[{k}]scale={w}:-1,drawbox=0:0:iw:ih:color=white@0.3:t=2[v{k}]"); k += 1
        n = len(chunk)
        for r in range(n):
            filt.append("".join(f"[v{r * 3 + c}]" for c in range(3)) + f"hstack=3[r{r}]")
        filt.append("".join(f"[r{r}]" for r in range(n)) + (f"vstack={n}[o]" if n > 1 else "null[o]"))
        sheet = out / f"sheet-{s // 4 + 1:02d}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[o]", str(sheet)], check=True)
        names = ", ".join(f"beat {i + 1} {plan['beats'][i]['component']}" for i, _ in chunk)
        print(f"REVIEW {sheet}  rows: {names}  (columns: entry, settled, end)")


if __name__ == "__main__":
    main()
