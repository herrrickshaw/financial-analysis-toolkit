"""Cash vs accrual bridges — CFI's Cash to Accrual, Cash Flow Reconciliation and Working Capital Cycle templates.

  Cash to accrual     — accrual revenue = cash received + increase in receivables - increase in unearned
                        revenue; accrual expense = cash paid + increase in accrued/payables - increase in
                        prepaids. The usual small-business conversion when books are kept on a cash basis.
  Indirect CFO        — net income + non-cash charges - increase in operating assets + increase in operating
                        liabilities; ``cash_flow_reconciliation`` then adds investing and financing flows and
                        checks the total against the balance-sheet change in cash (gap should be zero).
  Working capital     — DSO = AR / revenue x days, DIO = inventory / COGS x days, DPO = AP / COGS x days;
  cycle                 cash conversion cycle = DSO + DIO - DPO; operating cycle = DSO + DIO."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .fin import safe_div


def cash_to_accrual_revenue(cash_received: float, receivables_begin: float, receivables_end: float,
                            unearned_revenue_begin: float = 0.0, unearned_revenue_end: float = 0.0) -> Dict[str, Any]:
    d_ar = receivables_end - receivables_begin
    d_unearned = unearned_revenue_end - unearned_revenue_begin
    return {"cash_received": cash_received, "change_in_receivables": d_ar, "change_in_unearned_revenue": d_unearned,
            "accrual_revenue": cash_received + d_ar - d_unearned}


def cash_to_accrual_expense(cash_paid: float, payables_begin: float = 0.0, payables_end: float = 0.0,
                            prepaid_begin: float = 0.0, prepaid_end: float = 0.0) -> Dict[str, Any]:
    """``payables`` covers accounts payable or accrued liabilities for this expense line; ``prepaid`` the
    prepaid asset (or inventory, for purchases -> cost of goods sold)."""
    d_pay = payables_end - payables_begin
    d_pre = prepaid_end - prepaid_begin
    return {"cash_paid": cash_paid, "change_in_payables": d_pay, "change_in_prepaids": d_pre,
            "accrual_expense": cash_paid + d_pay - d_pre}


def cash_to_accrual_statement(revenue: Mapping[str, Any], expenses: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    """Whole-statement conversion: ``revenue`` = kwargs for ``cash_to_accrual_revenue``; ``expenses`` = name ->
    kwargs for ``cash_to_accrual_expense``. Returns both bases side by side."""
    rev = cash_to_accrual_revenue(**revenue)
    lines = {k: cash_to_accrual_expense(**v) for k, v in expenses.items()}
    cash_profit = rev["cash_received"] - sum(l["cash_paid"] for l in lines.values())
    accrual_profit = rev["accrual_revenue"] - sum(l["accrual_expense"] for l in lines.values())
    return {"revenue": rev, "expenses": lines, "cash_basis_profit": cash_profit, "accrual_basis_profit": accrual_profit,
            "difference": accrual_profit - cash_profit}


def cash_flow_reconciliation(net_income: float, non_cash_items: Mapping[str, float],
                             working_capital: Mapping[str, Tuple[float, float, str]],
                             investing: Mapping[str, float], financing: Mapping[str, float],
                             cash_begin: Optional[float] = None, cash_end: Optional[float] = None) -> Dict[str, Any]:
    """Indirect-method cash flow statement. ``working_capital`` = name -> (begin, end, "asset"|"liability");
    ``investing``/``financing`` = signed cash flows (outflows negative)."""
    wc_lines = {}
    for name, (b, e, kind) in working_capital.items():
        if kind not in ("asset", "liability"):
            raise ValueError(f"{name}: kind must be 'asset' or 'liability'")
        wc_lines[name] = (b - e) if kind == "asset" else (e - b)
    cfo = net_income + sum(non_cash_items.values()) + sum(wc_lines.values())
    cfi, cff = sum(investing.values()), sum(financing.values())
    net = cfo + cfi + cff
    out: Dict[str, Any] = {"net_income": net_income, "non_cash_items": dict(non_cash_items), "working_capital_changes": wc_lines,
                           "cash_from_operations": cfo, "cash_from_investing": cfi, "cash_from_financing": cff,
                           "net_change_in_cash": net}
    if cash_begin is not None and cash_end is not None:
        out.update({"balance_sheet_change_in_cash": cash_end - cash_begin,
                    "reconciliation_gap": net - (cash_end - cash_begin)})
    return out


def working_capital_cycle(revenue: float, cogs: float, receivables: Sequence[float] | float,
                          inventory: Sequence[float] | float, payables: Sequence[float] | float,
                          days: float = 365.0) -> Dict[str, Any]:
    """Balances may be a single figure or ``[begin, end]`` (averaged — the usual analyst convention)."""
    avg = lambda x: (sum(x) / len(x)) if isinstance(x, (list, tuple)) else x
    ar, inv, ap = avg(receivables), avg(inventory), avg(payables)
    dso = safe_div(ar, revenue) * days
    dio = safe_div(inv, cogs) * days
    dpo = safe_div(ap, cogs) * days
    return {"dso": dso, "dio": dio, "dpo": dpo, "operating_cycle": dso + dio, "cash_conversion_cycle": dso + dio - dpo,
            "net_working_capital_trade": ar + inv - ap, "days_basis": days}


_FUNCS = {f.__name__: f for f in (cash_to_accrual_revenue, cash_to_accrual_expense, cash_to_accrual_statement,
                                    cash_flow_reconciliation, working_capital_cycle)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    unknown = [k for k in d if not str(k).startswith("_") and k not in _FUNCS]
    if unknown:
        raise KeyError(f"unknown function(s): {unknown}; available: {sorted(_FUNCS)}")
    out = {}
    for k, v in d.items():
        if str(k).startswith("_"):
            continue
        if k == "cash_flow_reconciliation":   # JSON has no tuples
            v = dict(v, working_capital={n: tuple(t) for n, t in v["working_capital"].items()})
        out[k] = _FUNCS[k](**v)
    return out
