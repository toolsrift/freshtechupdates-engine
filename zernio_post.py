#!/usr/bin/env python3
"""Post freshtechupdates videos through Zernio (https://zernio.com) — drafts first, publish only after approval.

The API key is NEVER stored here. In the cloud it is attached by the environment's network secret
(host zernio.com, header "Authorization: Bearer <key>"). Locally you can export ZERNIO_API_KEY instead.

  python3 zernio_post.py accounts                       # list connected accounts (id, platform, name)
  python3 zernio_post.py draft [episode] [short] [reel] # upload media + create DRAFT posts (default: all that exist)
  python3 zernio_post.py publish [--at "2026-11-17 18:00"] [episode|short|reel|<postId> ...]
  python3 zernio_post.py status                         # status of today's drafts / posts
  python3 zernio_post.py draft trend-short trend-reel   # trending-explainer lane (made by make_trend.sh)
  python3 zernio_post.py recent [days]                  # our posts of the last N days (default 10) -> out/recent.json
  python3 zernio_post.py stats [days]                   # views per post (default 60 days) -> out/perf.json
                                                        #   needs Zernio analytics; if it is off, writes available:false and exits 0

Inputs (made by make_episode.sh / make_reel.sh): out/freshtechupdates-episode.mp4 + out/thumbnail.png + out/youtube.txt,
out/freshtechupdates-reel.mp4 + out/short-cover.png + out/short.txt, and out/ig-caption.txt (Instagram caption).
Trend lane (make_trend.sh): out/trend-reel.mp4 + out/trend-cover.png + out/trend-short.txt, and out/trend-ig-caption.txt.
Draft ids are saved to out/zernio-drafts.json.
Optional env: ZERNIO_YT_ACCOUNT, ZERNIO_IG_ACCOUNT (account ids; default = first connected account of that platform),
ZERNIO_YT_VISIBILITY (public | unlisted | private, default public).
"""
import json, os, sys, pathlib, mimetypes, urllib.request, urllib.error, datetime

BASE = pathlib.Path(__file__).resolve().parent
OUT = BASE / "out"
API = "https://zernio.com/api/v1"
DRAFTS = OUT / "zernio-drafts.json"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def call(method, path, body=None, raw=None, ctype="application/json", url=None):
    headers = {"Content-Type": ctype, "Accept": "application/json", "User-Agent": "freshtechupdates-engine"}
    key = os.environ.get("ZERNIO_API_KEY")
    if key and not url:
        headers["Authorization"] = f"Bearer {key}"
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url or API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            txt = r.read().decode() or "{}"
            return json.loads(txt) if txt.strip().startswith(("{", "[")) else {"raw": txt}
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:800]
        sys.exit(f"ZERNIO_ERROR {method} {url or path}: HTTP {e.code} {msg}")
    except urllib.error.URLError as e:
        sys.exit(f"ZERNIO_ERROR {method} {url or path}: {e.reason} (is zernio.com allowed in this environment?)")

def try_call(method, path):
    """Like call() but never exits: returns (http_status, json_or_text). Used by recent/stats."""
    headers = {"Accept": "application/json", "User-Agent": "freshtechupdates-engine"}
    key = os.environ.get("ZERNIO_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(API + path, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            txt = r.read().decode() or "{}"
            return r.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else {"raw": txt})
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")[:800]
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"error": txt}
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}

def first_line(txt):
    for line in (txt or "").splitlines():
        if line.strip():
            return line.strip()[:140]
    return ""

def lane_of(title, content=""):
    t = f"{title or ''} {content or ''}".lower()
    return "trend" if ("explained" in (title or "").lower() or "#explained" in t) else "daily"

