"""Equity and debt value bridges — CFI's Market Capitalization, Net Debt, Enterprise Value vs Equity Value,
Market Value of Debt, Tax Shield, BV vs MV of Equity, Additional Paid-in Capital and Weighted Average Shares
Outstanding templates.

  Market value of debt   — Damodaran's estimate treats all book debt as ONE coupon bond: annual interest as
                           the coupon, book debt as face, weighted-average maturity as the term, discounted at
                           the pre-tax cost of debt. ``market_value_of_debt_precise`` discounts each instrument's
                           own cash flows instead (CFI's second sheet does exactly this with NPV).
  Tax shield             — annual shield = interest x t; for permanent debt its present value is t x D
                           (Modigliani-Miller with corporate taxes); for a finite schedule it is discounted at
                           the cost of debt.
  Weighted shares        — share issuances/buybacks are time-weighted by the fraction of the period they were
                           outstanding; stock splits are applied retroactively to the whole period (IAS 33 /
                           ASC 260)."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from .fin import safe_div


def market_cap(share_price: float, shares_outstanding: float, diluted_shares: Optional[float] = None) -> Dict[str, Any]:
    out = {"market_cap": share_price * shares_outstanding}
    if diluted_shares is not None:
        out["diluted_market_cap"] = share_price * diluted_shares
    return out


def net_debt(total_debt: float, cash_and_equivalents: float, marketable_securities: float = 0.0,
             lease_liabilities: float = 0.0) -> Dict[str, Any]:
    """Net debt = debt (+ lease liabilities if you treat them as debt) - cash - liquid marketable securities.
    Negative net debt = a net cash position."""
    gross = total_debt + lease_liabilities
    nd = gross - cash_and_equivalents - marketable_securities
    return {"gross_debt": gross, "net_debt": nd, "net_cash_position": nd < 0}


def enterprise_value_bridge(equity_value: Optional[float] = None, enterprise_value: Optional[float] = None,
                            debt: float = 0.0, cash: float = 0.0, preferred_stock: float = 0.0,
                            minority_interest: float = 0.0, non_operating_assets: float = 0.0) -> Dict[str, Any]:
    """EV = equity + debt + preferred + minority interest - cash - non-operating assets. Give exactly one of
    ``equity_value`` / ``enterprise_value`` and the bridge items; the other is solved."""
    if (equity_value is None) == (enterprise_value is None):
        raise ValueError("give exactly one of equity_value or enterprise_value")
    claims = debt + preferred_stock + minority_interest - cash - non_operating_assets
    if enterprise_value is None:
        enterprise_value = equity_value + claims
    else:
        equity_value = enterprise_value - claims
    return {"equity_value": equity_value, "enterprise_value": enterprise_value, "net_claims": claims,
            "bridge": {"debt": debt, "preferred_stock": preferred_stock, "minority_interest": minority_interest,
                       "cash": -cash, "non_operating_assets": -non_operating_assets}}


def weighted_average_maturity(instruments: Sequence[Mapping[str, float]]) -> float:
    """Book-value-weighted average maturity, each instrument ``{"book_value": .., "years_to_maturity": ..}``."""
    total = sum(i["book_value"] for i in instruments)
    return sum(i["book_value"] * i["years_to_maturity"] for i in instruments) / total


def market_value_of_debt_estimate(total_book_debt: float, annual_interest_expense: float, pretax_cost_of_debt: float,
                                  weighted_avg_maturity_years: float) -> Dict[str, Any]:
    """Damodaran's one-bond estimate: I x [1 - (1+kd)^-n] / kd + D / (1+kd)^n."""
    k, n = pretax_cost_of_debt, weighted_avg_maturity_years
    mv = annual_interest_expense * (1 - (1 + k) ** -n) / k + total_book_debt / (1 + k) ** n
    return {"market_value_of_debt": mv, "book_value_of_debt": total_book_debt, "market_to_book": mv / total_book_debt}


