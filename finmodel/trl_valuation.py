"""TRL (Technology Readiness Level)-based valuation for a deep-tech / hard-tech startup: how a company should
be valued differently at TRL 5 (component/subsystem validated in a relevant environment) vs. TRL 7 (a system
prototype demonstrated in an actual operational environment), and what it costs to get from one to the other.

TRL is the standard 1-9 technology-maturity scale originated by NASA (Mankins, 1995) and formalized across the
U.S. Department of Defense's acquisition process (the DoD Technology Readiness Assessment (TRA) Guide) -- see
`TRL_DEFINITIONS` below for the nine official stage definitions, reproduced here for reference/CLI display, not
reinterpreted.

Two well-established valuation techniques translate a TRL gap into a $ value gap, applied together as a
cross-check rather than in isolation:

1. Risk-adjusted (probability-weighted) NPV -- the same logic biotech/pharma uses to price a drug candidate by
   its remaining clinical-trial phases (risk-adjust the eventual commercial value by the CUMULATIVE probability
   of reaching commercialization from here), applied instead to TRL-gate technical risk. `risk_adjusted_value()`
   below computes, for any TRL, the present value of the eventual fully-commercial (TRL 9) outcome, discounted
   for both time (years still needed to reach TRL 9) and technical risk (the product of every remaining stage's
   probability of successfully advancing).
2. The VC Method (already implemented in `finmodel.cap_table.vc_method_valuation`) -- working backward from a
   required return, using a stage-appropriate required IRR as a return-based (rather than probability-based)
   way of pricing the same technical risk. `vc_method_cross_check()` reuses it directly as a second opinion on
   the same TRL gap -- real investors sanity-check a probability-based valuation against a return-based one
   exactly this way.

This module does NOT hardcode a "TRL 5 = X% probability of success" table. Checked against how real deep-tech
valuation practice actually handles this (Equidam's published deep-tech/TRL valuation methodology conditions
its discount rate and probability-of-success weighting on TRL, but explicitly as a qualitative per-case
judgment, not one universal fixed table; no other publicly documented template does either) -- there is no
single authoritative number, and fabricating one would be worse than useless for a real money decision. Every
probability, discount rate, and required-IRR figure here is a required input the caller supplies -- from their
own gate-review track record, a named investor's stated required return, or a published empirical study of
TRL-linked program outcomes. The real, oft-cited empirical link this module is built to let a caller express:
a 2005 GAO review of 54 DoD programs found that programs integrating technologies rated below TRL 6-7 averaged
41% cost growth and a 13-month schedule delay, versus far less growth for programs that waited for TRL 7+
(GAO, "Technology Readiness Assessment Guide," GAO-20-48G; Bissing, "An Analysis of the Effects of Technology
Readiness Levels on Cost Growth," AFIT, finds the same TRL/cost-growth relationship in Major Defense Acquisition
Program data) -- real evidence that the TRL 5-to-7 gap specifically is where a large chunk of technical risk
gets priced out, without a single number this module could honestly bake in for every technology and market."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Sequence

from .cap_table import round_math, vc_method_valuation
from .fin import safe_div

TRL_DEFINITIONS: Dict[int, str] = {
    1: "Basic principles observed and reported",
    2: "Technology concept and/or application formulated",
    3: "Analytical and experimental critical function and/or characteristic proof of concept",
    4: "Component and/or breadboard validation in a laboratory environment",
    5: "Component and/or breadboard validation in a relevant environment",
    6: "System/subsystem model or prototype demonstration in a relevant environment",
    7: "System prototype demonstration in an operational environment",
    8: "Actual system completed and qualified through test and demonstration",
    9: "Actual system proven through successful mission/operational use",
}


@dataclass
class TRLStage:
    trl: int
    probability_of_advancing: float | None = None   # P(reach trl+1 | currently at trl); must be None for TRL 9, required otherwise
    years_to_next_stage: float = 0.0                 # 0.0 for TRL 9 (there is no next stage)
    capital_required: float = 0.0                    # $ needed to fund the climb from this TRL to the next; 0.0 for TRL 9
    required_irr: float | None = None                # investor's required annual return for capital deployed AT this stage (VC-Method cross-check only)

    def __post_init__(self) -> None:
        if not (1 <= self.trl <= 9):
            raise ValueError(f"trl must be between 1 and 9, got {self.trl!r}")
        if self.probability_of_advancing is not None and not (0.0 < self.probability_of_advancing <= 1.0):
            raise ValueError(f"TRL {self.trl}: probability_of_advancing must be in (0, 1], got {self.probability_of_advancing!r}")
        if self.years_to_next_stage < 0:
            raise ValueError(f"TRL {self.trl}: years_to_next_stage must be >= 0, got {self.years_to_next_stage!r}")
        if self.capital_required < 0:
            raise ValueError(f"TRL {self.trl}: capital_required must be >= 0, got {self.capital_required!r}")
        if self.required_irr is not None and self.required_irr <= -1.0:
            raise ValueError(f"TRL {self.trl}: required_irr must be > -1, got {self.required_irr!r}")


@dataclass
class TRLValuationInputs:
    commercial_value: float          # NPV/DCF value of the business once fully commercial (TRL 9), in today's $
    discount_rate: float             # time-value discount rate used to PV the commercial value back from each TRL
    stages: Sequence[TRLStage]       # every TRL from the earliest modeled stage through TRL 9 inclusive, no gaps

    def __post_init__(self) -> None:
        if self.commercial_value <= 0:
            raise ValueError(f"commercial_value must be positive, got {self.commercial_value!r}")
        if not (0.0 < self.discount_rate < 3.0):
            raise ValueError(f"discount_rate looks implausible (expected a small positive fraction): {self.discount_rate!r}")
        trls = sorted(s.trl for s in self.stages)
        if len(set(trls)) != len(trls):
            raise ValueError(f"duplicate TRL stages given: {trls}")
        if not trls or trls != list(range(trls[0], 10)):
            raise ValueError(f"stages must run consecutively from some starting TRL through 9 with no gaps, got {trls}")
        terminal = self.by_trl(9)
        if terminal.probability_of_advancing is not None:
            raise ValueError("TRL 9 is the terminal (fully commercial) stage and takes no probability_of_advancing")
        for s in self.stages:
            if s.trl != 9 and s.probability_of_advancing is None:
                raise ValueError(f"TRL {s.trl} needs a probability_of_advancing (every non-terminal stage does)")

    def by_trl(self, trl: int) -> TRLStage:
        for s in self.stages:
            if s.trl == trl:
                return s
        modeled = sorted(s.trl for s in self.stages)
        raise ValueError(f"TRL {trl} is not modeled in this input set (stages span {modeled[0]}-{modeled[-1]})")

    def min_trl(self) -> int:
        return min(s.trl for s in self.stages)


def cumulative_probability_of_success(inputs: TRLValuationInputs, from_trl: int) -> float:
    """Product of every remaining stage's probability_of_advancing, from `from_trl` through TRL 8 -- the chance
    the technology reaches full commercialization (TRL 9) at all, given where it stands today. 1.0 at TRL 9
    itself (an empty product: no technical risk left to price)."""
    p = 1.0
    for trl in range(from_trl, 9):
        p *= inputs.by_trl(trl).probability_of_advancing
    return p


def years_to_commercial(inputs: TRLValuationInputs, from_trl: int) -> float:
    """Sum of years_to_next_stage from `from_trl` through TRL 8 -- how long until TRL 9, on the stated plan."""
    return sum(inputs.by_trl(trl).years_to_next_stage for trl in range(from_trl, 9))


def capital_required_between(inputs: TRLValuationInputs, from_trl: int, to_trl: int) -> float:
    """Total capital needed to fund every stage's climb from `from_trl` up to (not including) `to_trl`."""
    if to_trl <= from_trl:
        raise ValueError(f"to_trl ({to_trl}) must be greater than from_trl ({from_trl})")
    return sum(inputs.by_trl(trl).capital_required for trl in range(from_trl, to_trl))


