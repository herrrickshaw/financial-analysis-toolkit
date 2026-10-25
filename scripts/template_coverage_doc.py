"""Regenerate docs/TEMPLATE_COVERAGE.md from catalog/curated_alternatives.json (run after editing that file)."""
import collections
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "catalog" / "curated_alternatives.json").read_text())
items = data["items"]
GROUPS = {"acct": "Accounting & financial statements", "tvm": "Time value, rates & growth calculators",
          "cost": "Cost & managerial accounting", "port": "Portfolio, trading & risk", "strat": "Strategy frameworks",
          "xl": "Excel functions & learning material", "doc": "Deal, legal & business documents",
          "soft": "Soft-skills diagnostics (outside the toolkit's finance scope)"}
best = collections.Counter(i["sources"][0]["match"] for i in items)
hosts = collections.Counter(urlparse(s["url"]).netloc.replace("www.", "") for i in items for s in i["sources"])
L = ["# Template coverage: other sources and engines for the CFI titles tag matching missed", "",
     f"Generated from `catalog/curated_alternatives.json` ({data['generated']}). These are the {len(items)} CFI dashboard titles "
     "that the model-type tag rules in `finmodel.alternatives` could not match (accounting one-pagers, calculators, Excel-function "
     "demos, documents). For each: free sources of the same template, graded `same` / `close` / `partial`, and the `finmodel` "
     "function that reproduces the calculation where one applies.", "",
     f"- Best available match: **{best['same']} same**, **{best['close']} close**, {best['partial']} partial only.",
     f"- {sum(1 for i in items if i['engine'])} titles name a `finmodel` engine function; the rest are Excel how-tos, documents or soft-skills material.",
     "- Verification: " + data["method"], "",
     "Most-used source sites: " + ", ".join(f"{h} ({n})" for h, n in hosts.most_common(12)) + ".", "",
     "Paid titles have no downloaded CFI file to inspect, so they were matched on title and CFI's page description; "
     "the `what it computes` line says so where relevant. Wall Street Prep and some Microsoft pages refuse scripted "
     "requests and are marked `page-exists, curl-blocked`; Wall Street Prep's Excel files need an email sign-up.", ""]
for g, name in GROUPS.items():
    rows = [i for i in items if i["group"] == g]
    if not rows:
        continue
    L += [f"## {name} ({len(rows)})", "", "| CFI title | Engine | Best source | Match |", "|---|---|---|---|"]
    for i in sorted(rows, key=lambda r: r["title"].lower()):
        s = i["sources"][0]
        eng = f"`{i['engine']}`" if i["engine"] else "—"
        L.append(f"| {i['title']} | {eng} | [{s['title']}]({s['url']}) ({s['source']}, {s['format']}) | {s['match']} |")
    L.append("")
L += ["## Partial matches only", "", "No free source reproduces these templates. Where an engine is named, it is the free equivalent.", ""]
L += [f"- **{i['title']}** — {i.get('note') or i['sources'][0]['match_note']}" + (f" Engine: `finmodel.{i['engine']}`." if i["engine"] else "")
      for i in items if i["sources"][0]["match"] == "partial"]
(ROOT / "docs" / "TEMPLATE_COVERAGE.md").write_text("\n".join(L) + "\n")
print("wrote docs/TEMPLATE_COVERAGE.md")
