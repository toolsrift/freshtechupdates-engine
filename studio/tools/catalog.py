#!/usr/bin/env python3
"""Searchable catalog of Remocn components, built offline from the docs in a Remocn clone.

  python3 tools/catalog.py build --repo ../remocn            -> catalog/catalog.json
  python3 tools/catalog.py search "big number funding" [--section numbers] [--vibe tech] [--max 10] [--seed 2026-11-21]
  python3 tools/catalog.py show counter-reveal               -> description, use/avoid, every prop, the usage example
  python3 tools/catalog.py sections                          -> section names with counts

Search ranks by word overlap with the component's title, description, "use when" and "asked as" lines.
--seed shuffles near-ties differently each day so videos don't keep landing on the same components.
Components that need your own photos/screenshots (they default to demo images we don't have) and
full templates/compositions are marked and left out of search unless --all is given.
"""
import argparse, json, pathlib, random, re, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
CAT = HERE / "catalog" / "catalog.json"
SKIP_SECTIONS = {"templates", "compositions", "getting-started", "guides", "craft", "ai", "icons"}
STOP = set("a an the of to in on for and or with is are be by at as it this that your you from into one two".split())


SCENES = "rocket robot shield phone bolt chip globe chat cloud car money law media code space search glasses"
FTU_ITEMS = [{
    "name": "ftu-illus", "title": "FT illustration hero", "section": "illustration", "group": "freshtechupdates",
    "description": "An animated 3D-sticker illustration scene (with the FT Bot mascot) beside a headline that rises word by word, "
                   "optional big stat and up to 3 icon point chips. Our own component; colours follow the look of the day.",
    "vibe": "playful", "length": "110",
    "useWhen": ["A story beat that needs a rich visual: an illustration of the subject plus the key facts",
                "Robots, agents, rockets, chips, phones, money, law, security, cloud, cars, space, search, media, code, glasses stories",
                "The long episode's main beat per story (headline + 2-3 points with icons)"],
    "avoidWhen": ["A single huge number is the whole beat - use a numbers component (optionally with a `visual`)",
                  "A pure statement or quote - use a typography component"],
    "askedAs": ["illustration", "robot", "icons", "visual", "mascot", "rocket", "points with icons", "rich visual"],
    "props": [
        {"name": "scene", "type": "string", "default": "", "desc": f"Illustration scene (required): {SCENES}"},
        {"name": "headline", "type": "string", "default": "", "desc": "Headline, max 9 words; wrap the key word in *asterisks* for the accent"},
        {"name": "kicker", "type": "string", "default": "", "desc": "Optional small line above the headline (e.g. 'Big tech')"},
        {"name": "points", "type": "{icon, text}[]", "default": "[]", "desc": "Up to 3 points, max 6 words each; icon = any lucide icon name (cpu, shield-check, rocket, globe, dollar-sign, bot, code, smartphone, zap, search...)"},
        {"name": "stat", "type": "{value, label}", "default": "", "desc": "Optional big number from the source, e.g. {value: '$1.3T', label: 'market value'}"},
        {"name": "family", "type": "'flat'|'ink'|'line'", "default": "storyboard illusFamily or flat", "desc": "flat = 3D stickers, ink = comic outlines, line = blueprint drawing"},
        {"name": "label", "type": "string", "default": "scene's own word", "desc": "Sticker word on the scene (e.g. search shows 'RANKED!'): set a word that fits the story, max 14 chars, or \"\" to hide it"},
        {"name": "bot", "type": "boolean", "default": "true", "desc": "Show the FT Bot mascot in the scene"},
        {"name": "pose", "type": "'cheer'|'wave'", "default": "cheer", "desc": "FT Bot pose"},
        {"name": "layout", "type": "'auto'|'illus-left'|'illus-right'|'stack'", "default": "auto", "desc": "auto = stacked in a Short, illustration left in the episode"}],
    "usage": '{"component": "ftu-illus", "props": {"scene": "robot", "kicker": "Big tech", "headline": "Apple is building an *AI agent*", '
             '"points": [{"icon": "code", "text": "Writes code"}, {"icon": "globe", "text": "Browses the web"}, {"icon": "app-window", "text": "Controls your apps"}]}}\n'
             'Any Remocn beat can also carry an illustration: "visual": {"scene": "money", "place": "top|bottom|left|right|corner|background", "family": "flat", "bot": false}',
    "needsMedia": False, "webgl": False, "doc": "studio/src/ftu/IllusHero.tsx"},
  {"name": "ftu-icons", "title": "FT icon grid", "section": "illustration", "group": "freshtechupdates",
   "description": "A list told with icons: 2-6 tiles pop in one by one, each with an icon, a short label and an optional value; optional title, optional illustration and FT Bot tip.",
   "vibe": "data", "length": "40 + 22 per item",
   "useWhen": ["A story with several features, specs, numbers or steps (what's new in a release, what the agent can do, 3 key numbers)",
               "Breaking a long beat into a visual list instead of a talking paragraph"],
   "avoidWhen": ["One fact only - use ftu-illus or a numbers component", "Two things compared - use ftu-compare"],
   "askedAs": ["icons", "list", "features", "grid", "specs", "what's new", "steps"],
   "props": [
     {"name": "title", "type": "string", "default": "", "desc": "Optional title, *accent* word"},
     {"name": "items", "type": "{icon, label, value?}[]", "default": "", "desc": "2-6 items; icon = lucide icon name; label max 5 words; value optional (e.g. '2x', '$20')"},
     {"name": "scene", "type": "string", "default": "", "desc": f"Optional illustration scene: {SCENES}"},
     {"name": "tip", "type": "string", "default": "", "desc": "Optional FT Bot tip, max 16 words"}],
   "usage": '{"component": "ftu-icons", "props": {"title": "What\'s *new* in Gemini 3", "items": [{"icon": "image", "label": "Makes images"}, {"icon": "video", "label": "Edits video"}, {"icon": "zap", "label": "2x faster", "value": "2x"}], "scene": "chip"}}',
   "needsMedia": False, "webgl": False, "doc": "studio/src/ftu/IconGrid.tsx"},
  {"name": "ftu-compare", "title": "FT comparison", "section": "illustration", "group": "freshtechupdates",
   "description": "Two things side by side (stacked in a Short) with an illustration or icon each, a name, a big value and up to 3 facts, with a 'vs' badge.",
   "vibe": "data", "length": "120",
   "useWhen": ["Two products, models, prices, companies or before/after compared", "A rival launch or a price change (old vs new)"],
   "avoidWhen": ["More than two things - use ftu-icons or a chart component"],
   "askedAs": ["versus", "vs", "compare", "before after", "old vs new", "rival"],
   "props": [
     {"name": "title", "type": "string", "default": "", "desc": "Optional title, *accent* word"},
     {"name": "left", "type": "{name, value?, icon?, scene?, facts?}", "default": "", "desc": "First side; scene = illustration (else icon); facts max 3 short lines"},
     {"name": "right", "type": "{name, value?, icon?, scene?, facts?}", "default": "", "desc": "Second side (gets the accent colour)"}],
   "usage": '{"component": "ftu-compare", "props": {"title": "Old price vs *new*", "left": {"name": "Before", "value": "$20", "icon": "tag"}, "right": {"name": "Now", "value": "$8", "icon": "badge-percent", "facts": ["From today", "All plans"]}}}',
   "needsMedia": False, "webgl": False, "doc": "studio/src/ftu/Compare.tsx"}]


