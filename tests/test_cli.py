import json
from pathlib import Path
from finmodel.cli import main

EX = Path(__file__).resolve().parent.parent / "examples"


def test_cli_roundtrips(tmp_path, capsys):
    main(["dcf", str(EX / "cfi_dcf.json"), "--json-out", str(tmp_path / "d.json"), "--sensitivity"])
    d = json.loads((tmp_path / "d.json").read_text())
    assert abs(d["equity_value_per_share"] - 33.6266) < 1e-3 and "sensitivity" in d
    main(["three-statement", str(EX / "cfi_three_statement.json"), "--table", "balance_sheet"])
    out = capsys.readouterr().out
    assert "balance sheet OK" in out and "Total Assets" in out
    main(["projection", str(EX / "projection_demo.json"), "--xlsx", str(tmp_path / "p.xlsx")])
    assert (tmp_path / "p.xlsx").exists()
    main(["ratios", str(EX / "ratios_demo.json")])
    assert "gross_margin" in capsys.readouterr().out
    main(["catalog", "list", "--source", "asimplemodel"])
    assert "asimplemodel" in capsys.readouterr().out


def test_cli_comps_scores_costing(tmp_path, capsys):
    from finmodel.cli import main
    root = Path(__file__).resolve().parent.parent
    main(["comps", str(root / "examples" / "comps_stld.json"), "--json-out", str(tmp_path / "c.json")])
    out = capsys.readouterr().out
    assert "Football field" in out and "EV / EBITDA LTM" in out and (tmp_path / "c.json").exists()
    main(["scores", str(root / "examples" / "scores_stld.json")]); assert "Altman Z" in capsys.readouterr().out
    main(["costing", str(root / "examples" / "costing_university.json")]); assert "HHI" in capsys.readouterr().out
    main(["charts", "comps", str(root / "examples" / "comps_stld.json"), "-o", str(tmp_path / "ch.html")])
    html = (tmp_path / "ch.html").read_text(); assert "Football field" in html and "<svg" in html
