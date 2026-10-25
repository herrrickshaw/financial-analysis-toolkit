"""finmodel.calculators: the Excel-function mirrors are checked against Microsoft's own documented examples
(EFFECT, FV, CUMIPMT, CUMPRINC support pages); the rest against hand calculations."""
import math

import pytest

from finmodel import calculators as K


def test_effective_annual_rate_matches_excel_effect_doc_example():
    assert K.effective_annual_rate(0.0525, 4)["effective_annual_rate"] == pytest.approx(0.053542667, abs=1e-9)
    assert K.effective_annual_rate(0.05)["effective_annual_rate"] == pytest.approx(math.exp(0.05) - 1)


def test_future_value_matches_excel_fv_doc_example():
    # =FV(0.06/12, 10, -200, -500, 1) -> 2,581.40 in Excel
    out = K.future_value(500, 0.06 / 12, 10, payment=200, payment_at_start=True)
    assert out["future_value"] == pytest.approx(2581.403374, abs=1e-6)


def test_cumipmt_and_cumprinc_match_excel_doc_examples():
    # =CUMIPMT(0.09/12, 360, 125000, 13, 24, 0) -> -11,135.23 ; first month -> -937.50
    yr2 = K.cumulative_interest_and_principal(0.09 / 12, 360, 125000, 13, 24)
    assert yr2["cumulative_interest"] == pytest.approx(11135.23213, abs=1e-5)
    # =CUMPRINC(0.09/12, 360, 125000, 13, 24, 0) -> -934.11
    assert yr2["cumulative_principal"] == pytest.approx(934.1071234, abs=1e-6)
    m1 = K.cumulative_interest_and_principal(0.09 / 12, 360, 125000, 1, 1)
    assert m1["cumulative_interest"] == pytest.approx(937.5)
    assert m1["cumulative_principal"] == pytest.approx(68.27827118, abs=1e-7)


def test_full_term_principal_repays_the_loan():
    out = K.cumulative_interest_and_principal(0.05 / 12, 60, 20000, 1, 60)
    assert out["cumulative_principal"] == pytest.approx(20000)
    assert out["balance_after_end_period"] == pytest.approx(0, abs=1e-6)


def test_interest_simple_compound_continuous():
    assert K.interest(1000, 0.05, 2, simple=True)["interest"] == pytest.approx(100)
    assert K.interest(1000, 0.05, 2, periods_per_year=1)["interest"] == pytest.approx(102.5)
    assert K.interest(1000, 0.05, 2, periods_per_year=None)["ending_balance"] == pytest.approx(1000 * math.exp(0.1))


def test_perpetuity_and_its_guard():
    assert K.perpetuity(100, 0.10)["present_value"] == pytest.approx(1000)
    assert K.perpetuity(100, 0.10, 0.04)["present_value"] == pytest.approx(100 / 0.06)
    with pytest.raises(ValueError):
        K.perpetuity(100, 0.05, 0.05)


def test_pvgo():
    out = K.pvgo(share_price=50, next_year_eps=3, cost_of_equity=0.10)
    assert out["no_growth_value"] == pytest.approx(30)
    assert out["pvgo"] == pytest.approx(20)
    assert out["pvgo_share_of_price"] == pytest.approx(0.4)


def test_heloc_available_credit_and_payment_shock():
    out = K.heloc(500000, 0.85, 300000, draw_amount=100000, annual_rate=0.08, draw_years=10, repayment_years=20)
    assert out["available_credit"] == pytest.approx(125000)
    assert out["interest_only_monthly_payment"] == pytest.approx(666.6667, abs=1e-3)
    assert out["repayment_monthly_payment"] == pytest.approx(836.4401, abs=1e-3)   # standard 20-yr amortising payment
    with pytest.raises(ValueError):
        K.heloc(500000, 0.85, 300000, draw_amount=200000, annual_rate=0.08)


def test_growth_and_return_measures():
    assert K.cmgr(100, 200, 12)["cmgr"] == pytest.approx(2 ** (1 / 12) - 1)
    assert K.cmgr(100, 200, 12)["annualised"] == pytest.approx(1.0)
    g = K.geometric_mean_return([0.5, -0.5])
    assert g["arithmetic_mean"] == 0.0
    assert g["geometric_mean"] == pytest.approx(math.sqrt(0.75) - 1)   # you lost money despite a 0% arithmetic mean
    cg = K.capital_gains_yield(40, 44, dividends=1)
    assert (cg["capital_gains_yield"], cg["dividend_yield"], cg["total_return"]) == pytest.approx((0.10, 0.025, 0.125))


def test_bond_and_preferred_yields():
    assert K.coupon_rate(50, 1000, price=950) == pytest.approx({"coupon_rate": 0.05, "current_yield": 50 / 950})
    assert K.cost_of_preferred_stock(5, 50, flotation_cost_pct=0.02)["cost_of_preferred"] == pytest.approx(5 / 49)


def test_period_comparisons():
    assert K.percentage_change(-50, -25)["percentage_change"] == pytest.approx(0.5)   # loss halved = +50%
    yoy = K.year_over_year([100, 110, 99], labels=[2023, 2024, 2025])
    assert [r["yoy"] for r in yoy] == pytest.approx([0.10, -0.10])
    ytd = K.year_to_date([10, 20, 30, 40], monthly_prior=[10, 10, 10, 10], through_month=3)
    assert (ytd["ytd"], ytd["prior_ytd"], ytd["ytd_growth"]) == pytest.approx((60, 30, 1.0))
    assert K.ltm(last_fiscal_year=1000, current_ytd=300, prior_ytd=250)["ltm"] == 1050
    assert K.revenue_run_rate(25, 12)["run_rate"] == 300


def test_markup_vs_margin_and_tax_decalculation():
    m = K.markup(cost=100, price=150)
    assert (m["markup"], m["margin"]) == pytest.approx((0.5, 1 / 3))
    assert K.price_from_margin(100, 0.5)["price"] == pytest.approx(200)
    assert K.price_from_markup(100, 0.5)["price"] == pytest.approx(150)
    t = K.sales_tax_decalculator(108, 0.08)
    assert (t["pre_tax_amount"], t["tax"]) == pytest.approx((100, 8))


def test_annual_income():
    assert K.annual_income(25, "hourly")["annual_income"] == pytest.approx(25 * 8 * 5 * 52)
    assert K.annual_income(5000, "monthly")["annual_income"] == 60000
    with pytest.raises(ValueError):
        K.annual_income(1, "fortnightly-ish")


def test_from_dict_runs_named_calculators_and_rejects_unknown_ones():
    out = K.from_dict({"_comment": "x", "pvgo": {"share_price": 50, "next_year_eps": 3, "cost_of_equity": 0.1},
                       "markup": {"cost": 100, "price": 150}})
    assert set(out) == {"pvgo", "markup"}
    with pytest.raises(KeyError):
        K.from_dict({"not_a_calculator": {}})