def risk_adjusted_value(inputs: TRLValuationInputs, at_trl: int) -> Dict[str, Any]:
    """The present value of the eventual TRL-9 commercial outcome, discounted for both time (years still needed)
    and technical risk (cumulative probability of actually getting there) -- what a technology at `at_trl` is
    worth TODAY, before any dilution from the capital needed to fund the remaining climb (see `trl_uplift()`)."""
    p = cumulative_probability_of_success(inputs, at_trl)
    t = years_to_commercial(inputs, at_trl)
    pv = inputs.commercial_value / (1 + inputs.discount_rate) ** t
    return {"trl": at_trl, "cumulative_probability_of_success": p, "years_to_commercial": t,
            "pv_of_commercial_value": pv, "risk_adjusted_value": pv * p}


def trl_uplift(inputs: TRLValuationInputs, from_trl: int, to_trl: int) -> Dict[str, Any]:
    """Compares the risk-adjusted value at two TRL stages -- e.g. TRL 5 vs. TRL 7 -- and nets the resulting
    value uplift against the capital it actually takes to climb there, via `cap_table.round_math()`: raising
    that capital against a TRL-`from_trl` pre-money dilutes existing holders even as the underlying technology
    re-rates higher on both less remaining technical risk and a shorter discounting horizon."""
    if to_trl <= from_trl:
        raise ValueError(f"to_trl ({to_trl}) must be greater than from_trl ({from_trl})")
    v_from = risk_adjusted_value(inputs, from_trl)
    v_to = risk_adjusted_value(inputs, to_trl)
    capital = capital_required_between(inputs, from_trl, to_trl)
    out: Dict[str, Any] = {"from": v_from, "to": v_to, "capital_required_to_advance": capital,
                           "value_uplift": v_to["risk_adjusted_value"] - v_from["risk_adjusted_value"],
                           "value_uplift_multiple": safe_div(v_to["risk_adjusted_value"], v_from["risk_adjusted_value"])}
    if capital > 0:
        out["financing_round_math"] = round_math(pre_money=v_from["risk_adjusted_value"], investment=capital)
    return out