def recent(days=10):
    since = (datetime.datetime.now(IST) - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    rows, page = [], 1
    while page <= 5:
        code, r = try_call("GET", f"/posts?fromDate={since}&limit=50&page={page}&view=summary")
        if code != 200:
            print(f"ZERNIO_WARN recent: HTTP {code} {str(r)[:200]} (continuing without post history)")
            break
        posts = r.get("posts", []) if isinstance(r, dict) else r
        for x in posts:
            plats = x.get("platforms") or []
            title = x.get("title") or first_line(x.get("content"))
            rows.append({"id": x.get("_id"), "title": title, "lane": lane_of(title, x.get("content")),
                         "status": x.get("status"), "platforms": [y.get("platform") for y in plats],
                         "when": x.get("scheduledFor") or x.get("createdAt")})
        nxt = (r.get("pagination") or {}).get("nextCursor") if isinstance(r, dict) else None
        if not posts or len(posts) < 50 or not nxt:
            break
        page += 1
    OUT.mkdir(exist_ok=True)
    (OUT / "recent.json").write_text(json.dumps({"days": days, "posts": rows}, indent=1, ensure_ascii=False))
    for x in rows:
        print(f'{x["lane"]:<6} {x["status"] or "":<10} {",".join(p or "" for p in x["platforms"]):<18} {x["title"]}')
    print(f"RECENT {len(rows)} posts -> out/recent.json")

def stats(days=60):
    """Views per published post -> out/perf.json, with `rel` = views / median of the same platform + lane,
    so YouTube and Instagram numbers can be compared (used by trends.py for learned pillar weights)."""
    import statistics
    sys.path.insert(0, str(BASE)); from trends import classify
    since = (datetime.datetime.now(IST) - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    rows, page, reason = [], 1, None
    while page <= 6:
        code, r = try_call("GET", f"/analytics?source=late&fromDate={since}&limit=50&page={page}&view=summary")
        if code != 200:
            reason = ("Zernio analytics add-on is not enabled on this account" if code == 402
                      else f"HTTP {code} {str(r)[:200]}")
            break
        posts = r.get("posts", []) if isinstance(r, dict) else []
        now = datetime.datetime.now(datetime.timezone.utc)
        for x in posts:
            a = x.get("analytics") or {}
            pub = x.get("publishedAt")
            try:
                age = (now - datetime.datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 3600
            except Exception:
                age = 0
            content = x.get("content") or ""
            rows.append({"id": x.get("postId") or x.get("_id"), "platform": x.get("platform"),
                         "title": first_line(content), "lane": lane_of(first_line(content), content),
                         "pillar": classify(content), "views": a.get("views"), "likes": a.get("likes"),
                         "comments": a.get("comments"), "published": pub, "age_h": round(age, 1),
                         "url": x.get("platformPostUrl")})
        if len(posts) < 50:
            break
        page += 1
    if reason and not rows:
        (OUT / "perf.json").write_text(json.dumps({"available": False, "reason": reason}, indent=1))
        print(f"STATS_UNAVAILABLE {reason} (trend scoring will run without learned weights)")
        return
    groups = {}
    for x in rows:
        if x["views"] is not None:
            groups.setdefault((x["platform"], x["lane"]), []).append(x["views"])
    med = {k: (statistics.median(v) or 1) for k, v in groups.items()}
    for x in rows:
        if x["views"] is not None:
            x["rel"] = round(x["views"] / med[(x["platform"], x["lane"])], 3)
    summary = {f"{k[0]}/{k[1]}": {"posts": len(groups[k]), "median_views": med[k]} for k in sorted(groups, key=str)}
    OUT.mkdir(exist_ok=True)
    (OUT / "perf.json").write_text(json.dumps({"available": True, "days": days, "summary": summary, "posts": rows}, indent=1, ensure_ascii=False))
    for k, v in summary.items():
        print(f"{k:<20} posts={v['posts']:<4} median views={v['median_views']}")
    top = sorted((x for x in rows if x.get("views") is not None), key=lambda x: -x["views"])[:5]
    for x in top:
        print(f'TOP {x["views"]:>7} {x["platform"]:<10} {x["lane"]:<6} {x["title"]}')
    print(f"STATS {len(rows)} posts -> out/perf.json")

def accounts():
    r = call("GET", "/accounts")
    items = r if isinstance(r, list) else r.get("accounts") or r.get("data") or []
    out = []
    for a in items:
        out.append(dict(id=a.get("_id") or a.get("id"), platform=a.get("platform"),
                        name=a.get("username") or a.get("displayName") or a.get("name") or ""))
    return out

def account_for(platform):
    env = {"youtube": "ZERNIO_YT_ACCOUNT", "instagram": "ZERNIO_IG_ACCOUNT"}[platform]
    if os.environ.get(env): return os.environ[env]
    for a in accounts():
        if a["platform"] == platform: return a["id"]
    sys.exit(f"ZERNIO_ERROR no connected {platform} account in Zernio (connect it in the Zernio dashboard)")

def upload(path):
    path = pathlib.Path(path)
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    p = call("POST", "/media/presign", {"filename": path.name, "contentType": ctype})
    call("PUT", "", raw=path.read_bytes(), ctype=ctype, url=p["uploadUrl"])
    print(f"uploaded {path.name} ({path.stat().st_size/1e6:.1f} MB)")
    return p["publicUrl"]

def sections(txt_path):
    """Parse TITLE:/DESCRIPTION:/TAGS: blocks from youtube.txt / short.txt."""
    cur, out = None, {}
    for line in pathlib.Path(txt_path).read_text().splitlines():
        h = line.strip().rstrip(":").upper()
        if line.strip().endswith(":") and h in ("TITLE", "DESCRIPTION", "TAGS"):
            cur = h; out[cur] = []; continue
        if line.startswith("SHOW:"): cur = None; continue
        if cur: out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}

def post_id(r):
    p = r.get("post", r)
    return p.get("_id") or p.get("id")

def make_draft(kind):
    if kind == "episode":
        mp4, txt = OUT / "freshtechupdates-episode.mp4", OUT / "youtube.txt"
        if not mp4.exists(): return None
        s = sections(txt); tags = [t.strip() for t in s.get("TAGS", "").split(",") if t.strip()]
        media = {"type": "video", "url": upload(mp4)}
        if (OUT / "thumbnail.png").exists(): media["thumbnail"] = upload(OUT / "thumbnail.png")
        body = {"content": s["DESCRIPTION"], "tags": tags, "isDraft": True, "mediaItems": [media],
                "platforms": [{"platform": "youtube", "accountId": account_for("youtube"),
                               "platformSpecificData": {"title": s["TITLE"][:100], "visibility": os.environ.get("ZERNIO_YT_VISIBILITY", "public"),
                                                        "categoryId": "28", "madeForKids": False}}]}
    elif kind in ("short", "trend-short"):
        mp4, txt = ((OUT / "freshtechupdates-reel.mp4", OUT / "short.txt") if kind == "short"
                    else (OUT / "trend-reel.mp4", OUT / "trend-short.txt"))
        if not mp4.exists(): return None
        s = sections(txt)
        body = {"content": s["DESCRIPTION"], "isDraft": True, "mediaItems": [{"type": "video", "url": upload(mp4)}],
                "platforms": [{"platform": "youtube", "accountId": account_for("youtube"),
                               "platformSpecificData": {"title": s["TITLE"][:100], "visibility": os.environ.get("ZERNIO_YT_VISIBILITY", "public"),
                                                        "categoryId": "28", "madeForKids": False}}]}
    else:  # reel | trend-reel
        trend = kind == "trend-reel"
        mp4 = OUT / ("trend-reel.mp4" if trend else "freshtechupdates-reel.mp4")
        cap = OUT / ("trend-ig-caption.txt" if trend else "ig-caption.txt")
        cover = OUT / ("trend-cover.png" if trend else "short-cover.png")
        if not mp4.exists(): return None
        if not cap.exists(): sys.exit(f"ZERNIO_ERROR out/{cap.name} missing (write the Instagram caption there first)")
        media = {"type": "video", "url": upload(mp4)}
        if cover.exists(): media["instagramThumbnail"] = upload(cover)
        body = {"content": cap.read_text().strip(), "isDraft": True, "mediaItems": [media],
                "platforms": [{"platform": "instagram", "accountId": account_for("instagram")}]}
    r = call("POST", "/posts", body)
    pid = post_id(r)
    print(f"DRAFT {kind}: {pid}")
    return {"kind": kind, "id": pid, "created": datetime.datetime.now(IST).isoformat(timespec="minutes")}

def load():
    return json.loads(DRAFTS.read_text()) if DRAFTS.exists() else []

def main():
    a = sys.argv[1:] or ["status"]
    cmd, rest = a[0], a[1:]
    if cmd == "accounts":
        for x in accounts(): print(f'{x["platform"]:<12} {x["id"]}  {x["name"]}')
    elif cmd == "draft":
        kinds = rest or ["episode", "short", "reel"]
        done = [d for d in load() if d["kind"] not in kinds]
        for k in kinds:
            d = make_draft(k)
            if d: done.append(d)
        DRAFTS.write_text(json.dumps(done, indent=1))
        print("ZERNIO_DRAFTS " + " ".join(f'{d["kind"]}={d["id"]}' for d in done))
    elif cmd == "publish":
        at = None
        if rest[:1] == ["--at"]:
            at = datetime.datetime.strptime(rest[1], "%Y-%m-%d %H:%M").replace(tzinfo=IST); rest = rest[2:]
        drafts = load(); kinds = {d["kind"]: d["id"] for d in drafts}
        ids = [kinds.get(x, x) for x in rest] if rest else [d["id"] for d in drafts]
        if not ids: sys.exit("ZERNIO_ERROR nothing to publish (no drafts recorded; pass post ids)")
        for pid in ids:
            body = {"isDraft": False, "timezone": "Asia/Kolkata"}
            if at: body["scheduledFor"] = at.isoformat()
            else: body["publishNow"] = True
            call("PUT", f"/posts/{pid}", body)
            print(f"{'SCHEDULED ' + at.strftime('%d %b %H:%M IST') if at else 'PUBLISHING'} {pid}")
    elif cmd == "recent":
        recent(int(rest[0]) if rest else 10)
    elif cmd == "stats":
        stats(int(rest[0]) if rest else 60)
    elif cmd == "status":
        for d in load():
            r = call("GET", f'/posts/{d["id"]}'); p = r.get("post", r)
            plats = ", ".join(f'{x.get("platform")}: {x.get("status", "")} {x.get("platformPostUrl", "") or ""}'.strip() for x in p.get("platforms", []))
            print(f'{d["kind"]:<8} {d["id"]}  {p.get("status", "")}  {plats}')
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main()
