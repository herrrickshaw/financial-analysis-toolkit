"""Single-purpose finance calculators — the time-value, rate and growth one-pagers that CFI ships as separate
small templates (Effective Annual Interest Rate, Future Value, Perpetuity, PVGO, CMGR, Geometric Mean, Capital
Gains Yield, Coupon Rate, Cost of Preferred Stock, Interest, CUMIPMT, HELOC, Markup, Sales Tax Decalculator,
Percentage Change, Annual Income, Revenue Run Rate, LTM, YoY, YTD).

Where a calculator mirrors a named Excel function (EFFECT, FV, CUMIPMT/CUMPRINC) it reproduces Excel's result,
and the tests check it against Microsoft's own documented examples. Unlike Excel, amounts come back POSITIVE
(interest paid, value accumulated); Excel's sign convention is noted where it differs."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence

from .fin import cagr, pmt, safe_div

# ----------------------------------------------------------------------------------------- rates and interest

def effective_annual_rate(nominal_rate: float, periods_per_year: Optional[int] = None) -> Dict[str, Any]:
    """Excel EFFECT: (1 + r/n)^n - 1. ``periods_per_year=None`` means continuous compounding, e^r - 1."""
    ear = math.exp(nominal_rate) - 1 if periods_per_year is None else (1 + nominal_rate / periods_per_year) ** periods_per_year - 1
    return {"nominal_rate": nominal_rate, "periods_per_year": periods_per_year or "continuous", "effective_annual_rate": ear}


def interest(principal: float, annual_rate: float, years: float, periods_per_year: Optional[int] = 1,
             simple: bool = False) -> Dict[str, Any]:
    """Interest earned on a lump sum. ``simple=True`` -> P*r*t; otherwise compounded ``periods_per_year`` times a
    year (``None`` = continuously)."""
    if simple:
        end = principal * (1 + annual_rate * years)
    elif periods_per_year is None:
        end = principal * math.exp(annual_rate * years)
    else:
        end = principal * (1 + annual_rate / periods_per_year) ** (periods_per_year * years)
    return {"principal": principal, "ending_balance": end, "interest": end - principal,
            "method": "simple" if simple else ("continuous" if periods_per_year is None else f"compound x{periods_per_year}/yr")}


def future_value(present_value: float, rate: float, periods: int, payment: float = 0.0, payment_at_start: bool = False) -> Dict[str, Any]:
    """Value after ``periods`` of a lump sum plus a level contribution each period (Excel FV with deposits entered
    as positives; Excel itself returns the negative of this)."""
    growth = (1 + rate) ** periods
    annuity = payment * periods if rate == 0 else payment * (growth - 1) / rate
    if payment_at_start:
        annuity *= (1 + rate)
    lump = present_value * growth
    return {"future_value": lump + annuity, "from_present_value": lump, "from_payments": annuity,
            "total_contributed": present_value + payment * periods}


def perpetuity(cash_flow_next_period: float, discount_rate: float, growth_rate: float = 0.0) -> Dict[str, Any]:
    """Present value of a (growing) perpetuity, CF1 / (r - g). Raises when g >= r: the value is unbounded."""
    if growth_rate >= discount_rate:
        raise ValueError("growth_rate must be below discount_rate for a perpetuity to have a finite value")
    return {"present_value": cash_flow_next_period / (discount_rate - growth_rate),
            "cash_flow_next_period": cash_flow_next_period, "discount_rate": discount_rate, "growth_rate": growth_rate}


def pvgo(share_price: float, next_year_eps: float, cost_of_equity: float) -> Dict[str, Any]:
    """Present value of growth opportunities: price minus the no-growth value EPS1 / r (all earnings paid out,
    no reinvestment). A negative PVGO means the market prices the firm below its no-growth value."""
    no_growth = next_year_eps / cost_of_equity
    g = share_price - no_growth
    return {"no_growth_value": no_growth, "pvgo": g, "pvgo_share_of_price": safe_div(g, share_price)}


def cumulative_interest_and_principal(rate: float, nper: int, pv: float, start_period: int, end_period: int,
                                      payment_at_start: bool = False) -> Dict[str, Any]:
    """Excel CUMIPMT and CUMPRINC for a level-payment loan, over periods ``start_period``..``end_period``
    (1-based, inclusive). Returned as positive amounts paid; Excel returns them negative."""
    if not 1 <= start_period <= end_period <= nper:
        raise ValueError("need 1 <= start_period <= end_period <= nper")
    payment = -pmt(rate, nper, pv, 0.0, 1 if payment_at_start else 0)
    balance, cum_int, cum_prin = pv, 0.0, 0.0
    for k in range(1, end_period + 1):
        # an annuity-due's first payment is made at t=0, before any interest accrues
        i = 0.0 if (payment_at_start and k == 1) else balance * rate
        principal = payment - i
        balance -= principal
        if k >= start_period:
            cum_int += i
            cum_prin += principal
    return {"payment": payment, "cumulative_interest": cum_int, "cumulative_principal": cum_prin,
            "balance_after_end_period": balance}


def heloc(home_value: float, max_combined_ltv: float, mortgage_balance: float, draw_amount: Optional[float] = None,
          annual_rate: float = 0.0, draw_years: int = 10, repayment_years: int = 20) -> Dict[str, Any]:
    """Home-equity line of credit: credit available = home value x maximum combined loan-to-value - existing
    mortgage(s). With a draw amount and rate, also the interest-only payment during the draw period and the
    level monthly payment once the repayment period starts (the payment-shock a borrower should plan for)."""
    available = max(0.0, home_value * max_combined_ltv - mortgage_balance)
    out: Dict[str, Any] = {"home_value": home_value, "max_combined_ltv": max_combined_ltv, "mortgage_balance": mortgage_balance,
                           "available_credit": available, "home_equity": home_value - mortgage_balance}
    if draw_amount is not None:
        if draw_amount > available:
            raise ValueError(f"draw {draw_amount:,.0f} exceeds available credit {available:,.0f}")
        r = annual_rate / 12
        io = draw_amount * r
        amort = -pmt(r, repayment_years * 12, draw_amount)
        out.update({"draw_amount": draw_amount, "interest_only_monthly_payment": io,
                    "repayment_monthly_payment": amort, "payment_increase_at_repayment": amort - io,
                    "draw_period_months": draw_years * 12, "repayment_period_months": repayment_years * 12})
    return out


# --------------------------------------------------------------------------------- returns, yields and growth

def cmgr(start_value: float, end_value: float, months: float) -> Dict[str, Any]:
    """Compound monthly growth rate, (end/start)^(1/months) - 1, with its annualised equivalent."""
    m = cagr(start_value, end_value, months)
    return {"cmgr": m, "annualised": (1 + m) ** 12 - 1, "months": months}


def geometric_mean_return(returns: Sequence[float]) -> Dict[str, Any]:
    """Geometric (compound) vs arithmetic average of periodic returns. The geometric mean is what an investor
    actually earned per period; the arithmetic mean overstates it whenever returns vary."""
    growth = 1.0
    for r in returns:
        growth *= 1 + r
    n = len(returns)
    return {"geometric_mean": growth ** (1 / n) - 1, "arithmetic_mean": sum(returns) / n, "cumulative_return": growth - 1, "periods": n}


def capital_gains_yield(beginning_price: float, ending_price: float, dividends: float = 0.0) -> Dict[str, Any]:
    """Capital gains yield (P1 - P0) / P0, dividend yield D / P0, and total holding-period return."""
    cg = (ending_price - beginning_price) / beginning_price
    dy = dividends / beginning_price
    return {"capital_gains_yield": cg, "dividend_yield": dy, "total_return": cg + dy}


def coupon_rate(annual_coupon_payment: float, face_value: float, price: Optional[float] = None) -> Dict[str, Any]:
    """Coupon rate = annual coupon / face value; with a price, also the current yield = annual coupon / price."""
    out = {"coupon_rate": annual_coupon_payment / face_value}
    if price:
        out["current_yield"] = annual_coupon_payment / price
    return out


def cost_of_preferred_stock(annual_dividend: float, price: float, flotation_cost_pct: float = 0.0) -> Dict[str, Any]:
    """Cost of (perpetual, non-convertible) preferred stock = Dp / (Pp x (1 - flotation cost))."""
    net = price * (1 - flotation_cost_pct)
    return {"cost_of_preferred": annual_dividend / net, "net_proceeds_per_share": net}


def percentage_change(old_value: float, new_value: float) -> Dict[str, Any]:
    """(new - old) / |old|; the absolute value keeps the sign meaningful when the base is negative."""
    if old_value == 0:
        raise ValueError("percentage change is undefined from a zero base")
    return {"change": new_value - old_value, "percentage_change": (new_value - old_value) / abs(old_value)}


def year_over_year(values: Sequence[float], labels: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
    """YoY change for each period after the first (None where the prior value is zero)."""
    labels = list(labels) if labels is not None else list(range(len(values)))
    return [{"period": labels[i], "value": values[i], "change": values[i] - values[i - 1],
             "yoy": None if values[i - 1] == 0 else (values[i] - values[i - 1]) / abs(values[i - 1])}
            for i in range(1, len(values))]


def year_to_date(monthly_current: Sequence[float], monthly_prior: Optional[Sequence[float]] = None,
                 through_month: Optional[int] = None) -> Dict[str, Any]:
    """YTD total through ``through_month`` (default: months supplied), and vs the same months of the prior year."""
    m = through_month or len(monthly_current)
    ytd = sum(monthly_current[:m])
    out: Dict[str, Any] = {"through_month": m, "ytd": ytd}
    if monthly_prior is not None:
        prior = sum(monthly_prior[:m])
        out.update({"prior_ytd": prior, "ytd_change": ytd - prior, "ytd_growth": safe_div(ytd - prior, abs(prior)) if prior else None})
    return out


def ltm(last_fiscal_year: float, current_ytd: float, prior_ytd: float) -> Dict[str, Any]:
    """Last twelve months = last full fiscal year + current year-to-date - the same YTD period a year earlier."""
    return {"ltm": last_fiscal_year + current_ytd - prior_ytd}


def revenue_run_rate(period_revenue: float, periods_per_year: int) -> Dict[str, Any]:
    """Annualised run rate (e.g. one month x 12). Overstates seasonal or one-off-heavy periods — a trailing
    figure (``ltm``) is the safer base when the period isn't representative."""
    return {"run_rate": period_revenue * periods_per_year, "period_revenue": period_revenue, "periods_per_year": periods_per_year}


