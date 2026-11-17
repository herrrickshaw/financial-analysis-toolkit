"""SAFE (Simple Agreement for Future Equity) / convertible-note conversion mechanics: the part of "pre-money vs.
post-money valuation" that trips up even experienced operators, because a valuation cap means something
different depending on which SAFE vintage it's written against.

Legacy (pre-money) SAFE / most non-YC convertible notes: the valuation cap sets a cap on the PRE-money
valuation of the priced round the note converts into -- i.e. a cap on the company's value BEFORE that round's
new money AND before any other outstanding notes get counted. Stack several of these at different caps and each
one's true conversion shares depend on every OTHER note issued later, so nobody -- not the founders, not the
new priced-round investor -- can know their real ownership % until the last note is signed. This was the exact
defect Y Combinator's 2018 post-money SAFE was built to fix (Y Combinator, "Safe Financing Documents" / "Post-
Money Safe: Introduction"; Kirsty Nathoo's SAFE primer).

Post-money SAFE (YC's current standard template): the valuation cap sets a cap on the company's valuation AFTER
all SAFEs (and only the SAFEs) are counted, but BEFORE the new priced round's own money and before any bump to
the option pool bundled into that round. A holder's ownership is then knowable the day they sign: investment /
valuation_cap, full stop -- stacking more SAFEs dilutes only the earlier SAFEs and the founders, never the
percentage a given post-money SAFE was sold at.

Both vintages also commonly carry a discount rate off the eventual priced round's per-share price; a note
converts at whichever of {cap price, discount price} is lower (more shares for the holder) -- never both, and
never automatically the cap (a common modeling mistake, same family as cap_table.py's non-participating-
preferred conversion decision).

The one thing that makes conversion a genuine simultaneous-equation problem rather than row-by-row arithmetic:
a capped note's conversion price depends on a "company capitalization" figure that itself includes every OTHER
converting note's shares. `convert_safes()` solves this with the same closed-form fraction technique this
repo's `cap_table._option_pool_topup()` already uses for the pure all-capped case, wrapped in a small, bounded,
convergence-checked fixed-point loop to handle a realistic mix of capped and discount-only notes (a note's
winning regime -- cap or discount -- can flip once the circular share count is known, which can in turn change
which notes are "capped" for the next pass)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .cap_table import Holder
from .fin import safe_div


@dataclass
class SAFE:
    name: str
    investment: float
    valuation_cap: Optional[float] = None
    discount_rate: Optional[float] = None      # e.g. 0.20 for a 20% discount to the priced round's price/share
    investor_name: str = ""

    def __post_init__(self) -> None:
        if self.valuation_cap is None and self.discount_rate is None:
            raise ValueError(f"SAFE {self.name!r} needs a valuation_cap and/or a discount_rate")
        if self.investment <= 0:
            raise ValueError(f"SAFE {self.name!r}: investment must be positive, got {self.investment!r}")
        if self.valuation_cap is not None and self.valuation_cap <= 0:
            raise ValueError(f"SAFE {self.name!r}: valuation_cap must be positive, got {self.valuation_cap!r}")
        if self.discount_rate is not None and not (0.0 < self.discount_rate < 1.0):
            raise ValueError(f"SAFE {self.name!r}: discount_rate must be between 0 and 1, got {self.discount_rate!r}")


def convert_safes(safes: Sequence[SAFE], pre_safe_fully_diluted_shares: float, round_price_per_share: float,
                  max_iterations: int = 100, tolerance: float = 1e-9) -> Dict[str, Any]:
    """Converts a batch of SAFEs/notes that all convert together into the same priced round. `round_price_per_
    share` is the round's own negotiated price per share (as in `cap_table.Round`, this is taken as already
    agreed -- e.g. pre_money / fully-diluted-shares-immediately-prior-to-the-round -- not itself re-solved here).
    `pre_safe_fully_diluted_shares` is the company's fully-diluted share count BEFORE any of these SAFEs convert
    (founders + existing preferred + existing option pool; NOT including the new round or a pool top-up for it).

    Returns each SAFE's winning conversion price/regime/shares plus the post-conversion fully-diluted share
    count -- ready to feed into `cap_table.simulate_rounds()`'s `initial_holders` (via `to_holders()`) alongside
    the priced round itself."""
    if pre_safe_fully_diluted_shares <= 0:
        raise ValueError(f"pre_safe_fully_diluted_shares must be positive, got {pre_safe_fully_diluted_shares!r}")
    if round_price_per_share <= 0:
        raise ValueError(f"round_price_per_share must be positive, got {round_price_per_share!r}")
    names = [s.name for s in safes]
    if len(set(names)) != len(names):
        raise ValueError(f"SAFE names must be unique, got {names}")
    if not safes:
        return {"safes": [], "total_shares_issued": 0.0, "pre_safe_fully_diluted_shares": pre_safe_fully_diluted_shares,
                "post_conversion_fully_diluted_shares": pre_safe_fully_diluted_shares}

    n0 = pre_safe_fully_diluted_shares

    def discount_price(s: SAFE) -> Optional[float]:
        return round_price_per_share * (1 - s.discount_rate) if s.discount_rate is not None else None

    # start every note that HAS a discount on its discount price (never circular: depends only on the given
    # round price) so the first regime-consistency check below has something real to compare a cap price against.
    regime: Dict[str, str] = {}
    shares: Dict[str, float] = {}
    for s in safes:
        if s.discount_rate is not None:
            regime[s.name] = "discount"
            shares[s.name] = safe_div(s.investment, discount_price(s))
        else:
            regime[s.name] = "cap"
            shares[s.name] = 0.0

    converged = False
    for _ in range(max_iterations):
        cap_notes = [s for s in safes if regime[s.name] == "cap"]
        discount_shares_fixed = sum(shares[s.name] for s in safes if regime[s.name] == "discount")
        if cap_notes:
            k = sum(safe_div(s.investment, s.valuation_cap) for s in cap_notes)
            if k >= 1:
                raise ValueError("combined SAFE valuation caps are infeasible against this pre-SAFE share count "
                                 f"(implied cap-only ownership fraction k={k:.6f} >= 1) -- the caps alone would "
                                 "give the SAFEs 100% or more of the company")
            n_total = (n0 + discount_shares_fixed) / (1 - k)
            for s in cap_notes:
                shares[s.name] = s.investment * n_total / s.valuation_cap

        # data-consistency re-check: with the current share counts, does every note actually still prefer the
        # regime it's assigned to? Re-derive each note's cap price against the CURRENT total and flip regime if
        # the other option is now strictly cheaper (more shares) -- never leave a note priced worse than its own
        # documents allow.
        current_total = n0 + sum(shares.values())
        changed = False
        for s in safes:
            cap_p = safe_div(s.valuation_cap, current_total) if s.valuation_cap is not None else None
            disc_p = discount_price(s)
            candidates = [p for p in (cap_p, disc_p) if p is not None]
            best_regime = "cap" if cap_p is not None and cap_p == min(candidates) else "discount"
            if best_regime != regime[s.name]:
                regime[s.name] = best_regime
                if best_regime == "discount":
                    shares[s.name] = safe_div(s.investment, disc_p)
                changed = True
        if not changed:
            converged = True
            break
    if not converged:
        raise RuntimeError(f"SAFE conversion regime assignment did not converge within {max_iterations} "
                           "iterations -- check for a pathological / degenerate mix of caps and discounts")

    post_total = n0 + sum(shares.values())
    per_safe: List[Dict[str, Any]] = []
    for s in safes:
        sh = shares[s.name]
        price = safe_div(s.investment, sh)
        # data-consistency check: the winning price must not exceed either price this note actually qualifies
        # for (a note is never worse off than either of its own terms) -- guards against a solver regression.
        for p in (safe_div(s.valuation_cap, post_total) if s.valuation_cap is not None else None, discount_price(s)):
            if p is not None:
                assert price <= p + 1e-6, f"SAFE {s.name!r} converted at {price:.6f}, worse than an available price {p:.6f}"
        per_safe.append({"name": s.name, "investor_name": s.investor_name or f"{s.name} investor",
                         "investment": s.investment, "regime": regime[s.name], "conversion_price": price,
                         "shares": sh, "ownership_pct_of_post_conversion_cap_table": safe_div(sh, post_total)})
    total_issued = sum(shares.values())
    assert abs((n0 + total_issued) - post_total) < 1e-6  # footing check
    return {"safes": per_safe, "total_shares_issued": total_issued,
            "pre_safe_fully_diluted_shares": n0, "post_conversion_fully_diluted_shares": post_total}


def to_holders(conversion: Dict[str, Any], security: str = "preferred", round_name: str = "SAFE",
              liquidation_preference_multiple: float = 1.0, participating: bool = False,
              seniority: int = 0) -> List[Holder]:
    """Turns `convert_safes()`'s output into `cap_table.Holder` objects -- typically fed into `initial_holders`
    for a subsequent `cap_table.simulate_rounds()` call covering the priced round the SAFEs just converted into,
    so the round's own option-pool shuffle and exit waterfall see the converted SAFE holders like any other
    pre-existing shareholder."""
    return [Holder(name=s["investor_name"], shares=s["shares"], security=security, round_name=round_name,
                   invested=s["investment"], liquidation_preference_multiple=liquidation_preference_multiple,
                   participating=participating, seniority=seniority) for s in conversion["safes"]]


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    safes = [SAFE(**s) for s in d["safes"]]
    conversion = convert_safes(safes, d["pre_safe_fully_diluted_shares"], d["round_price_per_share"],
                               **{k: v for k, v in d.items() if k in ("max_iterations", "tolerance")})
    out: Dict[str, Any] = {"conversion": conversion}
    if "cap_table_round" in d:
        from . import cap_table as CT
        holder_kwargs = d["cap_table_round"].get("safe_holder_terms", {})
        holders = to_holders(conversion, **holder_kwargs)
        holders.extend(CT.Holder(**h) for h in d["cap_table_round"].get("other_initial_holders", []))
        rounds = [CT.Round(**r) for r in d["cap_table_round"]["rounds"]]
        result = CT.simulate_rounds(holders, rounds)
        out["cap_table"] = result.to_dict()
        if "exit_proceeds" in d["cap_table_round"]:
            out["exit_waterfall"] = CT.exit_waterfall(result, d["cap_table_round"]["exit_proceeds"])
    return out
