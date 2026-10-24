"""Map CFI template titles (especially the paid-only ones) to public alternatives in the catalog.

Both sides are tagged with model-type keywords; a CFI title matches a public entry when they share
a tag.  Tags are deliberately coarse ("lbo", "dcf", "comps", "bank", ...) — the goal is a shortlist
of industry-standard equivalents, not an exact clone.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from .catalog import CATALOG_DIR, load

# tag -> regex over lower-cased title / filename
TAG_RULES: Dict[str, str] = {
    "3-statement": r"3[- ]statement|three[- ]statement|ifs_|statmnts|operating model|financial model|projection|forecast|budget",
    "dcf": r"\bdcf\b|discounted cash flow|fcff|fcfe|intrinsic|valuation model|business valuation|unlevered free cash|npv|xnpv",
    "ddm": r"dividend discount|\bddm|divginzu|h-model",
    "lbo": r"\blbo\b|leveraged buyout|buyout",
    "m&a": r"m&a|merger|acquisition|synergy|combination|consolidation|accretion|exchange ratio|purchase price",
    "comps": r"comps|comparable|precedent|multiple|ev/ebitda|ev to|trading comp|transaction comp",
    "wacc": r"wacc|cost of capital|cost of debt|cost of equity|beta|capm|risk premium|ratings|synthetic rating|levbeta|unlevered cost",
    "capital-structure": r"capital structure|capstru|apv|adjusted present value|debt capacity|leverage|optimal",
    "ratios": r"ratio|turnover|margin|coverage|liquidity|dupont|common size|trend analysis|benchmark|days sales|days inventory",
    "bank": r"\bbank|fig\b|net interest|risk weighted|capital adequacy|insurance|allstate|progressive|financial institution|eqexret",
    "real-estate": r"reit|real estate|cap rate|noi|rent multiplier|reval|price per square",
    "options": r"black[- ]scholes|option|warrant|greeks|put call|binomial|bstobin",
    "capital-budgeting": r"capital budget|capbudg|capital investment|payback|profitability index|irr|crossover|npv",
    "startup": r"saas|ecommerce|e-commerce|startup|pitch|cap table|capitalization table|pre-money|burn rate|ltv|rule of 40|venture|vc",
    "sensitivity": r"sensitivity|scenario|data table|monte carlo|goal seek|solver",
    "charts": r"football field|waterfall|chart|dashboard|graph",
    "energy-mining": r"mining|energy|solar|levelized|natres|natural resource|oil",
    "restructuring": r"restructuring|distress|troubled|bankruptcy|liquidation|normearn",
    "working-capital": r"working capital|nwc|cash conversion|cash budget|monthly cash|rollforward",
    "eva-returns": r"\beva\b|economic value|cfroi|roic|return on|valenh|value enhancement",
    "depreciation": r"depreciation|ppe|pp&e|amortization|capex",
}

# sources that ship real Excel files without a login (drive the recommendation order)
SOURCE_RANK = {"asimplemodel": 0, "macabacus": 1, "biws": 2, "damodaran": 3, "exinfm": 4}


def tags_for(text: str) -> List[str]:
    t = text.lower()
    return [tag for tag, rx in TAG_RULES.items() if re.search(rx, t)]


def load_curated(catalog_dir: Path = CATALOG_DIR) -> Dict[str, Any]:
    """``catalog/curated_alternatives.json``: hand-verified sources and the finmodel function that reproduces each
    CFI title the coarse tag rules cannot match (accounting one-pagers, calculators, Excel-function demos,
    documents). Each source records its match quality (same/close/partial) and how its URL was verified."""
    f = catalog_dir / "curated_alternatives.json"
    return {i["title"]: i for i in json.loads(f.read_text())["items"]} if f.exists() else {}


def build(catalog_dir: Path = CATALOG_DIR) -> Dict[str, Any]:
    cat = load(catalog_dir)
    public = [e for e in cat["entries"] if e["access"] == "public"]
    for e in public:
        e["tags"] = tags_for(f"{e['title']} {e.get('filename') or ''}")
    out: List[Dict[str, Any]] = []
    for e in cat["entries"]:
        if e["source"] != "cfi":
            continue
        tags = tags_for(e["title"])
        matches = []
        for p in public:
            shared = sorted(set(tags) & set(p["tags"]))
            if shared:
                matches.append({"source": p["source"], "title": p["title"], "url": p["url"], "shared_tags": shared,
                                "size": p.get("size")})
        matches.sort(key=lambda m: (-len(m["shared_tags"]), SOURCE_RANK.get(m["source"], 9), m["title"]))
        out.append({"cfi_title": e["title"], "access": e["access"], "tags": tags, "alternatives": matches[:8]})
    curated = load_curated(catalog_dir)
    for x in out:
        c = curated.get(x["cfi_title"], {})
        x["engine"] = c.get("engine")
        x["curated"] = c.get("sources", [])
        if c.get("note"):
            x["curated_note"] = c["note"]
    covered = lambda x: bool(x["alternatives"] or x["curated"])
    result = {"generated": cat["generated"], "items": out,
              "summary": {"cfi_titles": len(out), "with_alternatives": sum(1 for x in out if covered(x)),
                          "with_tag_matches": sum(1 for x in out if x["alternatives"]),
                          "with_curated_sources": sum(1 for x in out if x["curated"]),
                          "with_engine": sum(1 for x in out if x["engine"]),
                          "paid_with_alternatives": sum(1 for x in out if x["access"] == "cfi-paid" and covered(x)),
                          "paid_total": sum(1 for x in out if x["access"] == "cfi-paid")}}
    (catalog_dir / "alternatives.json").write_text(json.dumps(result, indent=1))
    (catalog_dir / "alternatives.md").write_text(to_markdown(result))
    return result


def to_markdown(res: Dict[str, Any], paid_only: bool = False) -> str:
    s = res["summary"]
    out = ["# Public alternatives for CFI template titles", "",
           f"{s['paid_with_alternatives']}/{s['paid_total']} paid-only CFI titles and {s['with_alternatives']}/{s['cfi_titles']} titles overall have at least one public match"
           f" ({s.get('with_tag_matches', s['with_alternatives'])} by model-type tag, {s.get('with_curated_sources', 0)} with hand-verified sources);"
           f" {s.get('with_engine', 0)} titles name the finmodel function that reproduces them.",
           "Tag matches are a shortlist; curated sources were checked one by one (match quality and URL check shown).", ""]
    for section, flag in (("Paid-only CFI titles (Unlock)", "cfi-paid"), ("Free-tier CFI titles (Download)", "cfi-login")):
        if paid_only and flag != "cfi-paid":
            continue
        out += [f"## {section}", ""]
        for it in res["items"]:
            if it["access"] != flag:
                continue
            alts, cur = it["alternatives"], it.get("curated", [])
            line = f"- **{it['cfi_title']}** `{' '.join(it['tags']) or '-'}`"
            if it.get("engine"):
                line += f" — engine: `finmodel.{it['engine']}`"
            if not alts and not cur:
                out.append(line + " — no public match" + (f" ({it['curated_note']})" if it.get("curated_note") else ""))
                continue
            out.append(line)
            for a in cur[:4]:
                out.append(f"  - {a['source']}: [{a['title']}]({a['url']}) — {a['match']} match, {a['format']}, {a['access']}; {a['match_note']}")
            for a in alts[:max(0, 4 - len(cur))]:
                out.append(f"  - {a['source']}: [{a['title']}]({a['url']}) ({', '.join(a['shared_tags'])})")
        out.append("")
    return "\n".join(out)
