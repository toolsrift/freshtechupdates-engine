# freshtechupdates-engine

Free, watermark-free renderer for the daily **@freshtechupdates** content:
- a **3–5 min YouTube episode** (16:9, continuous-camera motion graphics, two voices, music, chapters, thumbnail, metadata)
- a ~40 s vertical **Short/Reel** that ends with a "watch the full episode" card
- a 7-slide Instagram **carousel** (PNG)

## Run

```bash
./setup.sh                          # npm deps, free offline voice model, browser check
./make_carousel.sh slides.json      # -> out/carousel/slide-01.png … slide-07.png
./make_reel.sh reel.json            # -> out/freshtechupdates-reel.mp4 + out/short-cover.png + out/short.txt
./make_reel.sh reel.json comic      # force a style: comic | paper | blueprint | neon
./make_episode.sh episode.json      # -> out/freshtechupdates-episode.mp4 + 3 thumbnails (A/B/C) + out/youtube.txt
./make_episode.sh episode.json 4    # force a show (1-7)
./make_trend.sh trend.json          # trending explainer Short -> out/trend-reel.mp4 (see "Trending explainer lane")
```

The episode render takes ~4 min per minute of video: run it in the background
(`nohup ./make_episode.sh episode.json > out/episode.log 2>&1 &`) and wait for `EPISODE_DONE` in the log.

## Trending explainer lane (second daily Short)

One hot AI & tech topic a day, explained in ~40 s in three beats (**What it is → Why now → For you**).
Posted as a YouTube Short + Instagram Reel, separate from the daily updates.

```bash
python3 zernio_post.py recent           # our last 10 days of posts -> out/recent.json (so we don't repeat a topic)
python3 zernio_post.py stats            # views per post -> out/perf.json (skipped cleanly if Zernio analytics is off)
python3 trends.py score signals.json    # ranks today's topics -> out/trend-pick.json, prints TREND_PICK <topic>
./make_trend.sh trend.json              # -> out/trend-reel.mp4 + out/trend-cover.png + out/trend-short.txt
python3 zernio_post.py draft trend-short trend-reel   # needs out/trend-ig-caption.txt
python3 zernio_post.py publish trend-short trend-reel
```

