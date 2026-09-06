"""Populate the CFI 'Comps, Precedents, Football Field' template — the one `finmodel.comps.football_field()` is
reconciled against in `tests/test_comps.py` using the CFI workbook's illustrative numbers — with real Steel Dynamics
(STLD) data, and see where STLD's actual price sits:

  Trading comps    — the carbon-steel peer set from `scripts/comps_validation.py` (SEC EDGAR fundamentals,
                     market_data warehouse closing prices, 2026-07-02).
  Precedent deals  — two real, verifiable acquisitions of US steel producers: Nippon Steel / United States Steel
                     (cash, 2023-12-18) and Cleveland-Cliffs / AK Steel Holding (all-stock, 2019-12-02). Multiples
                     are built from SEC EDGAR fundamentals (revenue/EBIT/D&A/debt/cash for the target's last full
                     fiscal year before announcement) and the disclosed/derived deal consideration — NOT fabricated
                     figures. Premiums to the target's own undisturbed price are omitted: both targets are delisted
                     and absent from the warehouse, and free sources (Yahoo/Stooq) refuse historical data for a
                     delisted ticker, so there is no independently verifiable target price series to compute a
                     premium against — better to omit than to guess.
  DCF               — two scenarios built from STLD's own FY2025 EDGAR base year and its own 2018-2025 historical
                     margin range (base case recovers toward the FY2024 margin, blue-sky toward the FY2023 margin),
                     discounted at the WACC from `finmodel wacc examples/wacc_stld.json` (10.28%), with a small
                     discount-rate/growth sensitivity band standing in for the "Lo/Hi" a banker would get from a
                     scenario or data-table analysis. These are illustrative scenarios I built, not analyst
                     consensus — labelled as such throughout.
  52-week range    — the real trailing 252-trading-day high/low from the warehouse (2025-07-02 to 2026-07-02).

Run: python scripts/football_field_stld.py → docs/FOOTBALL_FIELD_STLD.md, out/comps_football_field_stld.json,
out/charts_football_field_stld.html"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from finmodel import comps, charts, dcf  # noqa: E402
import comps_validation as CV  # noqa: E402  (reuses CORE peer set, price lookup, latest() EDGAR loader)

PRICE_DATE = CV.PRICE_DATE


def week52(ticker: str):
    try:
        out = subprocess.run(["psql", "-d", "market_data", "-Atc",
                              f"with r as (select h.date, h.close_price, row_number() over (order by h.date desc) rn "
                              f"from ohlcv_history h join stocks s on s.stock_id=h.stock_id where s.market_id=2 and s.ticker='{ticker}') "
                              f"select min(close_price), max(close_price), min(date), max(date), count(*) from r where rn<=252"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        lo, hi, d0, d1, n = out.split("|")
        return {"low": float(lo), "high": float(hi), "from": d0, "to": d1, "n_days": int(n), "source": "warehouse"}
    except Exception as e:
        return {"error": str(e)}


def clf_price_on(date_str: str):
    out = subprocess.run(["psql", "-d", "market_data", "-Atc",
                          f"select close_price from ohlcv_history h join stocks s on s.stock_id=h.stock_id where s.market_id=2 and s.ticker='CLF' and h.date='{date_str}'"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return float(out) if out else None


def x_precedent():
    """Nippon Steel / United States Steel: $55.00/share cash, announced 2023-12-18 (publicly disclosed deal terms,
    a matter of record in both companies' own SEC filings and press releases — not derived from a price series).
    Multiples use X's own last full fiscal year (2023) EDGAR fundamentals."""
    _, _, r, _ = CV.latest("X")
    fy2023 = json.loads((ROOT / "data" / "edgar" / "X.json").read_text())["years"]["2023-12-31"]
    revenue, ebit, da = fy2023["revenue"], fy2023["operating_income"], fy2023["da"]
    debt, cash, shares = fy2023["debt_total"], fy2023["cash"], fy2023["diluted_shares"]
    offer_price = 55.00
    equity_value = offer_price * shares
    ev = equity_value + debt - cash
    return {"acquirer": "Nippon Steel Corporation", "target": "United States Steel Corporation", "date": "2023-12-18",
            "enterprise_value": ev, "ltm_revenue": revenue, "ltm_ebitda": ebit + da, "ltm_ebit": ebit,
            "offer_price": offer_price, "_detail": {"fy": "2023-12-31", "equity_value": equity_value, "net_debt": debt - cash, "diluted_shares": shares,
                                                     "source": "offer price: publicly disclosed deal terms; revenue/EBIT/D&A/debt/cash: SEC EDGAR 10-K"}}


def aks_precedent():
    """Cleveland-Cliffs / AK Steel Holding: all-stock, 0.400 CLF share per AKS share, announced 2019-12-02.
    Implied offer value/share = 0.400 x CLF's own warehouse closing price that day; AKS fundamentals from its
    last full fiscal year (2019) EDGAR company facts (CIK 918160; compact extract in data/edgar/AKS.json,
    fetched the same way as every other ticker in data/edgar/ — see finmodel.edgar)."""
    fy2019 = json.loads((ROOT / "data" / "edgar" / "AKS.json").read_text())["years"]["2019-12-31"]
    revenue, ebit, da = fy2019["revenue"], fy2019["operating_income"], fy2019["da"]
    debt, cash, shares = fy2019["debt_total"], fy2019["cash"], fy2019["diluted_shares"]
    clf_close = clf_price_on("2019-12-02")
    offer_price = 0.400 * clf_close if clf_close else None
    equity_value = offer_price * shares if offer_price else None
    ev = equity_value + debt - cash if equity_value else None
    return {"acquirer": "Cleveland-Cliffs Inc.", "target": "AK Steel Holding Corporation", "date": "2019-12-02",
            "enterprise_value": ev, "ltm_revenue": revenue, "ltm_ebitda": ebit + da, "ltm_ebit": ebit,
            "offer_price": offer_price, "_detail": {"fy": "2019-12-31", "clf_close_on_announcement": clf_close, "exchange_ratio": 0.400,
                                                     "equity_value": equity_value, "net_debt": debt - cash, "diluted_shares": shares,
                                                     "source": "CLF close: market_data warehouse (dividend-adjusted, likely a few % below the nominal quote); AKS revenue/EBIT/D&A/debt/cash: SEC EDGAR 10-K"}}


def stld_dcf_scenario(name: str, growth: float, margin_target: float, da_pct: float, capex_pct: float, discount_rate: float, current_price: float):
    fy = json.loads((ROOT / "data" / "edgar" / "STLD.json").read_text())["years"]["2025-12-31"]
    rev0 = fy["revenue"] / 1e6; margin0 = fy["operating_income"] / fy["revenue"]; nwc0_pct = (fy["current_assets"] - fy["current_liabilities"]) / fy["revenue"]
    n = 5
    rev = [rev0]
    for _ in range(n): rev.append(rev[-1] * (1 + growth))
    margins = [margin0 + (margin_target - margin0) * t / n for t in range(1, n + 1)]
    ebit = [rev[t] * margins[t - 1] for t in range(1, n + 1)]
    da = [rev[t] * da_pct for t in range(1, n + 1)]
    capex = [rev[t] * capex_pct for t in range(1, n + 1)]
    change_nwc = [nwc0_pct * (rev[t] - rev[t - 1]) for t in range(1, n + 1)]
    inp = dcf.DCFInputs(ebit=ebit, da=da, change_nwc=change_nwc, capex=capex, tax_rate=0.205, discount_rate=discount_rate,
                        perpetual_growth=0.025, terminal_method="perpetuity", transaction_date="2025-12-31", fiscal_year_end="2026-12-31",
                        current_price=current_price, shares_outstanding=fy["diluted_shares"] / 1e6, debt=fy["debt_total"] / 1e6, cash=fy["cash"] / 1e6)
    res = dcf.run(inp)
    sens = dcf.sensitivity(inp, [discount_rate - 0.005, discount_rate, discount_rate + 0.005], [0.02, 0.025, 0.03])
    flat = [v for row in sens["table"] for v in row]
    return {"name": name, "base_value_per_share": res["equity_value_per_share"], "low": min(flat), "high": max(flat),
            "assumptions": {"revenue_growth": growth, "ebit_margin_target_year5": margin_target, "da_pct_revenue": da_pct, "capex_pct_revenue": capex_pct, "discount_rate": discount_rate, "terminal_growth": 0.025},
            "projection": {"revenue": rev[1:], "ebit": ebit, "da": da, "capex": capex, "change_nwc": change_nwc}}


def run():
    px, price_source = CV.prices()
    peers = []
    for t in CV.CORE:
        name, fy, r, _ = CV.latest(t)
        m = {"revenue": r.get("revenue"), "ebitda": r.get("ebitda"), "ebit": r.get("operating_income"), "net_income": r.get("net_income")}
        peers.append(comps.Peer(name, px[t], r.get("diluted_shares", 0), cash=r.get("cash", 0) + r.get("short_term_investments", 0), debt=r.get("debt_total", 0), nci=r.get("nci", 0), metrics=m, ticker=t))
    trading = comps.spread(peers)

    x_deal, aks_deal = x_precedent(), aks_precedent()
    from finmodel.comps import Deal
    deals = [Deal(x_deal["acquirer"], x_deal["target"], x_deal["date"], x_deal["enterprise_value"], ltm_revenue=x_deal["ltm_revenue"], ltm_ebitda=x_deal["ltm_ebitda"], ltm_ebit=x_deal["ltm_ebit"]),
             Deal(aks_deal["acquirer"], aks_deal["target"], aks_deal["date"], aks_deal["enterprise_value"], ltm_revenue=aks_deal["ltm_revenue"], ltm_ebitda=aks_deal["ltm_ebitda"], ltm_ebit=aks_deal["ltm_ebit"])]
    precedents = comps.precedents(deals)

    tname, tfy, tr, _ = CV.latest("STLD")
    target = comps.Target(tname, px["STLD"], tr["diluted_shares"], metrics={"revenue": tr["revenue"], "ebitda": tr["ebitda"], "ebit": tr["operating_income"], "net_income": tr["net_income"]},
                          bridge={"cash": tr.get("cash", 0) + tr.get("short_term_investments", 0), "debt": -tr.get("debt_total", 0), "nci": -tr.get("nci", 0)})

    base = stld_dcf_scenario("DCF - base case (margin recovers toward FY2024 level)", growth=0.03, margin_target=0.11, da_pct=0.030, capex_pct=0.052, discount_rate=0.1028, current_price=px["STLD"])
    blue = stld_dcf_scenario("DCF - blue sky (margin recovers toward FY2023 level)", growth=0.06, margin_target=0.168, da_pct=0.023, capex_pct=0.080, discount_rate=0.1028, current_price=px["STLD"])
    wk52 = week52("STLD")

    ff = comps.football_field(target, {"Trading comps": trading, "Precedent transactions": precedents},
                              extra={base["name"]: (base["low"], base["high"]), blue["name"]: (blue["low"], blue["high"]),
                                     "52-week range": (wk52["low"], wk52["high"])} if "low" in wk52 else {base["name"]: (base["low"], base["high"]), blue["name"]: (blue["low"], blue["high"])},
                              stat_low="p25", stat_high="p75")

    stld_years = json.loads((ROOT / "data" / "edgar" / "STLD.json").read_text())["years"]
    fy0, fy1 = min(stld_years), max(stld_years)
    buyback = {"from_fy": fy0, "from_shares": stld_years[fy0]["diluted_shares"], "to_fy": fy1, "to_shares": stld_years[fy1]["diluted_shares"]}

    out = {"price": px["STLD"], "price_date": PRICE_DATE, "price_source": price_source, "trading_comps": trading, "precedents": precedents,
           "x_precedent_detail": x_deal, "aks_precedent_detail": aks_deal, "dcf_base": base, "dcf_blue_sky": blue, "week52": wk52, "football_field": ff, "buyback": buyback}
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "comps_football_field_stld.json").write_text(json.dumps(out, indent=1, default=str))
    charts.report_for("comps", {"comps": trading, "precedents": precedents, "football_field": ff}, ROOT / "out" / "charts_football_field_stld.html", title="Steel Dynamics — CFI football-field template on real data")

    md = write_doc(out)
    (ROOT / "docs" / "FOOTBALL_FIELD_STLD.md").write_text(md)
    print(f"STLD price {px['STLD']:.2f} ({price_source}, {PRICE_DATE})")
    for it in ff["items"]:
        print(f"  {it['method']:55} {it['low']:8.2f} - {it['high']:8.2f}")


