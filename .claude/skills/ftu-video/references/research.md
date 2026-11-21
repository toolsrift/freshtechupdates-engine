# Research: one pass for the Short, the episode and the explainer

Goal: a ranked list of today's AI & tech stories with evidence, so the videos cover what people are
actually talking about, not just what one search returned.

## 1. History
`python3 zernio_post.py recent` → `out/recent.json` (our last 10 days, both lanes).
`python3 zernio_post.py stats` → `out/perf.json` (views; skipped cleanly if analytics is off).

## 2. Trend signals (WebFetch, in parallel; the shell has no internet)
- `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=40` — "List every hit as: title | points | num_comments | created_at | url"
- `https://www.techmeme.com/` — "List the top 15 headline clusters in page order as: headline | publisher | number of related links shown"
- `https://huggingface.co/api/models?sort=trendingScore&limit=15` — "List each model as: id | likes | downloads | trendingScore | pipeline_tag"
- `https://trends.google.com/trending/rss?geo=IN` and `geo=US` — "List every item as: title | approx_traffic | pubDate | first news item title"

GitHub Trending comes back garbled through WebFetch and the GitHub search API is full of spam clones:
don't use them.

## 3. News sweep (WebSearch, several in parallel)
Last 24–36 hours: model releases (OpenAI, Anthropic, Google, Meta, xAI, Mistral, DeepSeek, Qwen, open
source); developer tools, APIs, pricing; AI image/video/voice tools; big tech launches; gadgets; web dev
(Next.js, React, Vercel, Node, browsers); Google Search/SEO/AdSense; India tech (startups, policy, UPI,
telecom); security; funding, acquisitions, regulation. Fetch the original article when a snippet is thin.
For each story note how many different outlets you saw reporting it, and whether an official source
(company blog, filing, government page) exists.

## 4. signals.json
One item per story per source, all items about the same story sharing one `topic` string:
```json
{"fetched_at": "<now ISO>", "items": [
 {"topic": "Anthropic Nasdaq debut", "source": "techmeme", "title": "...", "url": "...", "links": 34, "rank": 1},
 {"topic": "Anthropic Nasdaq debut", "source": "news", "title": "...", "url": "...", "outlets": 9, "official": true, "published": "..."},
 {"topic": "AI-assisted Riemann proof claim", "source": "hn", "title": "...", "url": "...", "points": 2320, "comments": 1571, "published": "..."}
]}
```
Optional per item: `"pillar"` when the keyword guess is wrong; `"covered": "daily" | "explainer"` when
`out/recent.json` shows we already posted it in other words. Keep only AI & tech (drop sport, celebrity,
politics without a tech angle, plain share-price moves).

## 5. Rank
- Daily run: `python3 trends.py score signals.json --lane daily` → `SHORT_PICKS` (3), `LONG_PICKS` (5–10).
  The episode's length follows `LONG_PICKS`: about 30–45 s per story plus intro and outro.
- Explainer run: `python3 trends.py score signals.json --lane trend` → `TREND_PICK`. Skip a pick that is a
  pure share-price move, a single-source rumour, too niche, or already explained; say why in one line.

## 6. Briefing (daily run only)
"AI & Tech Briefing — <Mon 17 Nov 2026>": Top 3 (2–3 sentences each), AI models & tools, Big tech &
products, Dev & web, India, Worth trying today. Every bullet ends with [Source](URL). Under 600 words.
Paraphrase; quotes under 15 words, one per source.