**signals.json** is written by the scheduled run from WebFetch results (Hacker News front page via the Algolia API,
Techmeme, Hugging Face trending models, Google Trends IN/US RSS). Items about the same story share one `topic`.
Format and scoring rules are at the top of `trends.py`: per-source normalisation, cross-source bonus, 18 h recency
half-life, a penalty for topics we already covered, and learned pillar weights from our own view counts
(only once 6+ explainer posts are 24 h+ old; clamped to 0.75–1.35x). Scoring ideas adapted from
[darkzOGx/youtube-automation-agent](https://github.com/darkzOGx/youtube-automation-agent) (MIT).

**trend.json** — same shape as reel.json plus `"mode": "explainer"`, a `label` per beat and the source URLs:

```json
{"mode":"explainer","topic":"short name","title":"YouTube title, max 70 chars, ends with 'explained'",
 "hook":{"headline":"max 7 words, *accent*","more":"Explained in 40 seconds","voice":"1-2 spoken sentences"},
 "stories":[{"label":"What it is","category":"1-2 words","shape":"<scene>","headline":"4-6 words, *accent*","source":"domain.com","voice":"16-24 words"},
            {"label":"Why now", "...":"voice starts with 'Next.'"},
            {"label":"For you", "...":"voice starts with 'And finally.'"}],
 "outro_question":"max 6 words, *accent*","outro_voice":"question + Tell me in the comments.",
 "sources":["https://..."]}
```

The style rotates one step ahead of the daily Short so both Shorts on the same day look different
(trend: Mon/Wed/Fri paper · Tue/Thu/Sat comic · Sun blueprint). The end card says "Follow for daily explainers".
See `example-trend.json`.

## Daily YouTube shows (rotate by weekday, India time)

| Day | Show | Look | Camera move between stories |
|---|---|---|---|
| Mon | The Newsroom | dark navy, red ticker | whip-pan with motion blur |
| Tue | The Countdown | purple neon, #N to #1 | zoom out over the map, dive into the next |
| Wed | Blueprint Lab | blueprint, line-drawn | smooth pan along a drawn line |
| Thu | Update Arcade | comic panels, "LEVEL" | hop up and land |
| Fri | World Tour | dark teal map | flight arc |
| Sat | The Classroom | chalkboard | slide along the board |
| Sun | Paper Studio | paper cut-outs | rotate between pinned pages |

Music (generated in code) changes chord progression by date, so the same show never sounds identical two weeks running.

Inside each episode the stories also change layout (never the same twice in a row):
**split** (text + illustration), **hero** (huge illustration, headline banner, floating point cards),
**big type** (giant headline, numbered chips), **steps** (points on a timeline the camera pans along),
**big number** (count-up stat — used when a story has a real `stat`).

## episode.json

```json
{"title":"YouTube title, max 70 chars","summary":"1-2 sentences","thumb_text":"max 5 words, *accent*",
 "hook_voice":"1-2 sentences teasing the top updates",
 "stories":[{"category":"AI tools","headline":"max 9 words, *accent*","scene":"chat",
   "voice":"60-90 spoken words","points":["max 7 words","max 7 words","max 7 words"],
   "stat":{"value":"$2B+","label":"what the number means"},
   "bot":"optional one-line FT Bot reaction or tip","source":"Publication"}],
 "question":"Which update *surprised* you most?",
 "outro_voice":"Which story surprised you most? Tell me in the comments, and subscribe for daily AI and tech updates.",
 "tags":["..."]}
```

5–8 stories, most important first. `stat` is optional: only a real number from the source.
`scene` (see `illus.py`, 17 animated illustrations with depth, a lit stage and characters; the same names work as `shape` in reel.json):
rocket (launches, growth) · robot (robotics, agents) · shield (security, scams) · phone (phones, gadgets) · bolt (energy, data centres) ·
chip (AI models, chips) · globe (global, India, policy) · chat (chatbots, assistants) · cloud (cloud, servers) · car (EVs, self-driving) ·
money (funding, IPO, deals) · law (regulation, courts, bans) · media (image/video/music AI) · code (developer tools, web) ·
space (satellites, telecom) · search (Google Search, SEO) · glasses (wearables, AR/VR). See `example-episode.json`.

Weekday rotation (India time): Mon/Wed/Fri/Sun **comic**, Tue/Thu **paper**, Sat **blueprint**.

## slides.json

```json
{"cover":{"kicker":"Top 5 AI & tech updates","headline":"hook, max 7 words, *accent*","teasers":["5 items, max 8 words"]},
 "stories":[{"category":"AI models","icon":"<lucide icon>","headline":"max 8 words, *accent*","body":"max 22 words","source":"domain.com"}]}
```

## reel.json

```json
{"hook":{"headline":"most surprising fact, max 7 words, *accent*","more":"+2 more AI & tech updates","voice":"spoken hook"},
 "stories":[{"category":"AI business","shape":"rocket","headline":"4-6 words, *accent*","source":"domain.com","voice":"14-22 spoken words"}],
 "outro_question":"Which update *surprised* you most?",
 "outro_voice":"Which one surprised you most? Tell me in the comments, and follow freshtechupdates for daily AI & tech updates."}
```

`shape` picks the animated scene: rocket (funding/IPO/launch), robot (robotics/agents), shield (security/privacy/regulation),
phone (gadgets/devices), bolt (energy/power), chip (AI models/chips/dev tools), globe (India/policy/global).

See `example-slides.json` and `example-reel.json`.

## Files

- `render.py` – carousel renderer (Playwright screenshots)
- `styreel.py` – Reel in comic / paper / blueprint styles with the FT Bot mascot (HyperFrames)
- `hfreel.py` – earlier neon 3D Reel style (`neon`)
- `longform.py` – daily YouTube episode engine (7 shows, thumbnail, YouTube metadata)
- `ftlogo.py` – the 3D FT logo as inline SVG
- `illus.py` – illustration library v2 (used by the episodes and the Reel)
- `thumbs.py` – YouTube thumbnails (3 designs for Test & Compare) and the Short/Reel cover
- `trends.py` – trending-topic scorer for the explainer lane
- `make_trend.sh` – renders the explainer Short (uses `styreel.py` in explainer mode)
- `zernio_post.py` – uploads the episode, Short and Reel to Zernio as **drafts**, publishes only when approved (key comes from the environment's network secret, never from this repo)