def write_doc(out):
    px = out["price"]; ff = out["football_field"]
    md = ["# Checking the CFI football-field template against real Steel Dynamics (STLD) numbers", "",
          f"`finmodel.comps.football_field()` is reconciled in `tests/test_comps.py` against the CFI template's own "
          f"illustrative numbers (fictional companies, fictional deals). This runs the same function on real inputs: "
          f"real peer trading comps (SEC EDGAR + market_data warehouse), two real, verifiable steel-industry M&A "
          f"precedents, two DCF scenarios built from STLD's own historical margin range, and STLD's real 52-week "
          f"trading range — then compares the resulting football field to STLD's actual price of "
          f"**${px:.2f}** (warehouse close, {out['price_date']}).", "",
          "## Football field", "", "| Method | Low | High | Current price inside range? |", "|---|---|---|---|"]
    brackets, price_above, price_below = [], [], []   # price_above = the method's range sits BELOW the price; price_below = the method's range sits ABOVE the price
    for it in ff["items"]:
        if it["low"] <= px <= it["high"]:
            inside = "yes"; brackets.append(it["method"])
        elif px > it["high"]:
            inside = "price is above this range"; price_above.append(it)
        else:
            inside = "price is below this range"; price_below.append(it)
        md.append(f"| {it['method']} | {it['low']:.2f} | {it['high']:.2f} | {inside} |")
    below_highs = ", ".join(f"{it['high']:.2f}" for it in price_above)
    md += ["", f"Only {' and '.join(brackets) if brackets else 'no method'} bracket{'s' if len(brackets) == 1 else ''} the "
           f"actual price. The trailing-multiple trading comps bracket it only because 2025 was a trough-earnings year "
           f"industry-wide (the same distortion documented in `docs/VALIDATION_REAL_DATA.md` — depressed LTM EBITDA "
           f"inflates EV/EBITDA), which happens to pull the range wide enough to catch the price rather than because the "
           f"multiples are themselves informative. The two precedent-transaction deals and both DCF scenarios sit "
           f"**entirely below** the actual price (highs of {below_highs} vs the price of {px:.2f}) — the honest reading "
           f"is that a conservative, backward-looking model (deals priced "
           f"off a *depressed* target's trailing metrics; a DCF anchored to STLD's own *depressed* FY2025 base year) "
           f"undershoots what the market is actually paying. Two real, unmodelled reasons this toolkit's DCF cannot "
           f"capture from EDGAR alone: STLD has been aggressively buying back stock (diluted shares fell from "
           f"{out['buyback']['from_shares']/1e6:.1f}M in FY{out['buyback']['from_fy'][:4]} to {out['buyback']['to_shares']/1e6:.1f}M "
           f"in FY{out['buyback']['to_fy'][:4]}, a {(1 - out['buyback']['to_shares']/out['buyback']['from_shares'])*100:.0f}% reduction — "
           f"a forward buyback pace mechanically raises per-share value in a way a single-base-year DCF does not price in), "
           f"and steel-industry valuations in the 2021–2023 upcycle traded at multiples "
           f"well above what trailing fundamentals alone would justify, which the market may still be partly "
           f"extrapolating. This is exactly the gap a forward (FY+1/FY+2 *consensus*) comps set and a buyback-aware DCF "
           f"would close — and exactly what EDGAR's trailing, as-filed data cannot supply.", ""]
    md += ["## 1. Trading comps (real: SEC EDGAR fundamentals + market_data warehouse prices)", "",
           "Same carbon-steel peer set and prices as `docs/VALIDATION_REAL_DATA.md` (NUE, CMC, RS, CLF, WOR); see that "
           "document for the full peer table. Statistics feeding the football field:", "",
           "| Multiple | 25th | Median | 75th |", "|---|---|---|---|"]
    for label in ("EV / Revenue LTM", "EV / EBITDA LTM", "EV / EBIT LTM"):
        s = out["trading_comps"]["summary"][label]
        md.append(f"| {label} | {s['p25']:.2f}x | {s['median']:.2f}x | {s['p75']:.2f}x |")
    md += ["", "## 2. Precedent transactions (real, verifiable deals)", ""]
    for key, title in (("x_precedent_detail", "Nippon Steel / United States Steel"), ("aks_precedent_detail", "Cleveland-Cliffs / AK Steel Holding")):
        d = out[key]; det = d["_detail"]
        md += [f"### {title} — announced {d['date']}", "",
               f"Enterprise value **${d['enterprise_value']/1e6:,.0f}M** = equity value ${det['equity_value']/1e6:,.0f}M "
               f"(offer ${d['offer_price']:.2f}/share × {det['diluted_shares']/1e6:.1f}M diluted shares) "
               f"+ net debt ${det['net_debt']/1e6:,.0f}M, all from the target's FY{det['fy'][:4]} 10-K (SEC EDGAR).", "",
               f"LTM revenue ${d['ltm_revenue']/1e6:,.0f}M, LTM EBITDA (EBIT + D&A) ${d['ltm_ebitda']/1e6:,.0f}M, LTM EBIT ${d['ltm_ebit']/1e6:,.0f}M → "
               f"**EV/Revenue {d['enterprise_value']/d['ltm_revenue']:.2f}x, EV/EBITDA {d['enterprise_value']/d['ltm_ebitda']:.2f}x, "
               f"EV/EBIT {d['enterprise_value']/d['ltm_ebit']:.2f}x**.", "",
               f"*Source: {det['source']}.*", ""]
    if out["aks_precedent_detail"]["_detail"].get("clf_close_on_announcement"):
        md.append(f"CLF's own closing price on the AK Steel announcement date was ${out['aks_precedent_detail']['_detail']['clf_close_on_announcement']:.4f} "
                  f"(market_data warehouse; likely a dividend-adjusted figure a few percent below the nominal quote that day). "
                  f"Premiums to AK Steel's own undisturbed price are not shown: AK Steel is delisted and absent from the "
                  f"warehouse, and Yahoo Finance and Stooq both refuse historical data for a fully delisted ticker, so there "
                  f"is no independently verifiable price series to compute a premium against.\n")
    md += ["## 3. DCF (illustrative scenarios built from STLD's own historical range, not analyst consensus)", "",
           f"Discount rate 10.28% for both scenarios (`finmodel wacc examples/wacc_stld.json`); terminal growth 2.5%, perpetuity method. "
           "The low–high range is a small discount-rate (±0.5pt) × terminal-growth (2.0%/2.5%/3.0%) sensitivity grid around each "
           "scenario's central case, standing in for a banker's data table.", ""]
    for key in ("dcf_base", "dcf_blue_sky"):
        d = out[key]; a = d["assumptions"]
        md += [f"**{d['name']}**: revenue grows {a['revenue_growth']*100:.0f}%/yr, EBIT margin reaches {a['ebit_margin_target_year5']*100:.1f}% by year 5 "
               f"(FY2025 was 8.1%) → implied share price **{d['base_value_per_share']:.2f}** (range {d['low']:.2f} – {d['high']:.2f} across the sensitivity grid).", ""]
    md += ["## 4. 52-week trading range (real, market_data warehouse)", ""]
    wk = out["week52"]
    if "low" in wk:
        md.append(f"${wk['low']:.2f} – ${wk['high']:.2f} ({wk['from']} to {wk['to']}, {wk['n_days']} trading days).")
    md += ["", "## Method note", "",
           "Everything here is either a live database query (peer prices, precedent-deal-acquirer's price, 52-week range), "
           "a public SEC filing (every revenue/EBIT/D&A/debt/cash figure), a matter of public record (the two deals' offer "
           "prices and announcement dates), or an explicitly labelled assumption I built (the two DCF scenarios' growth and "
           "margin paths, and the choice of which two precedent deals to include). Nothing here was invented and presented "
           "as fact; where a genuinely real number was unavailable (target-side premiums for delisted companies), it was "
           "omitted rather than approximated.", "",
           "Regenerate with `python scripts/football_field_stld.py`; chart at `out/charts_football_field_stld.html`."]
    return "\n".join(md)


if __name__ == "__main__":
    run()
