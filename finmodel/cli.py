"""finmodel command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__


def _load_json(p: str):
    return json.loads(Path(p).read_text())


def _dump(obj, out: str | None):
    s = json.dumps(obj, indent=1, default=str)
    if out:
        Path(out).write_text(s)
        print(f"wrote {out}")
    else:
        print(s)


def cmd_extract(a):
    from .extract import extract_workbook
    for f in a.files:
        spec = extract_workbook(f, a.out)
        print(f"{Path(f).name}: {len(spec['sheets'])} sheets, {spec.get('totals')}")
        for s in spec["sheets"]:
            print(f"  - {s['name']:40} cells={s['stats']['cells']:5} formulas={s['stats']['formulas']:5} inputs={s['stats']['inputs']:4}  links={[x['sheet'] for x in s['cross_sheet_refs']]}")
    if a.out:
        print(f"specs written to {a.out}/")


def cmd_catalog(a):
    from . import catalog as C
    cat = C.build() if a.action in ("build", "verify", "fetch") else C.load()
    if a.action == "verify":
        cat = C.verify(cat, a.source, a.auth)
        (C.CATALOG_DIR / "catalog.json").write_text(json.dumps(cat, indent=1))
        (C.CATALOG_DIR / "catalog.md").write_text(C.to_markdown(cat))
    if a.action == "paid":
        from . import paid_templates
        r = paid_templates.build()
        print(f"paid titles: {r['summary']} -> catalog/paid_templates.json, docs/PAID_TEMPLATES.md")
        if a.title:
            for i in r["items"]:
                if a.title.lower() in i["title"].lower():
                    print(f"\n{i['title']}  [{i['category']}]  coverage={i['coverage']}\n  CFI: {i['cfi_description'] or '(no public page found)'}\n  Does: {i['what_it_does']}\n  Analogues: " + "; ".join(f"{x['source']}: {x['title']}" for x in i["analogues"]) + f"\n  Literature: {i['literature']}\n  Toolkit: {i['toolkit']}")
        return
    if a.action == "fetch-signed":
        rows = C.fetch_signed(Path(a.urls), Path(a.dest), (a.source or ["cfi"])[0])
        print(f"fetched {sum(1 for r in rows if r['ok'])}/{len(rows)} signed URLs -> {a.dest}/")
        return
    if a.action == "alternatives":
        from . import alternatives
        r = alternatives.build()
        print(f"alternatives: {r['summary']} -> catalog/alternatives.md")
        return
    if a.action == "fetch":
        man = C.fetch(cat, Path(a.dest), a.source, a.auth, a.overwrite, limit=a.limit)
        ok = sum(1 for m in man if m.get("ok"))
        print(f"fetched {ok}/{len(man)} -> {a.dest}/ (manifest.json)")
        for m in man:
            if not m.get("ok"):
                print(f"  FAILED {m['id']}: {m.get('error')}")
        return
    print(f"catalog: {len(cat['entries'])} entries  counts={cat['counts']}")
    if a.action == "list":
        for e in cat["entries"]:
            if a.source and e["source"] not in a.source:
                continue
            print(f"{e['source']:13} {e['access']:10} {e['title'][:60]:60} {e['url'] or ''}")


def cmd_three(a):
    from . import three_statement as ts
    d = _load_json(a.inputs)
    res = ts.from_dict(d)
    if a.xlsx:
        from .excel import write_three_statement
        hist = [ts.HistoricalYear(**h) for h in d["historical"]]
        write_three_statement(a.xlsx, hist, ts.ForecastAssumptions(**d["forecast"]), d.get("ppe_opening0"), d.get("debt_opening0"), res)
        print(f"wrote {a.xlsx}")
    if a.json_out or not a.xlsx:
        if a.table:
            print(res.table(a.table if a.table != "all" else None))
        else:
            _dump(res.to_dict(), a.json_out)
    print(f"balance sheet {'OK' if res.balanced else 'ERROR'}")


def cmd_dcf(a):
    from . import dcf
    d = _load_json(a.inputs)
    inp = dcf.DCFInputs(**dcf.clean(d))
    res = dcf.run(inp)
    if a.sensitivity:
        rs = [inp.discount_rate + x for x in (-0.02, -0.01, 0, 0.01, 0.02)]
        gs = [inp.perpetual_growth + x for x in (-0.01, -0.005, 0, 0.005, 0.01)]
        res["sensitivity"] = dcf.sensitivity(inp, rs, gs)
    if a.xlsx:
        from .excel import write_dcf
        write_dcf(a.xlsx, inp)
        print(f"wrote {a.xlsx}")
    _dump(res, a.json_out) if (a.json_out or not a.xlsx) else None
    print(f"EV={res['enterprise_value']:,.0f}  equity/share={res['equity_value_per_share']:,.2f}  upside={res['target_price_upside']:.1%}  IRR={res['irr']:.1%}")


def cmd_projection(a):
    from . import projection
    res = projection.from_dict(_load_json(a.inputs))
    if a.xlsx:
        from .excel import write_projection
        write_projection(a.xlsx, res)
        print(f"wrote {a.xlsx}")
    if a.json_out or not a.xlsx:
        _dump(res, a.json_out)
    ni = res["income_statement"]["Net Earnings"]
    print(f"years={res['years']}  revenue={[round(x) for x in res['income_statement']['Revenue']]}  net={[round(x) for x in ni]}  balanced={res['balanced']}")


def cmd_ratios(a):
    from . import ratios
    d = _load_json(a.inputs)
    _dump(ratios.compute(d["is"], d["bs"], d.get("days", 365)), a.json_out)


def cmd_lbo(a):
    from . import lbo
    res = lbo.from_dict(_load_json(a.inputs))
    if a.xlsx:
        from .excel import write_generic
        write_generic(a.xlsx, {"Income Statement": (res["years"], res["income_statement"]), "Balance Sheet": (res["years"], res["balance_sheet"]),
                               "Cash Flow": (res["years"], res["cash_flow"]), **{f"Debt - {k}": (res["years"], v) for k, v in res["debt_schedule"].items()}})
        print(f"wrote {a.xlsx}")
    if a.json_out or not a.xlsx:
        _dump(res, a.json_out)
    R = res["returns"]
    print(f"sponsor IRR={R['sponsor']['irr']:.1%} MOIC={R['sponsor']['moic']:.2f}x  exit equity={R['exit_equity_value']:,.0f}  balanced={res['balanced']}")


def cmd_merger(a):
    from . import merger
    res = merger.from_dict(_load_json(a.inputs))
    if a.xlsx and "pro_forma" in res:
        from .excel import write_generic
        pf = res["pro_forma"]
        write_generic(a.xlsx, {"Pro Forma IS": (pf["years"], pf["income_statement"]), "Debt": (pf["years"], pf["debt_schedule"])})
        print(f"wrote {a.xlsx}")
    if a.json_out or not a.xlsx:
        _dump(res, a.json_out)
    if "deal" in res:
        d = res["deal"]; print(f"deal: EPS {d['acquirer']['eps']:.3f} -> {d['combined']['eps']:.3f}  accretion {d['accretion_dilution_pct']:+.1%}  new shares {d['new_shares_issued']:,.2f}")
    if "pro_forma" in res:
        IS = res["pro_forma"]["income_statement"]; print("pro forma accretion %:", [f"{x:+.1%}" for x in IS["Accretion / (Dilution) %"]])


def cmd_transpile(a):
    from .xlcalc import XlModel, to_python_source
    for f in a.files:
        m = XlModel(f)
        r = m.verify()
        print(f"{r['file']}: {r['checked']} formulas, {r['ok']} match cached values ({r['match_rate']:.2%}), {r['compile_errors']} compile errors, {r['circular']} circular")
        for ex in r["examples"][: a.show]:
            print("   ", ex[0], "|", str(ex[1])[:70], "| got", repr(ex[2])[:40], "| cached", repr(ex[3])[:30])
        if a.out:
            out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
            p = out / (Path(f).stem.replace(" ", "_").replace("-", "_") + "_model.py")
            p.write_text(to_python_source(m)); print("    ->", p)


def cmd_charts(a):
    from . import charts
    d = _load_json(a.inputs)
    if a.engine == "three_statement":
        from . import three_statement as ts; res = ts.from_dict(d).to_dict()
    elif a.engine == "dcf":
        from . import dcf; inp = dcf.DCFInputs(**dcf.clean(d)); res = dcf.run(inp)
        res["sensitivity"] = dcf.sensitivity(inp, [inp.discount_rate + x for x in (-0.02, -0.01, 0, 0.01, 0.02)], [inp.perpetual_growth + x for x in (-0.01, -0.005, 0, 0.005, 0.01)])
    elif a.engine == "lbo":
        from . import lbo; res = lbo.from_dict(d)
    elif a.engine == "merger":
        from . import merger; res = merger.from_dict(d)
    else:
        from . import projection; res = projection.from_dict(d)
    p = charts.report_for(a.engine, res, a.out, title=a.title)
    print(f"wrote {p} ({len(charts.CATALOG[a.engine]['charts'])} chart templates)")


def cmd_glossary(a):
    g = _load_json(Path(__file__).resolve().parent.parent / "data" / "glossary.json")
    q = " ".join(a.query).lower()
    hits = [e for e in g["entries"] if q in e["term"].lower() or any(q in s.lower() for s in e["synonyms"])]
    if not hits and a.deep:
        hits = [e for e in g["entries"] if q in e["definition"].lower()]
    for e in hits[: a.limit]:
        print(f"\n{e['term']}  [{e['category']}]" + (f"  (also: {', '.join(e['synonyms'])})" if e["synonyms"] else ""))
        print("  " + e["definition"])
        for k, lab in (("formula", "Formula"), ("gaap_vs_ifrs", "GAAP vs IFRS"), ("how_to_evaluate", "Evaluate"), ("toolkit", "Toolkit")):
            if e.get(k): print(f"  {lab}: {e[k]}")
    if not hits:
        rows = [r for r in g["gaap_vs_ifrs"] if q in r["topic"].lower()]
        for r in rows: print(f"\n{r['topic']}\n  US GAAP: {r['us_gaap']}\n  IFRS: {r['ifrs']}\n  Evaluate: {r['how_to_evaluate']}")
        if not rows: print("no match; try --deep to search definitions")


def cmd_demo(a):
    ex = Path(__file__).resolve().parent.parent / "examples"
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    from . import three_statement as ts, dcf, projection
    from .excel import write_three_statement, write_dcf, write_projection
    d = _load_json(ex / "cfi_three_statement.json")
    r = ts.from_dict(d)
    write_three_statement(out / "three_statement.xlsx", [ts.HistoricalYear(**h) for h in d["historical"]], ts.ForecastAssumptions(**d["forecast"]), d.get("ppe_opening0"), d.get("debt_opening0"), r)
    print(r.table("income_statement")); print(); print(r.table("balance_sheet")); print(f"balanced={r.balanced}\n")
    dd = _load_json(ex / "cfi_dcf.json"); inp = dcf.DCFInputs(**dcf.clean(dd)); rr = dcf.run(inp); write_dcf(out / "dcf.xlsx", inp)
    print(f"DCF: EV={rr['enterprise_value']:,.0f} equity/share={rr['equity_value_per_share']:.2f} upside={rr['target_price_upside']:.1%} IRR={rr['irr']:.1%}\n")
    pr = projection.from_dict(_load_json(ex / "projection_demo.json")); write_projection(out / "projection.xlsx", pr)
    print(f"Projection: years={pr['years']} revenue={[round(x) for x in pr['income_statement']['Revenue']]} balanced={pr['balanced']}")
    from . import charts
    charts.report_for("three_statement", r.to_dict(), out / "charts_three_statement.html")
    rr["sensitivity"] = dcf.sensitivity(inp, [inp.discount_rate + x for x in (-0.02, -0.01, 0, 0.01, 0.02)], [inp.perpetual_growth + x for x in (-0.01, -0.005, 0, 0.005, 0.01)])
    charts.report_for("dcf", rr, out / "charts_dcf.html"); charts.report_for("projection", pr, out / "charts_projection.html")
    from . import lbo, merger
    charts.report_for("lbo", lbo.from_dict(_load_json(ex / "lbo_asm.json")), out / "charts_lbo.html")
    charts.report_for("merger", merger.from_dict(_load_json(ex / "merger_biws.json")), out / "charts_merger.html")
    print(f"\nworkbooks and chart reports written to {out}/")


def main(argv=None):
    p = argparse.ArgumentParser(prog="finmodel", description="Financial modelling toolkit distilled from CFI templates")
    p.add_argument("--version", action="version", version=__version__)
    sp = p.add_subparsers(dest="cmd", required=True)

    x = sp.add_parser("extract", help="extract an Excel template into JSON+Markdown spec"); x.add_argument("files", nargs="+"); x.add_argument("-o", "--out", default="extracted"); x.set_defaults(fn=cmd_extract)
    c = sp.add_parser("catalog", help="build / list / verify / fetch template sources / alternatives"); c.add_argument("action", choices=["build", "list", "verify", "fetch", "alternatives", "fetch-signed", "paid"]); c.add_argument("--title", help="paid: filter titles containing this text")
    c.add_argument("--source", nargs="*", help="damodaran asimplemodel exinfm cfi"); c.add_argument("--auth", help='CFI header, e.g. "Cookie: ..." (or env FINMODEL_CFI_AUTH)')
    c.add_argument("--dest", default="downloads"); c.add_argument("--urls", help="fetch-signed: text file with one pre-signed URL per line"); c.add_argument("--overwrite", action="store_true"); c.add_argument("--limit", type=int); c.set_defaults(fn=cmd_catalog)
    t = sp.add_parser("three-statement", help="run the linked 3-statement model"); t.add_argument("inputs"); t.add_argument("--xlsx"); t.add_argument("--json-out"); t.add_argument("--table", help="income_statement|balance_sheet|cash_flow|schedules|all"); t.set_defaults(fn=cmd_three)
    d = sp.add_parser("dcf", help="run the unlevered DCF"); d.add_argument("inputs"); d.add_argument("--xlsx"); d.add_argument("--json-out"); d.add_argument("--sensitivity", action="store_true"); d.set_defaults(fn=cmd_dcf)
    j = sp.add_parser("projection", help="run the bottom-up projection"); j.add_argument("inputs"); j.add_argument("--xlsx"); j.add_argument("--json-out"); j.set_defaults(fn=cmd_projection)
    r = sp.add_parser("ratios", help="ratio analysis from {is:{}, bs:{}}"); r.add_argument("inputs"); r.add_argument("--json-out"); r.set_defaults(fn=cmd_ratios)
    l = sp.add_parser("lbo", help="run the LBO model"); l.add_argument("inputs"); l.add_argument("--xlsx"); l.add_argument("--json-out"); l.set_defaults(fn=cmd_lbo)
    g = sp.add_parser("merger", help="run the merger (accretion/dilution) model"); g.add_argument("inputs"); g.add_argument("--xlsx"); g.add_argument("--json-out"); g.set_defaults(fn=cmd_merger)
    tp = sp.add_parser("transpile", help="convert a workbook's formulas to Python and verify against cached values"); tp.add_argument("files", nargs="+"); tp.add_argument("-o", "--out"); tp.add_argument("--show", type=int, default=5); tp.set_defaults(fn=cmd_transpile)
    ch = sp.add_parser("charts", help="render the chart template for an engine's inputs to a self-contained HTML report"); ch.add_argument("engine", choices=["three_statement", "dcf", "lbo", "merger", "projection"]); ch.add_argument("inputs"); ch.add_argument("-o", "--out", default="out/charts.html"); ch.add_argument("--title"); ch.set_defaults(fn=cmd_charts)
    gl = sp.add_parser("glossary", help="look up a financial term (definition, formula, GAAP vs IFRS note)"); gl.add_argument("query", nargs="+"); gl.add_argument("--deep", action="store_true"); gl.add_argument("--limit", type=int, default=5); gl.set_defaults(fn=cmd_glossary)
    m = sp.add_parser("demo", help="run all engines on the bundled examples and write workbooks"); m.add_argument("--out", default="out"); m.set_defaults(fn=cmd_demo)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
