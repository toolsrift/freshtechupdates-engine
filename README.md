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
```

The episode render takes ~4 min per minute of video: run it in the background
(`nohup ./make_episode.sh episode.json > out/episode.log 2>&1 &`) and wait for `EPISODE_DONE` in the log.

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
- `zernio_post.py` – uploads the episode, Short and Reel to Zernio as **drafts**, publishes only when approved (key comes from the environment's network secret, never from this repo)
