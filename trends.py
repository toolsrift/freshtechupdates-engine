#!/usr/bin/env python3
"""Pick today's trending AI & tech topic for the explainer Short.

  python3 trends.py score signals.json [--lane trend|daily] [--recent out/recent.json] [--perf out/perf.json] [--top 8]
      -> prints a ranked table and writes out/trend-pick.json (ranked topics with their evidence)
         --lane daily also prints SHORT_PICKS (top 3) and LONG_PICKS (5-10 stories, by strength) for the daily videos
  python3 trends.py classify "any headline text"     -> prints the content pillar

signals.json is written by the scheduled run from WebFetch / WebSearch results (the shell has no open
internet here), one item per trending story, grouped by `topic` (the same short name for every item that
is about the same thing):

  {"fetched_at": "2026-11-21T07:00:00+05:30",
   "items": [{"topic": "AI claims Riemann Hypothesis proof", "source": "hn", "title": "...", "url": "...",
              "points": 2320, "comments": 1571, "published": "2026-11-20T14:16:21Z"},
             {"topic": "...", "source": "techmeme", "title": "...", "url": "...", "links": 34, "rank": 1},
             {"topic": "...", "source": "hf", "title": "Qwen/Qwen3.8-27B", "url": "...", "trending": 235, "likes": 20788},
             {"topic": "...", "source": "gtrends", "geo": "IN", "title": "...", "traffic": "5000+"},
             {"topic": "...", "source": "news", "title": "...", "url": "...", "outlets": 4, "official": true,
              "published": "2026-11-20T18:00:00Z"},
             {"topic": "...", "source": "search", "title": "...", "url": "..."}]}

Scoring (ideas ported from darkzOGx/youtube-automation-agent: content-strategy-agent's merged trend score
and channel-learning-engine's baseline comparison, rebuilt for free sources and no database):
  1. Each item gets a 0..1 strength *within its own source* (log-scaled engagement, or rank on Techmeme),
     so 2,000 HN points and 34 Techmeme links are comparable.
  2. A topic's score = sum of its items' strength x source weight, x a cross-source bonus
     (seen on 2 sources = 1.5x, 3 = 2x) — a topic trending in several places beats a niche spike.
  3. x recency (half-life 18 h from the newest item).
  4. x novelty, against our posts of the last 10 days (`zernio_post.py recent`): a topic we already made an
     explainer about -> 0.15x; a topic the daily updates already covered -> 0.6x (an explainer can still go
     deeper). The run can also mark an item "covered": "explainer" | "daily" when the wording differs.
  5. x learned pillar weight from our own results (`zernio_post.py stats`): median views of past explainer
     Shorts in that pillar vs the median of all of them, square-rooted and clamped to 0.75..1.35, and only
     when that pillar has 3+ measured posts (like the agent's "reliable only" rule). No data -> 1.0.
"""
import json, math, re, sys, pathlib, datetime, statistics

BASE = pathlib.Path(__file__).resolve().parent
OUT = BASE / "out"

SOURCE_WEIGHT = {"techmeme": 1.0, "hn": 1.0, "hf": 0.6, "gtrends": 0.8, "news": 1.0, "search": 0.5, "producthunt": 0.6}
HALF_LIFE_H = 18.0

# Content pillars: one place to keep "what kind of story is this" for scoring and learning.
PILLARS = [
    ("ai-models", r"\b(gpt|claude|gemini|llama|qwen|deepseek|mistral|grok|model|llm|weights|open[- ]source model|benchmark|reasoning)\b"),
    ("ai-media", r"\b(video|image|voice|music|audio|text-to|sora|veo|midjourney|tts|avatar)\b"),
    ("ai-agents", r"\b(agent|agents|agentic|automation|computer use|copilot|assistant)\b"),
    ("security", r"\b(hack|breach|leak|scam|malware|ransomware|security|privacy|vulnerab|cyber|phishing)\b"),
    ("money", r"\b(ipo|funding|raises|valuation|acquir|acquisition|stock|shares|market cap|revenue|earnings|sec)\b"),
    ("policy", r"\b(law|ban|court|regulat|government|policy|antitrust|lawsuit|fine|senate|ministry)\b"),
    ("gadgets", r"\b(iphone|pixel|galaxy|phone|laptop|watch|glasses|headset|vision pro|wearable|console|switch)\b"),
    ("chips", r"\b(chip|gpu|nvidia|tpu|cpu|semiconductor|tsmc|data cent)\b"),
    ("dev", r"\b(github|api|developer|code|coding|programming|framework|javascript|python|rust|browser|linux|open source)\b"),
    ("science", r"\b(math|proof|hypothesis|physics|space|nasa|esa|quantum|research|paper|biology|climate)\b"),
    ("india", r"\b(india|indian|upi|jio|airtel|bengaluru|hyderabad|isro|meity)\b"),
]

