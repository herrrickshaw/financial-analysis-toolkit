"""Tests for finmodel.sectors, including regression checks against the real committed EDGAR extracts that the
football-field docs (docs/FOOTBALL_FIELD_STLD.md, docs/FOOTBALL_FIELD_CVX.md) found were cycle-distorted by hand —
this module should flag the same years as trough/peak automatically."""
import json
from pathlib import Path

import pytest

from finmodel import sectors

ROOT = Path(__file__).resolve().parent.parent


def synthetic_history(margins, revenue=1000.0):
    """years 2018..2018+len-1, revenue flat, EBIT = margin * revenue, no D&A."""
    return {f"{2018+i}-12-31": {"revenue": revenue, "operating_income": revenue * m} for i, m in enumerate(margins)}


def test_normalize_metric_uses_trailing_window_and_method():
    h = {f"{2018+i}-12-31": {"operating_income": v} for i, v in enumerate([10, 20, 30, 40, 50])}
    r = sectors.normalize_metric(h, "operating_income", periods=3, method="median")
    assert r["periods_used"] == ["2020-12-31", "2021-12-31", "2022-12-31"] and r["value"] == 40
    assert sectors.normalize_metric(h, "operating_income", periods=3, method="mean")["value"] == pytest.approx(40)
    assert sectors.normalize_metric(h, "operating_income", periods=2, method="max")["value"] == 50
    with pytest.raises(ValueError):
        sectors.normalize_metric({}, "operating_income")


def test_cycle_diagnostics_flags_trough_and_peak_on_synthetic_cycle():
    # a steady 10% margin except one deep trough year
    h = synthetic_history([0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.03])
    d = sectors.cycle_diagnostics(h, periods=8, sector="steel")
    assert d["fiscal_year"] == "2025-12-31" and "trough" in d["flag"] and d["deviation_pct"] < -0.20
    # a steady margin except one spike-peak year
    h2 = synthetic_history([0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.30])
    d2 = sectors.cycle_diagnostics(h2, periods=8, sector="oil_gas")
    assert "peak" in d2["flag"] and d2["deviation_pct"] > 0.20
    # a genuinely unremarkable year
    h3 = synthetic_history([0.10, 0.11, 0.09, 0.10, 0.11, 0.09, 0.10, 0.105])
    assert sectors.cycle_diagnostics(h3, periods=8)["flag"] == "near normal"


def test_dcf_scenarios_from_history_matches_trailing_extremes():
    h = synthetic_history([0.05, 0.10, 0.15, 0.20, 0.08])
    s = sectors.dcf_scenarios_from_history(h, periods=5)
    assert s["current_margin"] == pytest.approx(0.08) and s["base_margin"] == pytest.approx(0.10)
    assert s["bear_margin"] == pytest.approx(0.05) and s["blue_sky_margin"] == pytest.approx(0.20)


def test_sector_beta_and_profile_fallback():
    assert sectors.sector_beta("steel") == sectors.SECTOR_PROFILES["steel"].unlevered_beta
    assert sectors.sector_beta("some_sector_nobody_has_analysed") == sectors.SECTOR_PROFILES["default"].unlevered_beta


def test_normalized_comps_metrics_only_normalizes_margin_lines():
    h = synthetic_history([0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.03])
    for y in h: h[y]["da"] = 50.0; h[y]["net_income"] = h[y]["operating_income"] * 0.7
    m = sectors.normalized_comps_metrics(h, sector="steel")
    latest = sorted(h)[-1]
    assert m["revenue"] == h[latest]["revenue"] and m["net_income"] == h[latest]["net_income"]   # not normalized
    assert m["ebit"] == pytest.approx(100.0) and m["ebit"] != h[latest]["operating_income"]        # normalized (median of steady 10% years)


def test_from_dict_bundles_everything():
    h = synthetic_history([0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.03])
    out = sectors.from_dict({"history": h, "sector": "steel", "periods": 8})
    assert set(out) == {"cycle_diagnostics", "dcf_scenarios", "normalized_metrics", "sector_profile"}
    assert out["sector_profile"]["name"] == "Steel / metals & mining"


# ---- regression: the real EDGAR data behind the two published football-field checks
def _real_history(ticker):
    return json.loads((ROOT / "data" / "edgar" / f"{ticker}.json").read_text())["years"]


def test_stld_fy2025_flags_as_trough_on_real_data():
    d = sectors.cycle_diagnostics(_real_history("STLD"), periods=8, sector="steel")
    assert d["fiscal_year"] == "2025-12-31" and "trough" in d["flag"]


def test_pxd_fy2022_flags_as_peak_on_real_data():
    d = sectors.cycle_diagnostics(_real_history("PXD"), periods=8, sector="oil_gas", as_of="2022-12-31")
    assert d["fiscal_year"] == "2022-12-31" and "peak" in d["flag"]


def test_cvx_own_cycle_is_wide_and_current_year_below_median():
    d = sectors.cycle_diagnostics(_real_history("CVX"), periods=8, sector="oil_gas")
    assert d["fiscal_year"] == "2025-12-31"
    assert d["median_margin_trailing_years"] > d["latest_margin"]   # 2025 sits below Chevron's own trailing median margin