def vc_method_cross_check(inputs: TRLValuationInputs, at_trl: int) -> Dict[str, Any]:
    """A second, return-based opinion on the same TRL gap: instead of discounting the commercial value by an
    explicit probability of success, `cap_table.vc_method_valuation()` prices the same risk into a stage-
    appropriate required IRR (typically much higher pre-TRL-7 than post-, mirroring the well-documented pattern
    that early-stage/hard-tech investors demand steeper returns the further a technology sits from a proven,
    operational demonstration). Needs `required_irr` set on `at_trl` and `capital_required` set on every stage
    between `at_trl` and TRL 9."""
    stage = inputs.by_trl(at_trl)
    if stage.required_irr is None:
        raise ValueError(f"TRL {at_trl} has no required_irr set -- vc_method_cross_check needs one")
    capital = capital_required_between(inputs, at_trl, 9)
    if capital <= 0:
        raise ValueError(f"no capital_required is set for any stage from TRL {at_trl} to 9 -- nothing to size a round against")
    years = years_to_commercial(inputs, at_trl)
    return vc_method_valuation(investment_amount=capital, target_exit_value=inputs.commercial_value,
                               years_to_exit=years, target_irr=stage.required_irr)


def inputs_from_dict(d: Dict[str, Any]) -> TRLValuationInputs:
    stages = [TRLStage(**s) for s in d["stages"]]
    return TRLValuationInputs(commercial_value=d["commercial_value"], discount_rate=d["discount_rate"], stages=stages)


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    inputs = inputs_from_dict(d)
    out: Dict[str, Any] = {}
    if "value_at_trl" in d:
        out["risk_adjusted_value"] = risk_adjusted_value(inputs, d["value_at_trl"])
    if "uplift" in d:
        out["uplift"] = trl_uplift(inputs, d["uplift"]["from_trl"], d["uplift"]["to_trl"])
    if "vc_method_cross_check_trl" in d:
        out["vc_method_cross_check"] = vc_method_cross_check(inputs, d["vc_method_cross_check_trl"])
    return out
