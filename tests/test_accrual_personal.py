"""finmodel.accrual_bridges and finmodel.personal_finance. The owner-net-worth test reproduces every
deduction in CFI's SME Lending template (its spec exposes the formulas: securities 1,500,000-468,000,
savings 475,000/2, retirement tax 260,000x45%, spousal retirement 260,000x55%/2, residence (1,150,000-708,000)/2)."""
import pytest

from finmodel import accrual_bridges as A
from finmodel import personal_finance as P


def test_cash_to_accrual_lines_and_statement():
    r = A.cash_to_accrual_revenue(cash_received=1000, receivables_begin=100, receivables_end=160,
                                  unearned_revenue_begin=50, unearned_revenue_end=30)
    assert r["accrual_revenue"] == 1000 + 60 + 20
    e = A.cash_to_accrual_expense(cash_paid=400, payables_begin=40, payables_end=70, prepaid_begin=10, prepaid_end=25)
    assert e["accrual_expense"] == 400 + 30 - 15
    s = A.cash_to_accrual_statement(
        revenue=dict(cash_received=1000, receivables_begin=100, receivables_end=160),
        expenses={"rent": dict(cash_paid=120, prepaid_begin=0, prepaid_end=10), "wages": dict(cash_paid=500, payables_begin=0, payables_end=20)})
    assert s["cash_basis_profit"] == 380
    assert s["accrual_basis_profit"] == 1060 - 110 - 520
    assert s["difference"] == pytest.approx(50)


def test_indirect_cfo_reconciles_to_balance_sheet_cash():
    out = A.cash_flow_reconciliation(
        net_income=760, non_cash_items={"depreciation": 500, "stock_based_compensation": 40},
        working_capital={"accounts_receivable": (300, 380, "asset"), "inventory": (200, 170, "asset"),
                         "accounts_payable": (150, 190, "liability")},
        investing={"capex": -600}, financing={"debt_repaid": -200, "dividends": -100},
        cash_begin=1000, cash_end=1410)
    assert out["working_capital_changes"] == {"accounts_receivable": -80, "inventory": 30, "accounts_payable": 40}
    assert out["cash_from_operations"] == 1290
    assert out["net_change_in_cash"] == 390
    assert out["reconciliation_gap"] == pytest.approx(-20)   # an unexplained 20 is surfaced, not hidden
    with pytest.raises(ValueError):
        A.cash_flow_reconciliation(0, {}, {"x": (0, 1, "equity")}, {}, {})


def test_working_capital_cycle_uses_average_balances():
    out = A.working_capital_cycle(revenue=3650, cogs=1825, receivables=[90, 110], inventory=100, payables=[40, 60])
    assert out["dso"] == pytest.approx(10)      # avg AR 100 / revenue 3,650 x 365
    assert out["dio"] == pytest.approx(20)      # inventory 100 / COGS 1,825 x 365
    assert out["dpo"] == pytest.approx(10)      # avg AP 50 / COGS 1,825 x 365
    assert out["cash_conversion_cycle"] == pytest.approx(20)
    assert out["operating_cycle"] == pytest.approx(30)


def test_from_dict_accepts_json_lists_for_working_capital():
    out = A.from_dict({"cash_flow_reconciliation": {"net_income": 10, "non_cash_items": {}, "working_capital": {"ar": [5, 7, "asset"]},
                                                    "investing": {}, "financing": {}}})
    assert out["cash_flow_reconciliation"]["cash_from_operations"] == 8


def test_personal_financial_statement():
    out = P.personal_financial_statement(
        assets={"checking_a": 5000, "savings_a": 15000, "taxable_investment_a": 40000, "401k": 120000, "property_a": 400000},
        liabilities={"credit_card_a": 3000, "student_loan": 20000, "mortgage": 250000},
        annual_income=120000, annual_debt_payments=30000)
    assert out["net_worth"] == 580000 - 273000
    assert out["liquid_assets"] == 20000
    assert out["debt_to_income"] == pytest.approx(0.25)


def test_owner_net_worth_adjustment_reproduces_cfi_sme_template_deductions():
    out = P.owner_net_worth_adjustment(
        stated_net_worth=5_000_000, related_company_loans=0,
        marketable_securities_stated=1_500_000, marketable_securities_realisable=468_000,
        joint_savings_and_securities=475_000, retirement_accounts=260_000, retirement_tax_rate=0.45,
        residence_value=1_150_000, residence_mortgage=708_000, spouse_is_co_guarantor=False)
    d = out["deductions"]
    assert d["marketable_securities_haircut"] == 1_500_000 - 468_000
    assert d["spousal_interest_in_savings_securities"] == pytest.approx(475_000 / 2)
    assert d["income_tax_on_retirement_accounts"] == pytest.approx(260_000 * 0.45)
    assert d["spousal_interest_in_retirement_after_tax"] == pytest.approx(260_000 * (1 - 0.45) / 2)
    assert d["spousal_equity_in_residence"] == pytest.approx((1_150_000 - 708_000) / 2)
    assert out["adjusted_net_worth"] == pytest.approx(5_000_000 - sum(d.values()))
    co = P.owner_net_worth_adjustment(5_000_000, joint_savings_and_securities=475_000, spouse_is_co_guarantor=True)
    assert "spousal_interest_in_savings_securities" not in co["deductions"]
