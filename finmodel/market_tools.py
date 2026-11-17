"""Market and trading tools — CFI's Alpha Calculator, Expected Return Example, Moving Averages, NVDA Moving
Average Algorithmic Trading Model, Market Risk Fundamentals and Directional / Non-directional Trading
Strategies templates.

  Jensen's alpha        — Rp - [Rf + beta x (Rm - Rf)], exactly CFI's Alpha Calculator formula.
  MA crossover backtest — the position decided at the close of day t is held over day t+1, so a signal never
                          earns the return of the bar that produced it (the usual lookahead error in
                          spreadsheet backtests). Costs are charged in basis points per unit of turnover.
  VaR / ES              — historical (empirical quantile of returns, linear interpolation) and parametric
                          (normal) Value-at-Risk, with expected shortfall; scaled to a horizon by sqrt(time),
                          which assumes i.i.d. returns.
  Option strategies     — expiry payoff of any combination of calls, puts and stock, with breakevens, max
                          profit/loss (``None`` = unlimited) and a directional / non-directional label from
                          comparing the payoff at very low and very high prices."""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any, Dict, List, Mapping, Optional, Sequence

# ------------------------------------------------------------------------------------------ returns and alpha

def capm_expected_return(risk_free_rate: float, beta: float, market_return: float) -> Dict[str, Any]:
    mrp = market_return - risk_free_rate
    return {"market_risk_premium": mrp, "expected_return": risk_free_rate + beta * mrp}


def jensens_alpha(portfolio_return: float, risk_free_rate: float, beta: float, market_return: float) -> Dict[str, Any]:
    capm = capm_expected_return(risk_free_rate, beta, market_return)
    return {**capm, "portfolio_return": portfolio_return, "alpha": portfolio_return - capm["expected_return"]}


def expected_return_scenarios(probabilities: Sequence[float], returns: Sequence[float]) -> Dict[str, Any]:
    """Probability-weighted expected return, variance and standard deviation of one investment."""
    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9):
        raise ValueError(f"probabilities sum to {sum(probabilities)}, not 1")
    er = sum(p * r for p, r in zip(probabilities, returns))
    var = sum(p * (r - er) ** 2 for p, r in zip(probabilities, returns))
    return {"expected_return": er, "variance": var, "std_dev": math.sqrt(var)}


def portfolio_expected_return(values_or_weights: Sequence[float], expected_returns: Sequence[float]) -> Dict[str, Any]:
    """Weights are derived from position values (they need not sum to one), as in CFI's Example 2."""
    total = sum(values_or_weights)
    w = [v / total for v in values_or_weights]
    return {"weights": w, "expected_return": sum(wi * r for wi, r in zip(w, expected_returns))}


# ------------------------------------------------------------------------------------------ moving averages

def moving_average(prices: Sequence[float], window: int, kind: str = "sma") -> List[Optional[float]]:
    """Trailing ``sma`` / ``wma`` (linear weights, newest heaviest) / ``ema`` (alpha = 2/(n+1), seeded with the
    first full-window SMA). Positions before the first full window are None."""
    n = len(prices)
    out: List[Optional[float]] = [None] * n
    if kind == "sma":
        for i in range(window - 1, n):
            out[i] = sum(prices[i - window + 1:i + 1]) / window
    elif kind == "wma":
        denom = window * (window + 1) / 2
        for i in range(window - 1, n):
            out[i] = sum(prices[i - window + 1 + j] * (j + 1) for j in range(window)) / denom
    elif kind == "ema":
        a = 2 / (window + 1)
        if n >= window:
            out[window - 1] = sum(prices[:window]) / window
            for i in range(window, n):
                out[i] = a * prices[i] + (1 - a) * out[i - 1]
    else:
        raise ValueError("kind must be sma, wma or ema")
    return out


def _max_drawdown(equity: Sequence[float]) -> float:
    peak, mdd = equity[0], 0.0
    for v in equity:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    return mdd


