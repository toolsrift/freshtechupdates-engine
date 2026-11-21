# Craft: the quality bar

Adapted from Remocn's anatomy and scene-reviewer guides (github.com/Remocn/remocn, MIT) and the hook and
humanizer rules of github.com/Jakeschincariol/instagram-agent-skill (MIT), for daily news videos.

## Do
- One idea per beat, one focal point on screen. The voice says it; the screen shows it.
- One accent colour per video, used only on the word, number or element that matters.
- Sentence case. Emphasis by weight, accent or a highlight on ONE word, never the whole line.
- Real, specific content: the actual number, name, date or claim from the source.
- Numbers get a numbers component (counter, stat, chart); claims get typography; products in action get
  a product scene; places get a globe/map component.
- Tell a story per video: what happened → why it matters → what to watch. Not a list.
- Tight runtime: cut words before cutting beats; the Short must not run past 60 s.

- Every story beat shows something: an illustration, icons or a number with an illustration. Text-only
  beats only for the hook, section cards and the end card.
- Something moves every 2–3 s: points reveal, FT Bot reacts, the scene animates. Split beats over ~12 s.

## Never
- A repeated look: the same opener, end card, caption style or transition pattern every day.
- Glow halos or large saturated gradient washes added by you; gradient text; ALL-CAPS blocks; decorative
  letter-spacing (components whose effect *is* that are fine).
- Placeholder copy left from component defaults ("remocn", "Studio", "This video took 1 day", "Scene A").
- Walls of text, tiny type, more than ~8 words on screen in a Short beat.
- A product UI of one company used for another company's story; real company logos.
- Invented numbers, quotes, prices or dates.
- Em dashes and AI-slop words in captions and descriptions (`finish.py` runs the humanizer; still write
  plainly).

## Review checklist (each sheet: rows = beats, columns = entry, settled, end)
Blocking (fix before posting):
- `review.py` printed `NO_VISUAL` or `EMPTY` for a beat.
- An illustration's sticker word that doesn't fit the story (set `label`).
- Text cut by the frame edge or a container in the settled/end column.
- Text under ~28 px at 1080 wide, or low contrast against what's behind it.
- A settled frame that is empty, flat colour, or red (= unknown component).
- Captions or the top-left chrome covering the beat's own text.
- Remocn name/logo, placeholder copy, or a wrong fact on screen.
Fix, if quick:
- Two beats in a row that look alike (same layout, same type treatment).
- A fallback system font where a designed face was expected.
- More than one accent colour.
The entry column is often mid-transition; judge it only for obvious breakage.