STOP = set("the a an of to in on for and or with is are was be by at from as its it this that new how why what who "
           "can could will just now today you your our about over into after says said vs via".split())


def classify(text):
    t = (text or "").lower()
    for name, pat in PILLARS:
        if re.search(pat, t):
            return name
    return "big-tech"


def tokens(text):
    return {w for w in re.findall(r"[a-z0-9][a-z0-9.+-]{2,}", (text or "").lower()) if w not in STOP}


def parse_time(s):
    if not s:
        return None
    try:
        s = str(s).strip().replace("Z", "+00:00")
        d = datetime.datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        for fmt in ("%a, %d %b %Y %H:%M:%S %z",):
            try:
                return datetime.datetime.strptime(s, fmt)
            except ValueError:
                pass
    return None


def traffic_num(v):
    if v is None:
        return 0.0
    m = re.match(r"\s*([\d.,]+)\s*([kKmM]?)", str(v))
    if not m:
        return 0.0
    n = float(m.group(1).replace(",", ""))
    return n * {"k": 1e3, "m": 1e6}.get(m.group(2).lower(), 1)


def raw_strength(it):
    src = it.get("source")
    if src == "hn":
        return float(it.get("points") or 0) + 0.5 * float(it.get("comments") or 0)
    if src == "techmeme":
        # bigger clusters = more outlets covering it; rank 1 = lead story
        links = float(it.get("links") or 0)
        rank = float(it.get("rank") or 15)
        return links + max(0.0, 16 - rank) * 2
    if src == "hf":
        return float(it.get("trending") or 0) + 0.01 * float(it.get("likes") or 0)
    if src == "gtrends":
        return traffic_num(it.get("traffic"))
    if src == "news":
        # a news story found by WebSearch: how many different outlets reported it (and a bonus for an official source)
        return float(it.get("outlets") or 1) + (2.0 if it.get("official") else 0.0)
    if src == "producthunt":
        return float(it.get("votes") or 0)
    return 1.0  # search hits: presence only


def normalise(items):
    """0..1 strength within each source (log scale relative to that source's max)."""
    by = {}
    for it in items:
        by.setdefault(it.get("source", "search"), []).append(it)
    for src, group in by.items():
        vals = [math.log1p(max(0.0, raw_strength(x))) for x in group]
        top = max(vals) if vals else 0
        for x, v in zip(group, vals):
            x["_strength"] = (v / top) if top > 0 else 0.5


def recent_posts(path):
    """[(title, lane)] from `zernio_post.py recent` (lane: trend | daily)."""
    if not path or not pathlib.Path(path).exists():
        return []
    data = json.loads(pathlib.Path(path).read_text())
    rows = (data.get("posts") if isinstance(data, dict) else data) or []
    return [(r.get("title") or r.get("content") or "", r.get("lane") or lane_of(r.get("title"), r.get("content"))) for r in rows]


def lane_of(title, content=""):
    t = f"{title or ''} {content or ''}".lower()
    return "trend" if ("explained" in (title or "").lower() or "#explained" in t) else "daily"


def overlap(topic, title):
    a, b = tokens(topic), tokens(title)
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def pillar_weights(perf_path):
    """Learned multipliers from our own explainer Shorts (see `zernio_post.py stats`)."""
    if not perf_path or not pathlib.Path(perf_path).exists():
        return {}, "no performance file"
    perf = json.loads(pathlib.Path(perf_path).read_text())
    if not perf.get("available"):
        return {}, perf.get("reason", "analytics unavailable")
    # rel = views / median of the same platform + lane (set by zernio_post.py stats), so YouTube and
    # Instagram posts can be pooled. Only posts at least 24 h old count (early numbers are noise).
    rows = [p for p in perf.get("posts", []) if p.get("lane") == "trend" and p.get("rel") is not None and p.get("age_h", 0) >= 24]
    if len(rows) < 6:
        return {}, f"only {len(rows)} measured explainer posts (need 6+)"
    out = {}
    for name in {r["pillar"] for r in rows}:
        vs = [r["rel"] for r in rows if r["pillar"] == name]
        if len(vs) >= 3:
            out[name] = round(max(0.75, min(1.35, math.sqrt(max(statistics.median(vs), 0.01)))), 3)
    return out, f"{len(rows)} measured explainer posts"


