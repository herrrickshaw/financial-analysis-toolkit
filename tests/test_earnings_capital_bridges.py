"""finmodel.earnings_bridges and finmodel.capital_bridges, checked against hand calculations and against the
worked numbers in CFI's own free templates where the spec exposes them (Market Value of Debt estimate formula,
APIC example, Cash-Flow-Reconciliation income statement)."""
import pytest

from finmodel import capital_bridges as C
from finmodel import earnings_bridges as E


def test_top_down_and_bottom_up_subtotals_reconcile():
    # CFI Cash-Flow-Reconciliation income statement: GP - dep 500 - SG&A 300 - interest 50, tax 20% of EBT
    rev, cogs = 3000.0, 1200.0
    ebt = rev - cogs - 500 - 300 - 50
    tax = 0.2 * ebt
    out = E.income_statement_subtotals(rev, cogs, operating_expenses=300, depreciation_amortization=500,
                                       interest_expense=50, taxes=tax, net_income=ebt - tax)
    assert (out["ebitda"], out["ebit"], out["ebt"], out["net_income"]) == pytest.approx((1500, 1000, 950, 760))
    assert out["bottom_up"]["gap_vs_top_down"] == pytest.approx(0)
    assert out["effective_tax_rate"] == pytest.approx(0.2)


def test_adjusted_ebitda_itemises_addbacks():
    out = E.adjusted_ebitda(100, {"restructuring": 15, "stock_comp": 10, "gain_on_asset_sale": -5}, revenue=1000)
    assert out["adjusted_ebitda"] == 120
    assert out["addbacks_share_of_adjusted"] == pytest.approx(20 / 120)
    assert out["adjusted_ebitda_margin"] == pytest.approx(0.12)


def test_normalized_net_income_is_after_tax_and_honours_item_tax_rates():
    out = E.normalize_net_income(500, [{"item": "litigation charge", "pretax": 100},
                                       {"item": "gain on sale", "pretax": -40},
                                       {"item": "regulatory fine (non-deductible)", "pretax": 30, "tax_rate": 0.0}],
                                 tax_rate=0.25, diluted_shares=100)
    assert out["total_after_tax_adjustment"] == pytest.approx(75 - 30 + 30)
    assert out["normalized_net_income"] == pytest.approx(575)
    assert out["normalized_eps"] == pytest.approx(5.75)


def test_nopat_fcff_fcfe():
    assert E.nopat(200, 0.25)["nopat"] == 150
    f = E.free_cash_flow(ebit=200, tax_rate=0.25, depreciation_amortization=40, capex=60, change_in_nwc=10,
                         interest_expense=20, net_borrowing=5, cash_from_operations=170)
    assert f["fcff"] == pytest.approx(150 + 40 - 60 - 10)
    assert f["fcfe"] == pytest.approx(120 - 15 + 5)
    assert f["simple_fcf"] == 110


def test_cash_eps_and_ffo():
    c = E.cash_eps(cash_from_operations=300, diluted_shares=100, net_income=200)
    assert (c["cash_eps"], c["eps"], c["cash_conversion"]) == pytest.approx((3, 2, 1.5))
    f = E.ffo(net_income=100, real_estate_depreciation_amortization=60, gains_on_property_sales=20,
              impairments_of_depreciable_real_estate=5, shares=10, recurring_capex=15, straight_line_rent_adjustment=4)
    assert f["ffo"] == 145 and f["affo"] == 126
    assert f["ffo_per_share"] == pytest.approx(14.5)


def test_ev_bridge_both_directions():
    a = C.enterprise_value_bridge(equity_value=1000, debt=300, cash=100, preferred_stock=50, minority_interest=20)
    assert a["enterprise_value"] == 1270
    b = C.enterprise_value_bridge(enterprise_value=1270, debt=300, cash=100, preferred_stock=50, minority_interest=20)
    assert b["equity_value"] == pytest.approx(1000)
    with pytest.raises(ValueError):
        C.enterprise_value_bridge(debt=1)


def test_net_debt_and_market_cap():
    nd = C.net_debt(total_debt=100, cash_and_equivalents=150, marketable_securities=10)
    assert nd["net_debt"] == -60 and nd["net_cash_position"]
    assert C.market_cap(20, 50, diluted_shares=55) == {"market_cap": 1000, "diluted_market_cap": 1100}


def test_market_value_of_debt_estimate_matches_damodaran_formula_and_precise_method():
    wam = C.weighted_average_maturity([{"book_value": 400, "years_to_maturity": 2},
                                       {"book_value": 600, "years_to_maturity": 7}])
    assert wam == pytest.approx(5.0)
    est = C.market_value_of_debt_estimate(1000, 60, 0.08, wam)
    expected = 60 * (1 - 1.08 ** -5) / 0.08 + 1000 / 1.08 ** 5
    assert est["market_value_of_debt"] == pytest.approx(expected)
    assert est["market_value_of_debt"] < 1000          # coupon 6% < 8% yield -> trades below book
    # a bond whose coupon equals its yield is worth par
    par = C.market_value_of_debt_precise([{"name": "bond", "face_value": 1000, "annual_interest": 80,
                                          "years_to_maturity": 7, "yield": 0.08}])
    assert par["market_value_of_debt"] == pytest.approx(1000)


def test_tax_shield_finite_and_permanent():
    out = C.tax_shield([100, 100], tax_rate=0.25, cost_of_debt=0.05, permanent_debt=2000)
    assert out["annual_tax_shield"] == [25, 25]
    assert out["pv_tax_shield"] == pytest.approx(25 / 1.05 + 25 / 1.05 ** 2)
    assert out["pv_tax_shield_permanent_debt"] == 500


def test_book_vs_market_and_apic():
    b = C.book_vs_market_equity(book_equity=500, share_price=30, shares_outstanding=50)
    assert b["price_to_book"] == pytest.approx(3.0)
    a = C.additional_paid_in_capital(offering_price=25, par_value=0.01, shares_issued=1000)
    assert (a["total_proceeds"], a["common_stock_at_par"], a["additional_paid_in_capital"]) == pytest.approx((25000, 10, 24990))


def test_weighted_average_shares_time_weights_issues_and_restates_splits():
    # 1,000 at start; +600 issued start of month 7 (6/12 outstanding); -120 bought back start of month 10 (3/12)
    out = C.weighted_average_shares(1000, [{"month": 7, "shares": 600}, {"month": 10, "shares": -120}])
    assert out["weighted_average_shares"] == pytest.approx(1000 + 300 - 30)
    assert out["ending_shares"] == 1480
    # a 2-for-1 split in month 9 restates the beginning shares and the month-7 issue, but not a month-11 issue
    s = C.weighted_average_shares(1000, [{"month": 7, "shares": 600}, {"month": 9, "split_ratio": 2},
                                         {"month": 11, "shares": 240}])
    assert s["weighted_average_shares"] == pytest.approx(2000 + 1200 * 0.5 + 240 * 2 / 12)
