#!/usr/bin/env python3
"""Fetch snippet (title, description, tags, publish date) for all shorts via YouTube Data API v3.

Key is read from env YOUTUBE_DATA_API_KEY (never printed). Usage:
  set -a; source ~/.config/market-secrets/credentials.env; set +a; python3 fetch_descriptions.py
Output: yt/descriptions.json and yt/descriptions.tsv
"""
import csv, json, os, sys, urllib.parse, urllib.request

key = os.environ.get("YOUTUBE_DATA_API_KEY") or os.environ.get("YOUTUBE_API_KEY")
if not key:
    sys.exit("YOUTUBE_DATA_API_KEY not set in environment")

ids = [r["video_id"] for r in csv.DictReader(open("abhinavsayshi_shorts_inventory.csv"))]
out = {}
for i in range(0, len(ids), 50):
    chunk = ids[i:i + 50]
    q = urllib.parse.urlencode({"part": "snippet,statistics", "id": ",".join(chunk), "key": key, "maxResults": 50})
    with urllib.request.urlopen(f"https://www.googleapis.com/youtube/v3/videos?{q}", timeout=60) as r:
        data = json.load(r)
    for it in data.get("items", []):
        sn = it["snippet"]; st = it.get("statistics", {})
        out[it["id"]] = {
            "title": sn.get("title"), "description": sn.get("description", ""),
            "tags": sn.get("tags", []), "published": sn.get("publishedAt"),
            "views": st.get("viewCount"), "likes": st.get("likeCount"), "comments": st.get("commentCount"),
        }
    print(f"fetched {len(out)}/{len(ids)}")

json.dump(out, open("yt/descriptions.json", "w"), ensure_ascii=False, indent=1)
with open("yt/descriptions.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["video_id", "published", "title", "description", "tags"])
    for vid in ids:
        d = out.get(vid, {})
        w.writerow([vid, d.get("published"), d.get("title"), (d.get("description") or "").replace("\n", " ⏎ "), "|".join(d.get("tags", []))])
missing = [v for v in ids if v not in out]
print("missing:", missing)
