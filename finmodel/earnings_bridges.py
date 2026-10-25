"""Earnings and cash-flow measures built up from (or reconciled back to) the income statement — the bridge
templates CFI ships separately: EBT / EBIT / EBITDA examples, EBIT vs EBITDA, Adjusted EBITDA, Normalizing
Income Statements, NOPAT, Free Cash Flow, Cash EPS and FFO.

  Top-down vs bottom-up  — EBITDA, EBIT and EBT can be built from revenue down or from net income up;
                           ``income_statement_subtotals`` does both and reports the gap, which should be zero.
  Adjusted EBITDA         — a non-GAAP measure: EBITDA plus management's add-backs. SEC Regulation G requires
                           it to be reconciled to the nearest GAAP measure, so every add-back is itemised.
  Normalised earnings     — strips non-recurring items out of net income AFTER tax (each pre-tax item moves
                           net income by amount x (1 - t)).
  FFO / AFFO              — Nareit's REIT measure: net income + real-estate depreciation/amortisation - gains
                           (+ losses) on sales of depreciable property + impairments of depreciable property.
                           AFFO has no standard definition; the deductions used here are the common ones."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from .fin import safe_div


def income_statement_subtotals(revenue: float, cogs: float, operating_expenses: float, depreciation_amortization: float,
                               interest_expense: float, taxes: float, interest_income: float = 0.0,
                               other_non_operating_income: float = 0.0,
                               net_income: Optional[float] = None) -> Dict[str, Any]:
    """Revenue-down subtotals. ``operating_expenses`` EXCLUDES depreciation & amortisation (SG&A, R&D, etc.).
    Give a reported ``net_income`` to also rebuild EBT/EBIT/EBITDA bottom-up and see the reconciliation gap."""
    gross_profit = revenue - cogs
    ebitda = gross_profit - operating_expenses
    ebit = ebitda - depreciation_amortization
    ebt = ebit - interest_expense + interest_income + other_non_operating_income
    ni = ebt - taxes
    out: Dict[str, Any] = {"gross_profit": gross_profit, "ebitda": ebitda, "ebit": ebit, "ebt": ebt, "net_income": ni,
                           "gross_margin": safe_div(gross_profit, revenue), "ebitda_margin": safe_div(ebitda, revenue),
                           "ebit_margin": safe_div(ebit, revenue), "effective_tax_rate": safe_div(taxes, ebt)}
    if net_income is not None:
        ebt_up = net_income + taxes
        ebit_up = ebt_up + interest_expense - interest_income - other_non_operating_income
        out["bottom_up"] = {"ebt": ebt_up, "ebit": ebit_up, "ebitda": ebit_up + depreciation_amortization,
                            "gap_vs_top_down": ebit_up - ebit}
    return out


def adjusted_ebitda(ebitda: float, addbacks: Mapping[str, float], revenue: Optional[float] = None) -> Dict[str, Any]:
    """EBITDA + itemised add-backs (positive = expense added back, negative = gain removed). Returns the
    reconciliation table and how much of Adjusted EBITDA comes from adjustments — a high share is the usual
    red flag in a lender's or buyer's review."""
    total = sum(addbacks.values())
    adj = ebitda + total
    return {"ebitda": ebitda, "addbacks": dict(addbacks), "total_addbacks": total, "adjusted_ebitda": adj,
            "addbacks_share_of_adjusted": safe_div(total, adj),
            "adjusted_ebitda_margin": safe_div(adj, revenue) if revenue else None}


def normalize_net_income(reported_net_income: float, adjustments: List[Mapping[str, Any]], tax_rate: float,
                         diluted_shares: Optional[float] = None) -> Dict[str, Any]:
    """Normalise net income for non-recurring items. Each adjustment: ``{"item": str, "pretax": float}`` with
    the sign of its effect on PRE-TAX income when removed (a one-off charge -> positive; a one-off gain ->
    negative). Optional ``"tax_rate"`` per item (e.g. a non-deductible fine -> 0)."""
    rows, total = [], 0.0
    for a in adjustments:
        t = a.get("tax_rate", tax_rate)
        after = a["pretax"] * (1 - t)
        rows.append({"item": a["item"], "pretax": a["pretax"], "tax_rate": t, "after_tax": after})
        total += after
    norm = reported_net_income + total
    out: Dict[str, Any] = {"reported_net_income": reported_net_income, "adjustments": rows,
                           "total_after_tax_adjustment": total, "normalized_net_income": norm}
    if diluted_shares:
        out.update({"reported_eps": reported_net_income / diluted_shares, "normalized_eps": norm / diluted_shares})
    return out


def nopat(ebit: float, tax_rate: float) -> Dict[str, Any]:
    """Net operating profit after tax = EBIT x (1 - t): operating profit as if the firm had no debt."""
    return {"ebit": ebit, "tax_rate": tax_rate, "nopat": ebit * (1 - tax_rate), "operating_taxes": ebit * tax_rate}


def free_cash_flow(ebit: float, tax_rate: float, depreciation_amortization: float, capex: float,
                   change_in_nwc: float, interest_expense: float = 0.0, net_borrowing: float = 0.0,
                   cash_from_operations: Optional[float] = None) -> Dict[str, Any]:
    """FCFF = EBIT(1 - t) + D&A - capex - increase in NWC; FCFE = FCFF - interest(1 - t) + net borrowing.
    With ``cash_from_operations`` also the simple FCF = CFO - capex used in most press releases."""
    fcff = ebit * (1 - tax_rate) + depreciation_amortization - capex - change_in_nwc
    fcfe = fcff - interest_expense * (1 - tax_rate) + net_borrowing
    out = {"nopat": ebit * (1 - tax_rate), "fcff": fcff, "fcfe": fcfe}
    if cash_from_operations is not None:
        out["simple_fcf"] = cash_from_operations - capex
    return out


def cash_eps(cash_from_operations: float, diluted_shares: float, net_income: Optional[float] = None) -> Dict[str, Any]:
    """Cash EPS = operating cash flow / diluted shares. Next to accounting EPS it shows how much of reported
    earnings turned into cash (cash conversion = CFO / net income)."""
    out = {"cash_eps": cash_from_operations / diluted_shares}
    if net_income is not None:
        out.update({"eps": net_income / diluted_shares, "cash_conversion": safe_div(cash_from_operations, net_income)})
    return out


def ffo(net_income: float, real_estate_depreciation_amortization: float, gains_on_property_sales: float = 0.0,
        impairments_of_depreciable_real_estate: float = 0.0, shares: Optional[float] = None,
        recurring_capex: float = 0.0, straight_line_rent_adjustment: float = 0.0,
        non_cash_compensation: float = 0.0) -> Dict[str, Any]:
    """Nareit FFO and a common AFFO. ``gains_on_property_sales`` is the NET gain (a loss is negative).
    AFFO = FFO - recurring (maintenance) capex - straight-line rent adjustment + non-cash compensation."""
    f = net_income + real_estate_depreciation_amortization - gains_on_property_sales + impairments_of_depreciable_real_estate
    a = f - recurring_capex - straight_line_rent_adjustment + non_cash_compensation
    out: Dict[str, Any] = {"ffo": f, "affo": a}
    if shares:
        out.update({"ffo_per_share": f / shares, "affo_per_share": a / shares})
    return out


_FUNCS = {f.__name__: f for f in (income_statement_subtotals, adjusted_ebitda, normalize_net_income, nopat,
                                    free_cash_flow, cash_eps, ffo)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    unknown = [k for k in d if not str(k).startswith("_") and k not in _FUNCS]
    if unknown:
        raise KeyError(f"unknown function(s): {unknown}; available: {sorted(_FUNCS)}")
    return {k: _FUNCS[k](**v) for k, v in d.items() if not str(k).startswith("_")}
