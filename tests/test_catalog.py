from finmodel import catalog


def test_build_catalog(tmp_path):
    cat = catalog.build()
    assert cat["counts"]["cfi:cfi-login"] == 196
    assert cat["counts"]["cfi:cfi-paid"] == 127
    assert cat["counts"]["damodaran:public"] >= 55
    assert cat["counts"]["asimplemodel:public"] == 8
    srcs = {e["source"] for e in cat["entries"]}
    assert srcs == {"cfi", "damodaran", "asimplemodel", "exinfm"}
    assert all(e["url"] for e in cat["entries"] if e["access"] != "cfi-paid")
    md = catalog.to_markdown(cat)
    assert "fcffginzu" in md and "Damodaran" in md


def test_fetch_skips_paid_and_login_without_auth(tmp_path):
    cat = catalog.build()
    man = catalog.fetch(cat, tmp_path, sources=["cfi"])  # no auth -> nothing attempted
    assert man == []