def ma_crossover_backtest(prices: Sequence[float], fast: int, slow: int, kind: str = "sma", long_short: bool = False,
                          cost_bps: float = 0.0) -> Dict[str, Any]:
    """Long (or long/short) when the fast MA is above the slow MA at the close; position applied next bar."""
    if fast >= slow:
        raise ValueError("fast window must be shorter than slow window")
    f, s = moving_average(prices, fast, kind), moving_average(prices, slow, kind)
    signal = [0] * len(prices)
    for t in range(len(prices)):
        if f[t] is not None and s[t] is not None:
            signal[t] = 1 if f[t] > s[t] else (-1 if long_short else 0)
    position = [0] + signal[:-1]                   # decided at close t, held over t+1
    equity, bh, trades = [1.0], [1.0], 0
    for t in range(1, len(prices)):
        r = prices[t] / prices[t - 1] - 1
        turnover = abs(position[t] - position[t - 1])
        trades += turnover > 0
        equity.append(equity[-1] * (1 + position[t] * r - turnover * cost_bps / 1e4))
        bh.append(bh[-1] * (1 + r))
    return {"signal": signal, "position": position, "equity_curve": equity, "total_return": equity[-1] - 1,
            "buy_and_hold_return": bh[-1] - 1, "max_drawdown": _max_drawdown(equity),
            "buy_and_hold_max_drawdown": _max_drawdown(bh), "trades": trades,
            "exposure": sum(1 for p in position if p != 0) / len(position)}


# ------------------------------------------------------------------------------------------------ market risk