def market_value_of_debt_precise(instruments: Sequence[Mapping[str, float]]) -> Dict[str, Any]:
    """Value each instrument from its own annual cash flows: ``{"name", "face_value", "annual_interest",
    "years_to_maturity" (whole years), "yield"}``; face repaid at maturity."""
    rows = []
    for i in instruments:
        y, n = i["yield"], int(i["years_to_maturity"])
        v = sum(i["annual_interest"] / (1 + y) ** t for t in range(1, n + 1)) + i["face_value"] / (1 + y) ** n
        rows.append({"name": i.get("name", ""), "face_value": i["face_value"], "market_value": v})
    total = sum(r["market_value"] for r in rows)
    return {"instruments": rows, "market_value_of_debt": total,
            "book_value_of_debt": sum(r["face_value"] for r in rows)}


def tax_shield(interest_expense: Optional[Sequence[float]] = None, tax_rate: float = 0.0,
               cost_of_debt: Optional[float] = None, permanent_debt: Optional[float] = None) -> Dict[str, Any]:
    """Interest tax shield. ``interest_expense`` as a per-year list -> annual shields and (with ``cost_of_debt``)
    their present value; ``permanent_debt`` -> PV = t x D."""
    out: Dict[str, Any] = {"tax_rate": tax_rate}
    if interest_expense is not None:
        shields = [i * tax_rate for i in interest_expense]
        out["annual_tax_shield"] = shields
        if cost_of_debt is not None:
            out["pv_tax_shield"] = sum(s / (1 + cost_of_debt) ** (t + 1) for t, s in enumerate(shields))
    if permanent_debt is not None:
        out["pv_tax_shield_permanent_debt"] = tax_rate * permanent_debt
    return out


def book_vs_market_equity(book_equity: float, share_price: float, shares_outstanding: float) -> Dict[str, Any]:
    mv = share_price * shares_outstanding
    return {"book_value_of_equity": book_equity, "market_value_of_equity": mv,
            "price_to_book": safe_div(mv, book_equity), "book_value_per_share": book_equity / shares_outstanding,
            "market_premium_to_book": mv - book_equity}


def additional_paid_in_capital(offering_price: float, par_value: float, shares_issued: float) -> Dict[str, Any]:
    """Proceeds split between common stock (at par) and APIC (the excess over par)."""
    return {"total_proceeds": offering_price * shares_issued, "common_stock_at_par": par_value * shares_issued,
            "additional_paid_in_capital": (offering_price - par_value) * shares_issued}


def weighted_average_shares(beginning_shares: float, events: Sequence[Mapping[str, Any]] = (),
                            period_months: float = 12.0) -> Dict[str, Any]:
    """Events, each ``{"month": m, "shares": +/-n}`` (issued/bought back at the START of month m, 1-based, so it
    is outstanding for ``period_months - m + 1`` months) or ``{"month": m, "split_ratio": r}`` (applied to all
    shares for the whole period)."""
    split = 1.0
    for e in events:
        if "split_ratio" in e:
            split *= e["split_ratio"]
    rows = [{"description": "beginning shares", "shares": beginning_shares * split, "weight": 1.0}]
    for e in sorted((e for e in events if "shares" in e), key=lambda e: e["month"]):
        months_out = period_months - e["month"] + 1
        later_splits = 1.0          # only splits AFTER this issuance restate it; later issues are already post-split
        for s in events:
            if "split_ratio" in s and s["month"] > e["month"]:
                later_splits *= s["split_ratio"]
        rows.append({"description": f"{'issued' if e['shares'] > 0 else 'bought back'} month {e['month']}",
                     "shares": e["shares"] * later_splits, "weight": months_out / period_months})
    wa = sum(r["shares"] * r["weight"] for r in rows)
    ending = sum(r["shares"] for r in rows)
    return {"rows": rows, "weighted_average_shares": wa, "ending_shares": ending, "split_factor": split}


_FUNCS = {f.__name__: f for f in (market_cap, net_debt, enterprise_value_bridge, market_value_of_debt_estimate,
                                    market_value_of_debt_precise, tax_shield, book_vs_market_equity,
                                    additional_paid_in_capital, weighted_average_shares)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    unknown = [k for k in d if not str(k).startswith("_") and k not in _FUNCS]
    if unknown:
        raise KeyError(f"unknown function(s): {unknown}; available: {sorted(_FUNCS)}")
    return {k: _FUNCS[k](**v) for k, v in d.items() if not str(k).startswith("_")}
