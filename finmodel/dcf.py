"""Unlevered DCF, distilled from CFI 'DCF Model Template (Updated)'.

  UFCF  = EBIT - cash taxes + D&A - capex - change in NWC
  TV    = average of  perpetuity-growth TV  and  exit EV/EBITDA-multiple TV   (CFI default; selectable)
  EV    = XNPV(discount rate, [0, UFCF_1*yf_1, ..., UFCF_n*yf_n, TV], dates)  -- stub-period aware
  Equity value = EV + cash - debt ;  per share = / shares ;  IRR = XIRR of (-market EV, flows..., TV)

Dates: period t ends on the fiscal-year-end month/day of (FYE.year + t); the first period runs from the
transaction date to that FYE, so its year-fraction (Excel YEARFRAC basis 0) scales the first flow.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Sequence

from .fin import to_date, yearfrac, xnpv, xirr


@dataclass
class DCFInputs:
    ebit: List[float]
    da: List[float]
    change_nwc: List[float]
    capex: Any                     # scalar or list (per forecast year)
    tax_rate: float = 0.25
    discount_rate: float = 0.12
    perpetual_growth: float = 0.03
    ev_ebitda_multiple: float = 7.0
    transaction_date: Any = "2017-12-31"
    fiscal_year_end: Any = "2018-06-30"
    current_price: float = 25.0
    shares_outstanding: float = 20000.0
    debt: float = 30000.0
    cash: float = 0.0
    terminal_method: str = "average"   # "average" | "perpetuity" | "multiple"
    yearfrac_basis: int = 0

    def capex_list(self) -> List[float]:
        n = len(self.ebit)
        if isinstance(self.capex, (int, float)):
            return [float(self.capex)] * n
        c = [float(x) for x in self.capex]
        if len(c) != n:
            raise ValueError("capex list must match ebit length")
        return c


def period_dates(transaction_date, fiscal_year_end, n: int) -> List[date]:
    """[transaction_date, FYE(y0), FYE(y0+1), ..., FYE(y0+n-1)]"""
    t0 = to_date(transaction_date)
    fye = to_date(fiscal_year_end)
    out = [t0]
    for t in range(n):
        y = fye.year + t
        d = fye.day
        # handle Feb-29 style FYE safely
        while True:
            try:
                out.append(date(y, fye.month, d))
                break
            except ValueError:
                d -= 1
    return out


def run(inp: DCFInputs) -> Dict[str, Any]:
    n = len(inp.ebit)
    if not (len(inp.da) == len(inp.change_nwc) == n):
        raise ValueError("ebit, da and change_nwc must have the same length")
    capex = inp.capex_list()
    dates = period_dates(inp.transaction_date, inp.fiscal_year_end, n)
    yf = [yearfrac(dates[t], dates[t + 1], inp.yearfrac_basis) for t in range(n)]
    taxes = [e * inp.tax_rate for e in inp.ebit]
    ufcf = [inp.ebit[t] - taxes[t] + inp.da[t] - capex[t] - inp.change_nwc[t] for t in range(n)]
    ebitda_last = inp.ebit[-1] + inp.da[-1]
    r, g = inp.discount_rate, inp.perpetual_growth
    if r <= g:
        raise ValueError("discount rate must exceed perpetual growth rate")
    tv_perp = ufcf[-1] * (1 + g) / (r - g)
    tv_mult = inp.ev_ebitda_multiple * ebitda_last
    tv = {"average": (tv_perp + tv_mult) / 2, "perpetuity": tv_perp, "multiple": tv_mult}[inp.terminal_method]

    market_cap = inp.shares_outstanding * inp.current_price
    market_ev = market_cap + inp.debt - inp.cash

    # valuation flows: entry 0, scaled FCFs, terminal value at last date
    val_flows = [0.0] + [ufcf[t] * yf[t] for t in range(n)] + [tv]
    val_dates = dates + [dates[-1]]
    ev = xnpv(r, val_flows, val_dates)
    equity = ev + inp.cash - inp.debt
    per_share = equity / inp.shares_outstanding

    # rate-of-return flows: pay market EV at entry, receive FCFs and TV
    irr_flows = [-market_ev] + [ufcf[t] * yf[t] for t in range(n)] + [tv]
    try:
        irr_val = xirr(irr_flows, val_dates)
    except ValueError:
        irr_val = float("nan")

    return {
        "dates": [d.isoformat() for d in dates],
        "years": [d.year for d in dates[1:]],
        "year_fraction": yf,
        "ebit": list(inp.ebit), "cash_taxes": taxes, "da": list(inp.da), "capex": capex,
        "change_nwc": list(inp.change_nwc), "ufcf": ufcf,
        "terminal_value": {"perpetuity_growth": tv_perp, "ev_ebitda": tv_mult, "used": tv, "method": inp.terminal_method},
        "valuation_flows": val_flows,
        "enterprise_value": ev, "plus_cash": inp.cash, "less_debt": inp.debt,
        "equity_value": equity, "equity_value_per_share": per_share,
        "market": {"market_cap": market_cap, "plus_debt": inp.debt, "less_cash": inp.cash,
                   "enterprise_value": market_ev, "price": inp.current_price},
        "target_price_upside": per_share / inp.current_price - 1,
        "upside_per_share": per_share - inp.current_price,
        "irr": irr_val,
        "discount_rate": r, "perpetual_growth": g,
    }


def sensitivity(inp: DCFInputs, discount_rates: Sequence[float], growth_rates: Sequence[float],
                metric: str = "equity_value_per_share") -> Dict[str, Any]:
    """2-D table of `metric` across discount rate (rows) x perpetual growth (cols)."""
    from dataclasses import replace
    table = []
    for r in discount_rates:
        row = []
        for g in growth_rates:
            try:
                row.append(run(replace(inp, discount_rate=r, perpetual_growth=g))[metric])
            except ValueError:
                row.append(float("nan"))
        table.append(row)
    return {"rows": list(discount_rates), "cols": list(growth_rates), "metric": metric, "table": table}


def clean(d: Dict[str, Any]) -> Dict[str, Any]:
    """Drop comment keys (those starting with '_')."""
    return {k: v for k, v in d.items() if not str(k).startswith("_")}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    return run(DCFInputs(**clean(d)))