def score(signals, recent=None, perf=None, top=8, lane="trend"):
    items = [dict(x) for x in signals.get("items", []) if x.get("topic")]
    if not items:
        sys.exit("TRENDS_ERROR signals.json has no items with a topic")
    normalise(items)
    now = parse_time(signals.get("fetched_at")) or datetime.datetime.now(datetime.timezone.utc)
    posted = recent_posts(recent)
    weights, learn_note = pillar_weights(perf)

    topics = {}
    for it in items:
        key = it["topic"].strip()
        t = topics.setdefault(key, {"topic": key, "items": [], "sources": set(), "base": 0.0, "newest": None})
        t["items"].append(it)
        t["sources"].add(it.get("source", "search"))
        t["base"] += it["_strength"] * SOURCE_WEIGHT.get(it.get("source"), 0.5)
        ts = parse_time(it.get("published"))
        if ts and (t["newest"] is None or ts > t["newest"]):
            t["newest"] = ts

    ranked = []
    for t in topics.values():
        n_src = len(t["sources"])
        cross = 1.0 + 0.5 * (n_src - 1)
        age_h = (now - t["newest"]).total_seconds() / 3600 if t["newest"] else 12.0
        recency = 0.5 ** (max(0.0, age_h) / HALF_LIFE_H)
        text = t["topic"] + " " + " ".join(i.get("title", "") for i in t["items"])
        pillar = next((i["pillar"] for i in t["items"] if i.get("pillar")), None) or classify(text)
        marks = {i.get("covered") for i in t["items"]}
        seen_trend = "explainer" in marks or any(lane == "trend" and overlap(t["topic"], x) >= 0.6 for x, lane in posted)
        seen_daily = "daily" in marks or any(lane == "daily" and overlap(t["topic"], x) >= 0.6 for x, lane in posted)
        if lane == "daily":   # the daily updates must not repeat yesterday's updates; an explainer topic is fine to update
            novelty = 0.3 if seen_daily else (0.85 if seen_trend else 1.0)
        else:
            novelty = 0.15 if seen_trend else (0.6 if seen_daily else 1.0)
        learned = weights.get(pillar, 1.0)
        final = t["base"] * cross * recency * novelty * learned
        ranked.append({
            "topic": t["topic"], "score": round(final, 3), "pillar": pillar,
            "sources": sorted(t["sources"]), "age_h": round(age_h, 1),
            "factors": {"base": round(t["base"], 3), "cross_source": cross, "recency": round(recency, 3),
                        "novelty": novelty, "learned": round(learned, 3)},
            "already_posted": "explainer" if seen_trend else ("daily" if seen_daily else None),
            "evidence": [{k: i.get(k) for k in ("source", "title", "url", "points", "comments", "links", "traffic", "trending") if i.get(k) is not None}
                         for i in sorted(t["items"], key=lambda i: -i["_strength"])][:6],
        })
    ranked.sort(key=lambda r: -r["score"])
    result = {"generated_at": now.isoformat(), "lane": lane, "learning": learn_note, "pillar_weights": weights, "ranked": ranked[:top]}
    if lane == "daily":
        # Short = the 3 strongest; long episode = every story at >= 25% of the top score (5..10), so its length follows the news
        good = [r for r in ranked if not r["already_posted"] or r["already_posted"] == "explainer"]
        result["short_picks"] = [r["topic"] for r in good[:3]]
        cut = (good[0]["score"] * 0.25) if good else 0
        longp = [r for r in good if r["score"] >= cut][:10]
        if len(longp) < 5:
            longp = good[:5]
        result["long_picks"] = [r["topic"] for r in longp]
    OUT.mkdir(exist_ok=True)
    (OUT / "trend-pick.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(f"learning: {learn_note}")
    for k, r in enumerate(ranked[:top], 1):
        flag = f"  (already covered: {r['already_posted']})" if r["already_posted"] else ""
        print(f"{k:>2}. {r['score']:6.3f}  {r['pillar']:<10} {'+'.join(r['sources']):<22} {r['age_h']:>5.1f}h  {r['topic']}{flag}")
    if lane == "daily":
        print("SHORT_PICKS " + " | ".join(result["short_picks"]))
        print("LONG_PICKS " + " | ".join(result["long_picks"]) + f"   ({len(result['long_picks'])} stories)")
    else:
        print("TREND_PICK " + (ranked[0]["topic"] if ranked else ""))
    return result


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "classify":
        print(classify(" ".join(a[1:])))
        return
    if a[0] != "score" or len(a) < 2:
        sys.exit(__doc__)
    opts = {"--recent": str(OUT / "recent.json"), "--perf": str(OUT / "perf.json"), "--top": "8", "--lane": "trend"}
    rest = a[2:]
    for i in range(0, len(rest) - 1, 2):
        if rest[i] in opts:
            opts[rest[i]] = rest[i + 1]
    top = max(int(opts["--top"]), 14 if opts["--lane"] == "daily" else 0)
    score(json.loads(pathlib.Path(a[1]).read_text()), opts["--recent"], opts["--perf"], top, opts["--lane"])


if __name__ == "__main__":
    main()