def words(t):
    return [w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if w not in STOP and len(w) > 1]


def front(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    fm, body = {}, text[m.end():]
    key = None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+- ", line) and key:
            fm.setdefault(key, []).append(line.strip()[2:].strip().strip('"'))
        elif ":" in line:
            key, v = line.split(":", 1)
            key = key.strip(); v = v.strip().strip('"')
            fm[key] = v if v else []
    return fm, body


def props(body):
    out = []
    for blk in re.findall(r"\{\s*name:\s*\"([^\"]+)\",(.*?)\n\s*\}", body, re.S):
        name, rest = blk
        g = lambda k: (re.search(rf"{k}:\s*\"((?:[^\"\\]|\\.)*)\"", rest) or [None, ""])[1].replace('\\"', '"')
        out.append({"name": name, "type": g("type"), "default": g("default"), "desc": g("description")})
    return out


def build(repo):
    docs = pathlib.Path(repo) / "content" / "docs"
    arts = pathlib.Path(repo) / "registry-artifacts"
    items = []
    for f in sorted(docs.rglob("*.mdx")):
        rel = f.relative_to(docs)
        section = rel.parts[0] if len(rel.parts) > 1 else ""
        if section in SKIP_SECTIONS or f.stem in ("index",):
            continue
        fm, body = front(f.read_text())
        comp = fm.get("component") if isinstance(fm.get("component"), str) else None
        if not comp or not (arts / f"{comp}.json").exists():
            continue
        usage = re.search(r"```tsx\n(.*?)```", body, re.S)
        usage = usage.group(1) if usage else ""
        art = json.loads((arts / f"{comp}.json").read_text())
        deps = art.get("dependencies") or []
        ps = props(body)
        media = bool(re.search(r"staticFile\(|\.(png|jpe?g|webp|mp4)\b", usage)) or any(
            p["name"] in ("src", "image", "images", "covers", "photos", "screenshots", "video") and not p["default"] in ("", "undefined")
            for p in ps)
        items.append({
            "name": comp, "title": fm.get("title", comp), "section": section, "group": "/".join(rel.parts[1:-1]),
            "description": fm.get("description", ""), "vibe": fm.get("vibe", ""), "length": fm.get("length", ""),
            "useWhen": fm.get("useWhen") or [], "avoidWhen": fm.get("avoidWhen") or [], "askedAs": fm.get("askedAs") or [],
            "props": ps, "usage": usage.strip()[:2500], "needsMedia": media,
            "webgl": any("gsh" in x for x in art.get("registryDependencies") or []) or "@paper-design/shaders-react" in deps,
            "doc": str(rel),
        })
    items += FTU_ITEMS
    CAT.parent.mkdir(exist_ok=True)
    CAT.write_text(json.dumps(items, ensure_ascii=False))
    print(f"CATALOG {len(items)} components -> {CAT}")


def load():
    if not CAT.exists():
        sys.exit("CATALOG_ERROR run: python3 tools/catalog.py build --repo <remocn clone>")
    return json.loads(CAT.read_text())


def search(q, section=None, vibe=None, n=10, seed=None, allow_all=False):
    qs = set(words(q))
    rng = random.Random(seed or "")
    rows = []
    for c in load():
        if not allow_all and c["needsMedia"]:
            continue
        if section and c["section"] != section:
            continue
        if vibe and c["vibe"] != vibe:
            continue
        hay = (c["title"] + " " + c["description"] + " " + " ".join(c["useWhen"]) + " " + " ".join(c["askedAs"]) + " " + c["group"])
        ws = words(hay)
        sc = sum(1 for w in qs if w in ws) + 0.5 * sum(1 for w in qs if w in words(c["name"] + " " + c["title"]))
        if sc <= 0:
            continue
        rows.append((sc + rng.random() * 0.9, c))
    rows.sort(key=lambda r: -r[0])
    for sc, c in rows[:n]:
        use = c["useWhen"][0] if c["useWhen"] else ""
        avoid = c["avoidWhen"][0] if c["avoidWhen"] else ""
        print(f"- {c['name']}  [{c['section']}{'/' + c['group'] if c['group'] else ''} · {c['vibe']} · {c['length']}f{' · webgl' if c['webgl'] else ''}]\n"
              f"    {c['description']}\n    use: {use}\n    avoid: {avoid}")
    if not rows:
        print("no match; try fewer or plainer words, or `sections`")


def show(name):
    for c in load():
        if c["name"] == name:
            print(f"# {c['name']} — {c['title']}  [{c['section']} · vibe {c['vibe']} · natural length {c['length']} frames"
                  f"{' · needs WebGL ground' if c['webgl'] else ''}{' · NEEDS MEDIA' if c['needsMedia'] else ''}]")
            print(c["description"])
            print("Use when:"); [print("  - " + x) for x in c["useWhen"]]
            print("Avoid when:"); [print("  - " + x) for x in c["avoidWhen"]]
            print("Props:")
            for p in c["props"]:
                print(f"  {p['name']}: {p['type']} = {p['default']}  — {p['desc']}")
            print("Usage example:\n" + c["usage"])
            return
    sys.exit(f"CATALOG_ERROR no component '{name}'")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--repo", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--section"); s.add_argument("--vibe")
    s.add_argument("--max", type=int, default=10); s.add_argument("--seed"); s.add_argument("--all", action="store_true")
    sh = sub.add_parser("show"); sh.add_argument("name")
    sub.add_parser("sections")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.repo)
    elif a.cmd == "search":
        search(a.query, a.section, a.vibe, a.max, a.seed, a.all)
    elif a.cmd == "show":
        show(a.name)
    else:
        from collections import Counter
        cnt = Counter(c["section"] for c in load() if not c["needsMedia"])
        for k, v in cnt.most_common():
            print(f"{k:<16} {v}")


if __name__ == "__main__":
    main()
