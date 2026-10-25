"""Personal balance sheet and the lender's adjustment to a guarantor's stated net worth — CFI's Personal
Financial Statement and SME Lending - Owner's Net Worth Adjustment templates (the same information the U.S.
SBA collects on Form 413).

``owner_net_worth_adjustment`` reproduces the deductions in CFI's SME template: a lender only relies on assets it
could actually reach through the guarantee, so it deducts loans to related companies, the haircut on marketable
securities, the income tax that would fall due on retirement accounts, and — when the spouse has NOT co-signed —
the spouse's share of jointly held savings, retirement assets and home equity."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .fin import safe_div

LIQUID = ("cash", "checking", "savings", "money_market")


def personal_financial_statement(assets: Mapping[str, float], liabilities: Mapping[str, float],
                                 annual_income: Optional[float] = None, annual_debt_payments: Optional[float] = None,
                                 liquid_asset_keys: Optional[tuple] = None) -> Dict[str, Any]:
    """Totals, net worth, liquid assets (keys containing cash/checking/savings/money_market unless
    ``liquid_asset_keys`` is given), debt-to-assets and, with income and payments, debt-to-income."""
    ta, tl = sum(assets.values()), sum(liabilities.values())
    keys = liquid_asset_keys or tuple(k for k in assets if any(w in k.lower() for w in LIQUID))
    liquid = sum(assets[k] for k in keys)
    out: Dict[str, Any] = {"total_assets": ta, "total_liabilities": tl, "net_worth": ta - tl, "liquid_assets": liquid,
                           "liquid_asset_keys": list(keys), "debt_to_assets": safe_div(tl, ta)}
    if annual_income and annual_debt_payments is not None:
        out["debt_to_income"] = annual_debt_payments / annual_income
    return out


def owner_net_worth_adjustment(stated_net_worth: float, related_company_loans: float = 0.0,
                               marketable_securities_stated: float = 0.0, marketable_securities_realisable: Optional[float] = None,
                               joint_savings_and_securities: float = 0.0, retirement_accounts: float = 0.0,
                               retirement_tax_rate: float = 0.0, residence_value: float = 0.0, residence_mortgage: float = 0.0,
                               spouse_is_co_guarantor: bool = False, spouse_share: float = 0.5,
                               other_deductions: Optional[Mapping[str, float]] = None) -> Dict[str, Any]:
    """Adjusted net worth = stated net worth - each deduction (itemised). Spousal deductions apply only when the
    spouse is NOT a co-guarantor; ``spouse_share`` is 50% for jointly owned assets by default."""
    d: Dict[str, float] = {"related_company_loans": related_company_loans}
    if marketable_securities_realisable is not None:
        d["marketable_securities_haircut"] = marketable_securities_stated - marketable_securities_realisable
    retirement_tax = retirement_accounts * retirement_tax_rate
    d["income_tax_on_retirement_accounts"] = retirement_tax
    if not spouse_is_co_guarantor:
        d["spousal_interest_in_savings_securities"] = joint_savings_and_securities * spouse_share
        d["spousal_interest_in_retirement_after_tax"] = (retirement_accounts - retirement_tax) * spouse_share
        d["spousal_equity_in_residence"] = (residence_value - residence_mortgage) * spouse_share
    for k, v in (other_deductions or {}).items():
        d[k] = v
    total = sum(d.values())
    adjusted = stated_net_worth - total
    return {"stated_net_worth": stated_net_worth, "deductions": d, "total_deductions": total,
            "adjusted_net_worth": adjusted, "haircut_pct": safe_div(total, stated_net_worth)}


_FUNCS = {f.__name__: f for f in (personal_financial_statement, owner_net_worth_adjustment)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    unknown = [k for k in d if not str(k).startswith("_") and k not in _FUNCS]
    if unknown:
        raise KeyError(f"unknown function(s): {unknown}; available: {sorted(_FUNCS)}")
    return {k: _FUNCS[k](**v) for k, v in d.items() if not str(k).startswith("_")}