# ------------------------------------------------------------------------------------------- pricing and pay

def markup(cost: float, price: float) -> Dict[str, Any]:
    """Markup is profit over COST; margin is profit over PRICE. A 50% markup is only a 33% margin."""
    profit = price - cost
    return {"profit": profit, "markup": safe_div(profit, cost), "margin": safe_div(profit, price)}


def price_from_markup(cost: float, markup_pct: float) -> Dict[str, Any]:
    price = cost * (1 + markup_pct)
    return {"price": price, **markup(cost, price)}


def price_from_margin(cost: float, margin_pct: float) -> Dict[str, Any]:
    if margin_pct >= 1:
        raise ValueError("margin must be below 100%")
    price = cost / (1 - margin_pct)
    return {"price": price, **markup(cost, price)}


def sales_tax_decalculator(total_including_tax: float, tax_rate: float) -> Dict[str, Any]:
    """Back out the pre-tax price from a tax-inclusive total: total / (1 + rate). (Not total x (1 - rate).)"""
    pre = total_including_tax / (1 + tax_rate)
    return {"pre_tax_amount": pre, "tax": total_including_tax - pre}


_PERIODS = {"hourly": None, "daily": None, "weekly": 52, "biweekly": 26, "semimonthly": 24, "monthly": 12, "annual": 1}


