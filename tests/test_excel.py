"""Write formula workbooks and prove (via LibreOffice recalculation) that they reproduce the engines."""
import pytest
from finmodel import three_statement as ts, dcf, projection
from finmodel import trl_valuation as trl
from finmodel import excel


def _trl_inputs_dict():
    return {
        "commercial_value": 500_000_000, "discount_rate": 0.12,
        "stages": [
            {"trl": 5, "probability_of_advancing": 0.6, "years_to_next_stage": 1.0, "capital_required": 2_000_000, "required_irr": 0.60},
            {"trl": 6, "probability_of_advancing": 0.7, "years_to_next_stage": 1.0, "capital_required": 3_000_000, "required_irr": 0.50},
            {"trl": 7, "probability_of_advancing": 0.8, "years_to_next_stage": 1.0, "capital_required": 5_000_000, "required_irr": 0.40},
            {"trl": 8, "probability_of_advancing": 0.9, "years_to_next_stage": 1.0, "capital_required": 8_000_000, "required_irr": 0.30},
            {"trl": 9},
        ],
    }


def test_write_three_statement_and_dcf_have_formulas(tmp_path, three_statement_inputs, dcf_inputs):
    d = three_statement_inputs
    hist = [ts.HistoricalYear(**h) for h in d["historical"]]
    p = excel.write_three_statement(tmp_path / "ts.xlsx", hist, ts.ForecastAssumptions(**d["forecast"]), d["ppe_opening0"], d["debt_opening0"])
    from openpyxl import load_workbook
    ws = load_workbook(p)["Three Statement Model"]
    assert ws["I26"].value == "=H26*(1+I8)" and ws["M60"].value == "=M58-M48"
    q = excel.write_dcf(tmp_path / "dcf.xlsx", dcf.DCFInputs(**{k: v for k, v in dcf_inputs.items() if not k.startswith("_")}))
    wd = load_workbook(q)["DCF Model"]
    assert wd["D33"].value.startswith("=XNPV(") and wd["D43"].value.startswith("=XIRR(")


@pytest.mark.skipif(excel.soffice_path() is None, reason="LibreOffice not installed")
def test_libreoffice_recalc_matches_engine(tmp_path, three_statement_inputs, dcf_inputs):
    d = three_statement_inputs
    hist = [ts.HistoricalYear(**h) for h in d["historical"]]
    fc = ts.ForecastAssumptions(**d["forecast"])
    res = ts.run(hist, fc, d["ppe_opening0"], d["debt_opening0"])
    p = excel.write_three_statement(tmp_path / "ts.xlsx", hist, fc, d["ppe_opening0"], d["debt_opening0"], res)
    rp = excel.recalc_with_libreoffice(p)
    assert rp is not None
    v = excel.read_values(rp, "Three Statement Model")
    cols = "DEFGHIJKLM"
    for i, c in enumerate(cols):
        assert v[f"{c}38"] == pytest.approx(res.rows["Net Earnings"][i], abs=0.01)
        assert v[f"{c}48"] == pytest.approx(res.rows["Total Assets"][i], abs=0.01)
        assert v[f"{c}82"] == pytest.approx(res.rows["Closing Cash Balance"][i], abs=0.01)
        assert abs(v.get(f"{c}60", 0) or 0) < 0.01
        assert v[f"{c}3"] == "OK"
    inp = dcf.DCFInputs(**{k: v_ for k, v_ in dcf_inputs.items() if not k.startswith("_")})
    r = dcf.run(inp)
    q = excel.write_dcf(tmp_path / "dcf.xlsx", inp)
    rq = excel.recalc_with_libreoffice(q)
    w = excel.read_values(rq, "DCF Model")
    assert w["D33"] == pytest.approx(r["enterprise_value"], rel=1e-6)
    assert w["D38"] == pytest.approx(r["equity_value_per_share"], rel=1e-6)
    assert w["D43"] == pytest.approx(r["irr"], abs=1e-5)
    assert w["E21"] == pytest.approx(0.5)


def test_write_projection(tmp_path, projection_inputs):
    r = projection.from_dict(projection_inputs)
    p = excel.write_projection(tmp_path / "proj.xlsx", r)
    from openpyxl import load_workbook
    wb = load_workbook(p)
    assert {"Income Statement", "Balance Sheet", "Cash Flow", "Sales", "Payroll", "Opex", "Schedules", "Ratios"} <= set(wb.sheetnames)