def _quantile(xs: Sequence[float], q: float) -> float:
    s = sorted(xs)
    pos = (len(s) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def value_at_risk(returns: Sequence[float], confidence: float = 0.95, portfolio_value: float = 1.0,
                  horizon_days: float = 1.0) -> Dict[str, Any]:
    """Losses reported as positive numbers (in ``portfolio_value`` units)."""
    q = 1 - confidence
    scale = math.sqrt(horizon_days)
    hist_var = -_quantile(returns, q)
    tail = [r for r in returns if r <= -hist_var]
    hist_es = -sum(tail) / len(tail) if tail else hist_var
    mu = sum(returns) / len(returns)
    sd = math.sqrt(sum((r - mu) ** 2 for r in returns) / (len(returns) - 1))
    z = NormalDist().inv_cdf(q)
    par_var = -(mu + z * sd)
    par_es = -(mu - sd * NormalDist().pdf(z) / q)
    v = portfolio_value * scale
    return {"confidence": confidence, "horizon_days": horizon_days,
            "historical_var": hist_var * v, "historical_es": hist_es * v,
            "parametric_var": par_var * v, "parametric_es": par_es * v, "mean": mu, "std_dev": sd}


# ------------------------------------------------------------------------------------------ option strategies

def _leg_payoff(leg: Mapping[str, Any], s: float) -> float:
    kind, side, qty = leg["instrument"], leg.get("side", "long"), leg.get("quantity", 1)
    sign = 1 if side == "long" else -1
    if kind == "call":
        v = max(s - leg["strike"], 0) - leg["premium"]
    elif kind == "put":
        v = max(leg["strike"] - s, 0) - leg["premium"]
    elif kind == "stock":
        v = s - leg["price"]
    else:
        raise ValueError("instrument must be call, put or stock")
    return sign * qty * v


def strategy_payoff(legs: Sequence[Mapping[str, Any]], prices: Optional[Sequence[float]] = None) -> Dict[str, Any]:
    """Expiry profit/loss per unit of underlying. Breakevens and extremes are exact: the payoff is piecewise
    linear with kinks only at strikes, so it is evaluated at 0, every strike and well beyond the top strike."""
    strikes = sorted({l["strike"] for l in legs if "strike" in l} | {l["price"] for l in legs if l["instrument"] == "stock"})
    top = max(strikes) if strikes else 1.0
    kinks = [0.0] + strikes + [top * 3]
    pay = lambda s: sum(_leg_payoff(l, s) for l in legs)
    vals = [pay(k) for k in kinks]
    breakevens = []
    for (a, va), (b, vb) in zip(zip(kinks, vals), zip(kinks[1:], vals[1:])):
        if va == 0 and a not in breakevens:
            breakevens.append(a)
        elif va * vb < 0:
            breakevens.append(a + (b - a) * (-va) / (vb - va))
    right_slope = pay(top * 3 + 1) - pay(top * 3)
    max_profit = None if right_slope > 1e-12 else max(vals)
    max_loss = None if right_slope < -1e-12 else min(vals)
    low, high = vals[0], vals[-1]
    if math.isclose(low, high, rel_tol=1e-9, abs_tol=1e-9) and abs(right_slope) < 1e-12:
        view = "non-directional (range-bound)"
    elif right_slope > 1e-12 and low > min(vals) + 1e-12:
        view = "non-directional (long volatility)"
    elif right_slope < -1e-12 and low < max(vals) - 1e-12:
        view = "non-directional (short volatility)"
    elif high > low:
        view = "directional (bullish)"
    else:
        view = "directional (bearish)"
    out: Dict[str, Any] = {"breakevens": breakevens, "max_profit": max_profit, "max_loss": max_loss,
                           "net_premium": -sum((1 if l.get("side", "long") == "long" else -1) * l.get("quantity", 1) * l.get("premium", 0)
                                               for l in legs if l["instrument"] != "stock"),
                           "view": view}
    if prices is not None:
        out["payoff"] = [{"price": p, "pnl": pay(p)} for p in prices]
    return out


def named_strategy(name: str, **k: float) -> List[Dict[str, Any]]:
    """Legs for common strategies. Directional: bull_call_spread(k1,k2,c1,c2), bear_put_spread(k1,k2,p1,p2),
    covered_call(stock_price,k,c). Non-directional: long_straddle(k,c,p), long_strangle(kp,kc,p,c),
    long_call_butterfly(k1,k2,k3,c1,c2,c3), iron_condor(kp1,kp2,kc1,kc2,p1,p2,c1,c2) — k1 < k2 < ..."""
    L = lambda i, side, strike=None, prem=0.0, price=None: {k2: v for k2, v in
        {"instrument": i, "side": side, "strike": strike, "premium": prem, "price": price}.items() if v is not None}
    builders = {
        "bull_call_spread": lambda: [L("call", "long", k["k1"], k["c1"]), L("call", "short", k["k2"], k["c2"])],
        "bear_put_spread": lambda: [L("put", "long", k["k2"], k["p2"]), L("put", "short", k["k1"], k["p1"])],
        "covered_call": lambda: [L("stock", "long", price=k["stock_price"]), L("call", "short", k["k"], k["c"])],
        "long_straddle": lambda: [L("call", "long", k["k"], k["c"]), L("put", "long", k["k"], k["p"])],
        "long_strangle": lambda: [L("put", "long", k["kp"], k["p"]), L("call", "long", k["kc"], k["c"])],
        "long_call_butterfly": lambda: [L("call", "long", k["k1"], k["c1"]), {**L("call", "short", k["k2"], k["c2"]), "quantity": 2},
                                        L("call", "long", k["k3"], k["c3"])],
        "iron_condor": lambda: [L("put", "long", k["kp1"], k["p1"]), L("put", "short", k["kp2"], k["p2"]),
                                L("call", "short", k["kc1"], k["c1"]), L("call", "long", k["kc2"], k["c2"])],
    }
    if name not in builders:
        raise KeyError(f"unknown strategy {name!r}; available: {sorted(builders)}")
    return builders[name]()


_FUNCS = {f.__name__: f for f in (capm_expected_return, jensens_alpha, expected_return_scenarios, portfolio_expected_return,
                                    moving_average, ma_crossover_backtest, value_at_risk, strategy_payoff)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Keys are function names; ``{"strategy": {"name": ..., <named_strategy kwargs>}}`` builds and prices a
    named option strategy."""
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if str(k).startswith("_"):
            continue
        if k == "strategy":
            v = dict(v)
            name = v.pop("name")
            prices = v.pop("prices", None)
            out[k] = {"name": name, **strategy_payoff(named_strategy(name, **v), prices)}
        elif k in _FUNCS:
            out[k] = _FUNCS[k](**v)
        else:
            raise KeyError(f"unknown function {k!r}; available: {sorted(_FUNCS) + ['strategy']}")
    return out
