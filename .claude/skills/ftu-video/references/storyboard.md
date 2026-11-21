# Storyboards

Write one file per video in the engine root: `storyboard-short.json`, `storyboard-long.json`,
`storyboard-trend.json`. Full field list: top of `studio/tools/build.py`. Example: `studio/test/short.json`.

```json
{"format": "short", "captions": "caption-active-pop", "music": true,
 "meta": {"title": "...", "description": "...", "tags": ["..."], "cover_text": "max 6 words, *accent*",
          "ig_caption": "40-70 words + 12-15 hashtags", "sources": ["https://..."],
          "thumb_text": "...", "thumb_beat": 2, "thumb_text_b": "...", "thumb_beat_b": 4},
 "beats": [{"component": "...", "props": {...}, "voice": "...", "captions": true, "tag": "AI business",
            "source": "Reuters", "transition": "slide", "chapter": "long format only"}]}
```

## Timing
- A beat lasts as long as its voice line (plus hold), and never less than its component's own animation.
  Keep voice lines short: 12–25 words per beat in a Short, up to 45 in the episode.
- Short: hard limit 60 s (build refuses longer). Aim for 35–55 s.
- Long: about 30–45 s per story → 5 stories ≈ 3.5 min, 10 stories ≈ 7 min. Don't pad a slow day.
- Explainer: 35–45 s.

## Beat recipes (starting points; choose the components per story)

**Daily Short (3 stories)**
1. Hook — the most surprising concrete fact (Social → Hooks, or Typography → Kinetic posters). `captions: false`.
2. Story 1 — show its key thing (a number → Numbers; a product doing something → Product scenes/UI blocks;
   a claim → Typography statement).
3. Story 2 — voice starts "Next."
4. Story 3 — voice starts "And finally."
5. End — Logo sting (`introducing`, `first-light`, end stings…) with "Full episode on YouTube at 6 PM" or
   "Follow for tomorrow's updates". `captions: false`.

**Long episode (5–10 stories)**
- Opener: one statement beat ("Today in AI and tech" or the top story as a headline) — no list of
  stories (Vedanth's rule).
- Per story: a section card (`chapter` set) + 1–2 beats that show it + optional takeaway beat
  (Typography quote/statement: why it matters). Vary the section-card component every few stories.
- Outro: question for comments + subscribe, logo sting.

**Explainer (one topic)**
1. Hook: why everyone is talking about it. 2. What it is. 3. Why now. 4. What it means for you.
5. End: "Follow for daily explainers".

## Thumbnails and cover
`thumb_beat` / `thumb_beat_b` (0-based beat index): pick beats whose settled frame is a number, chart,
product scene or illustration, never a text statement (the thumbnail headline sits on the left half
and would clash). `cover_beat` (default 0) is the Short's cover with `cover_text` on the lower part.
After `finish.py`, view `out/thumbnail.png`, `thumbnail-B.png` and the cover with Read; if text clashes,
pick another beat and run finish.py again (seconds).

## Captions
Use a voice-caption component (`caption-active-pop`, `caption-karaoke`, `caption-highlight-box`,
`caption-underline`… — search `--section captions`). Vary it by day. Set `captions: false` on beats
whose own on-screen text already says the line (hooks, statements, end cards), so text never doubles up.

## Props that matter in 9:16
Remocn components are designed at 16:9. In a Short, big type often needs `scale` 0.5–0.85; wide
layouts need fewer words. Check every beat on the review sheet; fix with `scale` or shorter copy.