def test_write_record_tables_writes_headers_rows_and_readme(tmp_path):
    sheets = {
        "States": {"headers": ["State", "Rate"], "rows": [["Gujarat", 0.75], ["Odisha", 1.0]]},
        "Central": {"headers": ["Scheme", "Outlay"], "rows": [["PLI Auto", 25938]]},
    }
    p = excel.write_record_tables(tmp_path / "catalog.xlsx", sheets, readme_lines=["Generated for testing", "Line 2"])
    from openpyxl import load_workbook
    wb = load_workbook(p)
    assert wb.sheetnames == ["README", "States", "Central"]
    assert wb["README"]["A1"].value == "Generated for testing"
    assert wb["README"]["A2"].value == "Line 2"
    ws = wb["States"]
    assert [ws.cell(row=1, column=c).value for c in (1, 2)] == ["State", "Rate"]
    assert [ws.cell(row=2, column=c).value for c in (1, 2)] == ["Gujarat", 0.75]
    assert [ws.cell(row=3, column=c).value for c in (1, 2)] == ["Odisha", 1.0]
    assert ws.freeze_panes == "A2"
    ws2 = wb["Central"]
    assert ws2.cell(row=2, column=1).value == "PLI Auto"
    assert ws2.cell(row=2, column=2).value == 25938


def test_write_record_tables_without_readme_uses_first_sheet_as_active(tmp_path):
    sheets = {"Only": {"headers": ["A"], "rows": [[1], [2]]}}
    p = excel.write_record_tables(tmp_path / "no_readme.xlsx", sheets)
    from openpyxl import load_workbook
    wb = load_workbook(p)
    assert wb.sheetnames == ["Only"]
    assert wb["Only"].cell(row=3, column=1).value == 2


def test_write_record_tables_sets_workbook_title_document_property(tmp_path):
    sheets = {"Only": {"headers": ["A"], "rows": [[1]]}}
    p = excel.write_record_tables(tmp_path / "titled.xlsx", sheets, workbook_title="Investment Promotion Agency (IPA) Support")
    from openpyxl import load_workbook
    wb = load_workbook(p)
    assert wb.properties.title == "Investment Promotion Agency (IPA) Support"


def test_write_trl_valuation_has_live_formulas_wired_bottom_up(tmp_path):
    inputs = trl.inputs_from_dict(_trl_inputs_dict())
    p = excel.write_trl_valuation(tmp_path / "trl_formulas.xlsx", inputs, uplift_from_trl=5, uplift_to_trl=7)
    from openpyxl import load_workbook
    ws = load_workbook(p)["TRL Valuation"]
    # TRL 9 (row 12, the last/terminal stage row) is the base case: no risk, no discounting
    assert ws["G12"].value == 1 and ws["H12"].value == 0
    # every row above chains off the row below (its next TRL) -- TRL 5 (row 8) references TRL 6 (row 9)
    assert ws["G8"].value == "=C8*G9" and ws["H8"].value == "=D8+H9"
    assert ws["I8"].value == "=$C$4/(1+$C$5)^H8" and ws["J8"].value == "=I8*G8"
    # the uplift block references the TRL 5 and TRL 7 rows' Risk-Adjusted Value cells (J8, J10) directly
    assert ws["C15"].value == "=J8" and ws["C16"].value == "=J10"
    assert ws["C19"].value == "=SUM(E8:E9)"  # capital required TRL5->TRL6 only, not through TRL8
    # the VC-Method cross-check block reads TRL 5's own Required IRR input cell (F8)
    assert ws["C26"].value == "=F8"


@pytest.mark.skipif(excel.soffice_path() is None, reason="LibreOffice not installed")
def test_write_trl_valuation_libreoffice_recalc_matches_engine(tmp_path):
    d = _trl_inputs_dict()
    inputs = trl.inputs_from_dict(d)
    p = excel.write_trl_valuation(tmp_path / "trl.xlsx", inputs, uplift_from_trl=5, uplift_to_trl=7)
    rp = excel.recalc_with_libreoffice(p)
    if rp is None:
        pytest.skip("LibreOffice headless conversion did not produce an output file in this environment")
    v = excel.read_values(rp, "TRL Valuation")
    uplift = trl.trl_uplift(inputs, 5, 7)
    assert v["J8"] == pytest.approx(uplift["from"]["risk_adjusted_value"], rel=1e-6)
    assert v["J10"] == pytest.approx(uplift["to"]["risk_adjusted_value"], rel=1e-6)
    assert v["C17"] == pytest.approx(uplift["value_uplift"], rel=1e-6)
    assert v["C18"] == pytest.approx(uplift["value_uplift_multiple"], rel=1e-6)
    vc = trl.vc_method_cross_check(inputs, 5)
    assert v["C32"] == pytest.approx(vc["implied_pre_money_valuation"], rel=1e-6)
