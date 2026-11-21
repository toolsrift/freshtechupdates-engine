---
name: ftu-video
description: Make and post the daily freshtechupdates videos (YouTube Short + Instagram Reel up to 60 s, the long YouTube episode whose length follows the news, and the trending explainer Short). Use for any freshtechupdates daily run, or when asked to research AI & tech updates and turn them into videos with the engine's Remotion + Remocn studio. Every video is designed from its own storyboard, never from a fixed template.
---

# freshtechupdates video director

You research the day's AI & tech updates, then direct each video yourself: pick a layout per beat that
fits *that* story, write the voice, render, look at the frames, fix, and post through Zernio.

Every video mixes three layers (Vedanth's rule, 21 Nov 2026: text alone looks empty):
- **Visuals**: the FT illustration scenes (17 animated 3D-sticker scenes + FT Bot mascot, from v1) and
  icons. Our own layouts: `ftu-illus` (illustration + headline + icon points + stat + FT Bot tip),
  `ftu-icons` (icon tiles for lists/numbers), `ftu-compare` (A vs B). Any Remocn beat can also carry a
  `"visual"` illustration (top/bottom/left/right/corner/background).
- **Motion type**: Remocn components (~800) for hooks, statements, number reveals, charts, section cards,
  logo stings, captions, transitions.
- **Voice + captions**: free Kokoro voice with word-timed captions.

**Every story beat must show something**: an `ftu-*` layout or a Remocn beat with a `visual`. Text-only
is allowed only for the hook, section cards and the end card. `review.py` flags `NO_VISUAL` and `EMPTY`
(settled frame more than 80% empty); fix every flag before rendering.
There is no template to fill. Two videos on the same day should not look alike, and no video should look
like yesterday's. That is the whole point of this skill: viewers scroll past anything that looks
auto-generated.

All paths below are relative to the engine repo root (`engine/` in scheduled runs).

## 0. Setup (once per run)

```bash
./setup.sh && ./setup-v2.sh          # Kokoro voice, Remotion studio, Remocn source (../remocn), component catalog
```
`setup-v2.sh` prints `REMOCN_DIR=...`; pass that as `--repo` to the studio tools. Everything renders offline
(fonts are local copies; the shell cannot reach Google Fonts or most websites).

## 1. Research (one pass feeds every video)

Read `references/research.md` and do it. Output: `signals.json` and
`python3 trends.py score signals.json --lane daily` (or `--lane trend` for the explainer), which prints
`SHORT_PICKS` (3 stories), `LONG_PICKS` (5–10 stories) or `TREND_PICK`. Run
`python3 zernio_post.py recent` first so already-posted stories are pushed down.

Facts come only from pages you retrieved in this run. Every number on screen must appear in a source.
Unverified claims are labelled as claims ("says", "claims", "experts are still checking").

## 2. Direct each video: storyboard

Read `references/storyboard.md` (format, beat recipes, length budgets) and `references/craft.md`
(the quality bar). Then for each beat:

1. Decide what the beat must *show*: a number, a comparison, a list, a quote, a product doing something, a
   place, a claim. That decides the layout, not habit:
   - one story with its key facts → `ftu-illus` (pick the scene that fits; set `label` to a word that fits
     the story or `""`; add `points` with icons, a `stat` when the source has a number, a `tip` on about
     half of the stories in the episode)
   - several features / numbers / steps → `ftu-icons`
   - two things, before/after, rival vs rival → `ftu-compare`
   - one big number → a Remocn numbers component + `"visual": {"scene": ..., "place": "top"}` (Short) or `"left"` (episode)
   - a statement/claim/quote → a Remocn typography component + a `visual` (bottom, corner or background)
2. Search: `python3 studio/tools/catalog.py search "<what it shows>" --seed <today>` (add `--section numbers`
   etc. to narrow). Read 3–6 candidates' "use/avoid" lines.
3. `python3 studio/tools/catalog.py show <name>` for the one you pick. Use only props listed there.
   Respect its "Avoid when" lines; they name the better component.
4. Write the beat: component, props (real content, no defaults left as placeholder copy), voice line, tag,
   source, transition.

Variety rules (these are what kill the template look):
- No component twice in one video, except section cards in the long episode (max 3 uses) and the `ftu-*`
  layouts (but never the same `ftu-*` layout on two beats in a row, and never the same illustration
  scene twice in one video).
- Vary `ftu-illus` layouts (`stack`/`full` in a Short; `illus-left`/`illus-right`/`full` in the episode).
- Mix families across a video: at least 3 different sections (e.g. typography, numbers, product-scenes,
  motion-graphics, logo-stings).
- Vary transitions; do not use the same one more than twice in a row.
- Do not reuse the previous video's opener or end card component (check `out/recent.json` titles and, if
  the last run left `studio/out/storyboard-*.json`, its components).
- One accent colour per video: the look of the day (set automatically) unless the story's own subject
  makes another accent clearly better. The long episode uses the weekday show from v1 (Newsroom,
  Countdown, Blueprint Lab, Arcade, World Tour, Classroom, Paper Studio) for its background, palette and
  illustration style; layouts still change per story.

Hook (first beat of every Short): write 3 options, score them with
`python3 tools/ig/hookscore.py hooks.txt` and use the best. A hook states the most surprising concrete
fact in under 3 seconds of speech. Never "Here are today's top AI updates".

## 3. Build, review, fix (the loop that makes it good)

```bash
cd studio
python3 tools/build.py ../storyboard-short.json --repo $REMOCN_DIR    # BUILD_OK + per-beat timing
python3 tools/review.py out/props.json                                 # contact sheets: entry / settled / end per beat
```
View every `out/review/sheet-*.png` with Read. Fix anything in the craft checklist
(`references/craft.md` → "Review checklist") by changing props (usually `scale`, shorter text, another
component) and run build + review again. Two review rounds maximum; if a beat still fails, swap the
component. Then render:

```bash
./render.sh out/props.json out/short.mp4       # ~6 min per minute of video on 2 cores
python3 tools/finish.py ../storyboard-short.json out/props.json out/short.mp4 --kind daily-short
```
`finish.py` writes the cover/thumbnails (frozen frames of your own beats plus a headline) and the post
texts into `engine/out/` with the names `zernio_post.py` expects. Copy `out/props.json` and the
storyboard to `out/storyboard-<kind>.json` before building the next video (the build overwrites them).

Long episode: render it in the background (`run_in_background`), and poll with `sleep 290; ls -la out/`.

## 4. Post

Exactly as the scheduled task says (drafts with `zernio_post.py draft <kinds>`, then `publish` now or
`--at "<date> HH:MM"`). Post only if: the render finished, the Short is ≤ 60 s at 1080x1920 with audio,
the long video is 1920x1080 with audio, and the last review round showed no blocking issue.

## Hard limits

- Free tools only. No paid voices, stock or AI video. No downloaded photos of real people.
- Never imitate a real company's product UI for a *different* company's story; product-scene
  components show generic interfaces. Do not put a company's logo on screen.
- Never show Remocn's own name or logo (the build swaps defaults, but check the frames).
- Sentence case, no ALL-CAPS headlines, no emoji in videos.
- Say "AI & tech updates", never just "AI news".
