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
    print(f"\nworkbooks written to {out}/")


def main(argv=None):
    p = argparse.ArgumentParser(prog="finmodel", description="Financial modelling toolkit distilled from CFI templates")
    p.add_argument("--version", action="version", version=__version__)
    sp = p.add_subparsers(dest="cmd", required=True)

    x = sp.add_parser("extract", help="extract an Excel template into JSON+Markdown spec"); x.add_argument("files", nargs="+"); x.add_argument("-o", "--out", default="extracted"); x.set_defaults(fn=cmd_extract)
    c = sp.add_parser("catalog", help="build / list / verify / fetch template sources / alternatives"); c.add_argument("action", choices=["build", "list", "verify", "fetch", "alternatives", "fetch-signed"])
    c.add_argument("--source", nargs="*", help="damodaran asimplemodel exinfm cfi"); c.add_argument("--auth", help='CFI header, e.g. "Cookie: ..." (or env FINMODEL_CFI_AUTH)')
    c.add_argument("--dest", default="downloads"); c.add_argument("--urls", help="fetch-signed: text file with one pre-signed URL per line"); c.add_argument("--overwrite", action="store_true"); c.add_argument("--limit", type=int); c.set_defaults(fn=cmd_catalog)
    t = sp.add_parser("three-statement", help="run the linked 3-statement model"); t.add_argument("inputs"); t.add_argument("--xlsx"); t.add_argument("--json-out"); t.add_argument("--table", help="income_statement|balance_sheet|cash_flow|schedules|all"); t.set_defaults(fn=cmd_three)
    d = sp.add_parser("dcf", help="run the unlevered DCF"); d.add_argument("inputs"); d.add_argument("--xlsx"); d.add_argument("--json-out"); d.add_argument("--sensitivity", action="store_true"); d.set_defaults(fn=cmd_dcf)
    j = sp.add_parser("projection", help="run the bottom-up projection"); j.add_argument("inputs"); j.add_argument("--xlsx"); j.add_argument("--json-out"); j.set_defaults(fn=cmd_projection)
    r = sp.add_parser("ratios", help="ratio analysis from {is:{}, bs:{}}"); r.add_argument("inputs"); r.add_argument("--json-out"); r.set_defaults(fn=cmd_ratios)
    m = sp.add_parser("demo", help="run all engines on the bundled examples and write workbooks"); m.add_argument("--out", default="out"); m.set_defaults(fn=cmd_demo)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
