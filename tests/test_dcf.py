"""Reconcile to cached values of the CFI 'DCF Model Template (Updated)'."""
import math
import pytest
from finmodel import dcf


def test_reconciles_to_cfi_workbook(dcf_inputs):
    inp = dcf.DCFInputs(**dcf.clean(dcf_inputs))
    r = dcf.run(inp)
    assert r["year_fraction"][0] == pytest.approx(0.5)
    assert r["year_fraction"][1:] == pytest.approx([1, 1, 1, 1])
    assert r["ufcf"] == pytest.approx([35494.262, 37715.192065, 41501.0737282, 43510.4616657, 47008.0299436], rel=1e-9)
    tv = r["terminal_value"]
    assert tv["perpetuity_growth"] == pytest.approx(537980.7871321079)
    assert tv["ev_ebitda"] == pytest.approx(546277.7332654343)
    assert tv["used"] == pytest.approx(542129.260198771)
    assert r["enterprise_value"] == pytest.approx(462982.9754462675, rel=1e-9)
    assert r["equity_value"] == pytest.approx(672532.4958114524, rel=1e-9)
    assert r["equity_value_per_share"] == pytest.approx(33.62662479057262, rel=1e-9)
    assert r["market"]["enterprise_value"] == pytest.approx(290450.4796348151)
    assert r["target_price_upside"] == pytest.approx(0.3450649916229047, rel=1e-9)
    assert r["irr"] == pytest.approx(0.2634776532649994, abs=1e-7)
    assert r["dates"] == ["2017-12-31", "2018-06-30", "2019-06-30", "2020-06-30", "2021-06-30", "2022-06-30"]


def test_terminal_methods_and_sensitivity(dcf_inputs):
    base = {k: v for k, v in dcf_inputs.items() if not k.startswith("_")}
    p = dcf.run(dcf.DCFInputs(**{**base, "terminal_method": "perpetuity"}))
    m = dcf.run(dcf.DCFInputs(**{**base, "terminal_method": "multiple"}))
    a = dcf.run(dcf.DCFInputs(**base))
    assert min(p["enterprise_value"], m["enterprise_value"]) < a["enterprise_value"] < max(p["enterprise_value"], m["enterprise_value"])
    s = dcf.sensitivity(dcf.DCFInputs(**base), [0.10, 0.12, 0.14], [0.02, 0.03, 0.04])
    assert s["table"][1][1] == pytest.approx(a["equity_value_per_share"])
    assert s["table"][0][2] > s["table"][2][0]  # low WACC / high g is worth more
    with pytest.raises(ValueError):
        dcf.run(dcf.DCFInputs(**{**base, "discount_rate": 0.02}))


def test_capex_list_and_fye_feb29():
    inp = dcf.DCFInputs(ebit=[100, 100], da=[10, 10], change_nwc=[0, 0], capex=[5, 6], transaction_date="2023-12-31", fiscal_year_end="2024-02-29")
    r = dcf.run(inp)
    assert r["capex"] == [5, 6]
    assert r["dates"][1:] == ["2024-02-29", "2025-02-28"]
