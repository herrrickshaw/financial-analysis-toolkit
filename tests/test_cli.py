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
