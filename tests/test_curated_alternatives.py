"""catalog/curated_alternatives.json stays consistent with the code and the catalog: every engine it names is a
real finmodel function, every title is a real CFI catalog title, and every source carries a match grade and a
record of how its URL was checked."""
import importlib
import json
from pathlib import Path

from finmodel import alternatives
from finmodel.catalog import CATALOG_DIR, load

CURATED = json.loads((CATALOG_DIR / "curated_alternatives.json").read_text())["items"]


def test_every_named_engine_function_exists():
    for item in CURATED:
        if not item["engine"]:
            continue
        mod, fn = item["engine"].split(".")
        assert hasattr(importlib.import_module(f"finmodel.{mod}"), fn), item["engine"]


def test_titles_are_real_cfi_titles_and_unique():
    titles = [i["title"] for i in CURATED]
    assert len(titles) == len(set(titles))
    cfi = {e["title"] for e in load()["entries"] if e["source"] == "cfi"}
    assert set(titles) <= cfi


def test_sources_are_graded_and_verified():
    for item in CURATED:
        assert item["sources"], item["title"]
        for s in item["sources"]:
            assert s["match"] in ("same", "close", "partial"), (item["title"], s)
            assert s["url"].startswith("https://") or s["url"].startswith("http://"), s["url"]
            assert s.get("verified"), (item["title"], s["url"])
        # best match first
        order = {"same": 0, "close": 1, "partial": 2}
        ranks = [order[s["match"]] for s in item["sources"]]
        assert ranks == sorted(ranks), item["title"]


def test_build_merges_curated_sources_and_engines(tmp_path):
    for f in ("catalog.json", "curated_alternatives.json"):
        (tmp_path / f).write_text((CATALOG_DIR / f).read_text())
    res = alternatives.build(tmp_path)
    s = res["summary"]
    assert s["with_curated_sources"] == len(CURATED)
    assert s["with_alternatives"] >= s["with_tag_matches"]
    eoq = next(i for i in res["items"] if i["cfi_title"] == "Economic Order Quantity")
    assert eoq["engine"] == "managerial_costing.economic_order_quantity" and eoq["curated"]
    assert "engine: `finmodel.managerial_costing.economic_order_quantity`" in (tmp_path / "alternatives.md").read_text()
