# freshtechupdates-engine

Free, watermark-free renderer for the daily **@freshtechupdates** Instagram posts:
a 7-slide carousel (PNG) and a ~35 s vertical Reel (MP4, voiceover + captions + animated scenes).

## Run

```bash
./setup.sh                          # npm deps, free offline voice model, browser check
./make_carousel.sh slides.json      # -> out/carousel/slide-01.png … slide-07.png
./make_reel.sh reel.json            # -> out/freshtechupdates-reel.mp4 (style rotates by weekday)
./make_reel.sh reel.json comic      # force a style: comic | paper | blueprint | neon
```

Weekday rotation (India time): Mon/Wed/Fri/Sun **comic**, Tue/Thu **paper**, Sat **blueprint**.

## slides.json

```json
{"cover":{"kicker":"Top 5 AI & tech updates","headline":"hook, max 7 words, *accent*","teasers":["5 items, max 8 words"]},
 "stories":[{"category":"AI models","icon":"<lucide icon>","headline":"max 8 words, *accent*","body":"max 22 words","source":"domain.com"}]}
```

## reel.json

```json
{"hook":{"headline":"most surprising fact, max 7 words, *accent*","more":"+2 more AI updates","voice":"spoken hook"},
 "stories":[{"category":"AI business","shape":"rocket","headline":"4-6 words, *accent*","source":"domain.com","voice":"14-22 spoken words"}],
 "outro_question":"Which update *surprised* you most?",
 "outro_voice":"Which one surprised you most? Tell me in the comments, and follow freshtechupdates for daily AI news."}
```

`shape` picks the animated scene: rocket (funding/IPO/launch), robot (robotics/agents), shield (security/privacy/regulation),
phone (gadgets/devices), bolt (energy/power), chip (AI models/chips/dev tools), globe (India/policy/global).

See `example-slides.json` and `example-reel.json`.

## Files

- `render.py` – carousel renderer (Playwright screenshots)
- `styreel.py` – Reel in comic / paper / blueprint styles with the FT Bot mascot (HyperFrames)
- `hfreel.py` – earlier neon 3D Reel style (`neon`)