def annual_income(rate: float, period: str, hours_per_day: float = 8.0, days_per_week: float = 5.0,
                  weeks_per_year: float = 52.0) -> Dict[str, Any]:
    """Annualise pay quoted per hour / day / week / biweekly / semimonthly / month / year."""
    period = period.lower()
    if period not in _PERIODS:
        raise ValueError(f"period must be one of {sorted(_PERIODS)}")
    if period == "hourly":
        n = hours_per_day * days_per_week * weeks_per_year
    elif period == "daily":
        n = days_per_week * weeks_per_year
    else:
        n = _PERIODS[period]
    annual = rate * n
    return {"annual_income": annual, "monthly": annual / 12, "weekly": annual / weeks_per_year, "periods_per_year": n}


# ------------------------------------------------------------------------------------------------ dispatcher

_FUNCS = {f.__name__: f for f in (effective_annual_rate, interest, future_value, perpetuity, pvgo,
                                    cumulative_interest_and_principal, heloc, cmgr, geometric_mean_return,
                                    capital_gains_yield, coupon_rate, cost_of_preferred_stock, percentage_change,
                                    year_over_year, year_to_date, ltm, revenue_run_rate, markup, price_from_markup,
                                    price_from_margin, sales_tax_decalculator, annual_income)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Run every calculator named as a key, e.g. ``{"pvgo": {"share_price": 50, ...}, "markup": {...}}``."""
    unknown = [k for k in d if not str(k).startswith("_") and k not in _FUNCS]
    if unknown:
        raise KeyError(f"unknown calculator(s): {unknown}; available: {sorted(_FUNCS)}")
    return {k: _FUNCS[k](**v) for k, v in d.items() if not str(k).startswith("_")}
