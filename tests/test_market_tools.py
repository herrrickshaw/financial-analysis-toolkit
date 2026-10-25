"""finmodel.market_tools: alpha and expected returns by hand; moving averages by hand; the crossover backtest's
no-lookahead property; VaR against a hand-sorted sample and the normal formula; option-strategy payoffs,
breakevens, extremes and directional labels for the textbook strategies."""
import math
from statistics import NormalDist

import pytest

from finmodel import market_tools as T


def test_jensens_alpha_matches_cfi_formula():
    out = T.jensens_alpha(portfolio_return=0.15, risk_free_rate=0.03, beta=1.2, market_return=0.10)
    assert out["alpha"] == pytest.approx(0.15 - 0.03 - 1.2 * 0.07)


def test_expected_returns():
    s = T.expected_return_scenarios([0.25, 0.5, 0.25], [-0.10, 0.05, 0.20])
    assert s["expected_return"] == pytest.approx(0.05)
    assert s["std_dev"] == pytest.approx(math.sqrt(0.25 * 0.0225 * 2))
    with pytest.raises(ValueError):
        T.expected_return_scenarios([0.5, 0.4], [0.1, 0.2])
    p = T.portfolio_expected_return([2000, 3000, 5000], [0.06, 0.08, 0.10])
    assert p["expected_return"] == pytest.approx(0.2 * 0.06 + 0.3 * 0.08 + 0.5 * 0.10)


def test_moving_averages():
    px = [1, 2, 3, 4, 5]
    assert T.moving_average(px, 3, "sma") == [None, None, 2, 3, 4]
    assert T.moving_average(px, 3, "wma")[2] == pytest.approx((1 + 4 + 9) / 6)
    ema = T.moving_average(px, 3, "ema")
    assert ema[2] == 2 and ema[3] == pytest.approx(0.5 * 4 + 0.5 * 2)


def test_crossover_backtest_has_no_lookahead():
    px = [100 + i for i in range(30)] + [130 - 2 * i for i in range(30)]
    base = T.ma_crossover_backtest(px, 3, 10, cost_bps=5)
    shocked = T.ma_crossover_backtest(px[:-1] + [px[-1] * 10], 3, 10, cost_bps=5)
    # changing the LAST price cannot change any position, only the last bar's P&L
    assert base["position"] == shocked["position"]
    assert base["position"][0] == 0 and base["position"][1:] == base["signal"][:-1]
    assert base["trades"] >= 2 and 0 < base["exposure"] < 1
    assert base["max_drawdown"] > base["buy_and_hold_max_drawdown"]   # it exits the decline
    with pytest.raises(ValueError):
        T.ma_crossover_backtest(px, 10, 3)


def test_value_at_risk_historical_and_parametric():
    rets = [x / 100 for x in range(-10, 10)]            # -10% .. +9%, 20 points
    out = T.value_at_risk(rets, confidence=0.95, portfolio_value=1_000_000)
    q = sorted(rets)[0] + (sorted(rets)[1] - sorted(rets)[0]) * (19 * 0.05 - 0)   # interpolated 5th pct
    assert out["historical_var"] == pytest.approx(-q * 1_000_000)
    mu = sum(rets) / 20
    sd = math.sqrt(sum((r - mu) ** 2 for r in rets) / 19)
    assert out["parametric_var"] == pytest.approx(-(mu + NormalDist().inv_cdf(0.05) * sd) * 1_000_000)
    assert out["parametric_es"] > out["parametric_var"]
    ten = T.value_at_risk(rets, 0.95, 1_000_000, horizon_days=10)
    assert ten["historical_var"] == pytest.approx(out["historical_var"] * math.sqrt(10))


def test_directional_strategies():
    bcs = T.strategy_payoff(T.named_strategy("bull_call_spread", k1=100, k2=110, c1=5, c2=2))
    assert bcs["breakevens"] == [pytest.approx(103)]
    assert (bcs["max_profit"], bcs["max_loss"]) == pytest.approx((7, -3))
    assert bcs["view"] == "directional (bullish)"
    bps = T.strategy_payoff(T.named_strategy("bear_put_spread", k1=90, k2=100, p1=2, p2=6))
    assert bps["view"] == "directional (bearish)" and bps["breakevens"] == [pytest.approx(96)]
    cc = T.strategy_payoff(T.named_strategy("covered_call", stock_price=100, k=105, c=3))
    assert cc["max_profit"] == pytest.approx(8) and cc["breakevens"] == [pytest.approx(97)]


def test_non_directional_strategies():
    st = T.strategy_payoff(T.named_strategy("long_straddle", k=100, c=4, p=3))
    assert st["breakevens"] == [pytest.approx(93), pytest.approx(107)]
    assert st["max_profit"] is None and st["max_loss"] == pytest.approx(-7)
    assert st["view"] == "non-directional (long volatility)"
    short = T.strategy_payoff([{**l, "side": "short"} for l in T.named_strategy("long_straddle", k=100, c=4, p=3)])
    assert short["view"] == "non-directional (short volatility)" and short["max_loss"] is None
    ic = T.strategy_payoff(T.named_strategy("iron_condor", kp1=80, kp2=90, kc1=110, kc2=120, p1=1, p2=3, c1=3, c2=1))
    assert ic["view"] == "non-directional (range-bound)"
    assert (ic["max_profit"], ic["max_loss"]) == pytest.approx((4, -6))
    assert ic["breakevens"] == [pytest.approx(86), pytest.approx(114)]
    fly = T.strategy_payoff(T.named_strategy("long_call_butterfly", k1=90, k2=100, k3=110, c1=12, c2=6, c3=3))
    assert fly["max_profit"] == pytest.approx(7) and fly["view"] == "non-directional (range-bound)"


def test_from_dict_named_strategy_with_price_grid():
    out = T.from_dict({"strategy": {"name": "long_straddle", "k": 100, "c": 4, "p": 3, "prices": [80, 100, 120]},
                       "jensens_alpha": {"portfolio_return": 0.1, "risk_free_rate": 0.02, "beta": 1, "market_return": 0.08}})
    assert [r["pnl"] for r in out["strategy"]["payoff"]] == [13, -7, 13]
    assert out["jensens_alpha"]["alpha"] == pytest.approx(0.02)
