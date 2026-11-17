"""Strategy-consulting frameworks: market sizing (TAM/SAM/SOM) and the two real, named portfolio-classification
matrices McKinsey/BCG/Bain-style engagements use (confirmed via a market survey of MBB's own public materials
and third-party strategy-framework references, not invented here):

  - BCG Growth-Share Matrix (Boston Consulting Group, early 1970s): classifies business units on relative
    market share (share ÷ largest competitor's share) vs market growth rate into Star/Cash Cow/Question Mark/
    Dog. Two simple proxies, by design — the point of the framework is speed and directional portfolio triage.
  - GE-McKinsey Nine-Box Matrix (McKinsey & Company for General Electric, early 1970s): the more nuanced
    successor — weighted multi-factor scores for "industry attractiveness" and "business unit strength" (each
    High/Medium/Low), placed into 9 cells grouped into three real, named zones (Invest/Grow, Selective/Hold,
    Harvest/Divest).
  - TAM/SAM/SOM market sizing (top-down and bottom-up): the standard total/serviceable/obtainable market-size
    decomposition every strategy-consulting market-sizing exercise (and every real startup pitch deck) uses.
  - Porter's Five Forces (Porter, "How Competitive Forces Shape Strategy", HBR 1979): each force rated for
    intensity; the higher the average intensity, the less attractive the industry for incumbents' profits.
  - Weighted decision matrix / multi-criteria analysis (weighted-sum model): options scored on weighted
    criteria, with a check of how much each criterion's weight would have to move before the winner changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .fin import safe_div


# ---------------------------------------------------------------------------------------------------------
# Market sizing (TAM / SAM / SOM)
# ---------------------------------------------------------------------------------------------------------

def market_sizing_top_down(tam: float, sam_pct_of_tam: float, som_pct_of_sam: float) -> Dict[str, Any]:
    """Top-down: start from a known total market figure and narrow it by realistic serviceable/obtainable
    percentages — fast, defensible only as far as the TAM figure and the two percentages are."""
    sam = tam * sam_pct_of_tam
    som = sam * som_pct_of_sam
    return {"method": "top_down", "tam": tam, "sam": sam, "som": som,
            "sam_pct_of_tam": sam_pct_of_tam, "som_pct_of_sam": som_pct_of_sam, "som_pct_of_tam": safe_div(som, tam)}


@dataclass
class CustomerSegment:
    name: str
    customer_count: float
    penetration_pct: float          # share of this segment realistically reachable/obtainable
    annual_price_per_customer: float


def market_sizing_bottom_up(segments: Sequence[CustomerSegment]) -> Dict[str, Any]:
    """Bottom-up: build the market size from real, addressable customer counts and a real price point per
    segment — the more defensible (if more data-hungry) method, since it's grounded in countable units rather
    than a single top-down percentage guess."""
    rows = []
    tam = 0.0; som = 0.0
    for s in segments:
        segment_tam = s.customer_count * s.annual_price_per_customer
        segment_som = segment_tam * s.penetration_pct
        tam += segment_tam; som += segment_som
        rows.append({"segment": s.name, "customer_count": s.customer_count, "annual_price_per_customer": s.annual_price_per_customer,
                    "segment_tam": segment_tam, "penetration_pct": s.penetration_pct, "segment_som": segment_som})
    return {"method": "bottom_up", "segments": rows, "tam": tam, "som": som, "som_pct_of_tam": safe_div(som, tam)}


# ---------------------------------------------------------------------------------------------------------
# BCG Growth-Share Matrix
# ---------------------------------------------------------------------------------------------------------

def bcg_classify(relative_market_share: float, market_growth_rate: float, share_threshold: float = 1.0,
                 growth_threshold: float = 0.10) -> str:
    """Real BCG convention: relative_market_share = this unit's share / the LARGEST competitor's share (so 1.0
    is the boundary between market leader and follower); growth_threshold defaults to 10%, the figure most
    commonly cited for BCG's own original matrix (a modern application should instead use the industry's real
    growth rate or GDP growth as the cutoff — 10% is a starting point, not a universal constant)."""
    high_share = relative_market_share >= share_threshold
    high_growth = market_growth_rate >= growth_threshold
    if high_growth and high_share: return "Star"
    if not high_growth and high_share: return "Cash Cow"
    if high_growth and not high_share: return "Question Mark"
    return "Dog"


def bcg_matrix(business_units: Sequence[Dict[str, Any]], share_threshold: float = 1.0, growth_threshold: float = 0.10) -> Dict[str, Any]:
    """`business_units`: [{"name", "relative_market_share", "market_growth_rate", "revenue" (optional, for the
    portfolio-mix summary)}, ...]."""
    rows = []
    for u in business_units:
        cls = bcg_classify(u["relative_market_share"], u["market_growth_rate"], share_threshold, growth_threshold)
        rows.append({**u, "classification": cls})
    total_revenue = sum(u.get("revenue", 0.0) for u in business_units)
    mix = {}
    if total_revenue:
        for cls in ("Star", "Cash Cow", "Question Mark", "Dog"):
            mix[cls] = safe_div(sum(r.get("revenue", 0.0) for r in rows if r["classification"] == cls), total_revenue)
    return {"units": rows, "share_threshold": share_threshold, "growth_threshold": growth_threshold,
            "revenue_mix_by_classification": mix}


# ---------------------------------------------------------------------------------------------------------
# GE-McKinsey Nine-Box Matrix
# ---------------------------------------------------------------------------------------------------------

ZONES = {
    ("High", "High"): "Invest/Grow", ("High", "Medium"): "Invest/Grow", ("Medium", "High"): "Invest/Grow",
    ("Medium", "Medium"): "Selective/Hold", ("High", "Low"): "Selective/Hold", ("Low", "High"): "Selective/Hold",
    ("Medium", "Low"): "Harvest/Divest", ("Low", "Medium"): "Harvest/Divest", ("Low", "Low"): "Harvest/Divest",
}


def _weighted_score(factors: Dict[str, Tuple[float, float]]) -> float:
    """factors: {name: (score_1_to_5, weight)}. Weights are normalized to sum to 1 (so callers don't have to
    hit an exact 1.0 by hand), then combined into a single 1-5 composite score."""
    total_weight = sum(w for _, w in factors.values())
    if total_weight <= 0:
        raise ValueError("factor weights must sum to a positive number")
    return sum(score * (weight / total_weight) for score, weight in factors.values())


def _bucket(score: float) -> str:
    """Standard tercile split of a 1-5 composite score: Low < 2.33, 2.33 <= Medium < 3.67, High >= 3.67."""
    if score >= 11 / 3:
        return "High"
    if score >= 7 / 3:
        return "Medium"
    return "Low"


def ge_mckinsey_classify(industry_attractiveness_factors: Dict[str, Tuple[float, float]],
                         business_strength_factors: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
    attractiveness_score = _weighted_score(industry_attractiveness_factors)
    strength_score = _weighted_score(business_strength_factors)
    attractiveness_bucket = _bucket(attractiveness_score)
    strength_bucket = _bucket(strength_score)
    zone = ZONES[(strength_bucket, attractiveness_bucket)]
    return {"industry_attractiveness_score": attractiveness_score, "industry_attractiveness_bucket": attractiveness_bucket,
            "business_strength_score": strength_score, "business_strength_bucket": strength_bucket, "zone": zone}


def ge_mckinsey_matrix(business_units: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """`business_units`: [{"name", "industry_attractiveness_factors": {factor: [score, weight]},
    "business_strength_factors": {factor: [score, weight]}}, ...]."""
    rows = []
    for u in business_units:
        cls = ge_mckinsey_classify({k: tuple(v) for k, v in u["industry_attractiveness_factors"].items()},
                                   {k: tuple(v) for k, v in u["business_strength_factors"].items()})
        rows.append({"name": u["name"], **cls})
    return {"units": rows}



# ---------------------------------------------------------------------------------------------------------
# Porter's Five Forces
# ---------------------------------------------------------------------------------------------------------
FIVE_FORCES = ("rivalry", "threat_of_new_entrants", "supplier_power", "buyer_power", "threat_of_substitutes")


def five_forces(ratings: Dict[str, Any], scale_max: float = 5.0) -> Dict[str, Any]:
    """``ratings``: force -> intensity on 1..``scale_max`` (higher = stronger force = worse for incumbents), or
    force -> {sub-factor: rating} (averaged). All five forces are required. Attractiveness is the share of the
    scale left over, 1 - (mean intensity - 1) / (scale_max - 1); the labels (>= 0.6 attractive, <= 0.4
    unattractive) are a convention for reading the score, not part of Porter's framework."""
    missing = [f for f in FIVE_FORCES if f not in ratings]
    if missing:
        raise ValueError(f"missing forces: {missing}")
    scores: Dict[str, float] = {}
    for f in FIVE_FORCES:
        r = ratings[f]
        scores[f] = sum(r.values()) / len(r) if isinstance(r, dict) else float(r)
        if not 1 <= scores[f] <= scale_max:
            raise ValueError(f"{f}: rating {scores[f]} outside 1..{scale_max}")
    mean = sum(scores.values()) / 5
    attract = 1 - (mean - 1) / (scale_max - 1)
    label = "attractive" if attract >= 0.6 else ("unattractive" if attract <= 0.4 else "moderately attractive")
    return {"force_intensity": scores, "mean_intensity": mean, "strongest_force": max(scores, key=scores.get),
            "attractiveness_index": attract, "assessment": label}


# ---------------------------------------------------------------------------------------------------------
# Weighted decision matrix (multi-criteria analysis)
# ---------------------------------------------------------------------------------------------------------
def weighted_decision_matrix(weights: Dict[str, float], scores: Dict[str, Dict[str, float]],
                             lower_is_better: Sequence[str] = ()) -> Dict[str, Any]:
    """``weights``: criterion -> weight (normalised to sum to 1); ``scores``: option -> {criterion: raw value}.
    Raw values are min-max scaled to 0..1 per criterion (inverted for ``lower_is_better`` criteria, e.g. cost).
    ``weight_tipping_points`` gives, per criterion, the smallest absolute change in its weight (others rescaled
    proportionally) that makes a different option win; None if no change within 0..1 does."""
    crit = list(weights)
    wsum = sum(weights.values())
    w = {c: weights[c] / wsum for c in crit}
    norm: Dict[str, Dict[str, float]] = {o: {} for o in scores}
    for c in crit:
        vals = [scores[o][c] for o in scores]
        lo, hi = min(vals), max(vals)
        for o in scores:
            x = 0.5 if hi == lo else (scores[o][c] - lo) / (hi - lo)
            norm[o][c] = 1 - x if c in lower_is_better else x

    def totals(wt: Dict[str, float]) -> Dict[str, float]:
        return {o: sum(wt[c] * norm[o][c] for c in crit) for o in scores}

    base = totals(w)
    ranking = sorted(base, key=base.get, reverse=True)
    winner = ranking[0]
    tipping: Dict[str, Optional[float]] = {}
    for c in crit:
        best = None
        for step in range(1, 1001):
            for sign in (1, -1):
                new_c = w[c] + sign * step / 1000
                if not 0 <= new_c <= 1:
                    continue
                rest = 1 - w[c]
                wt = {k: (new_c if k == c else (w[k] * (1 - new_c) / rest if rest else (1 - new_c) / (len(crit) - 1))) for k in crit}
                t = totals(wt)
                if max(t, key=t.get) != winner:
                    best = sign * step / 1000
                    break
            if best is not None:
                break
        tipping[c] = best
    return {"weights": w, "normalized_scores": norm, "weighted_totals": base, "ranking": ranking, "winner": winner,
            "weight_tipping_points": tipping}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if "market_sizing_top_down" in d:
        out["market_sizing_top_down"] = market_sizing_top_down(**d["market_sizing_top_down"])
    if "market_sizing_bottom_up" in d:
        segs = [CustomerSegment(**s) for s in d["market_sizing_bottom_up"]["segments"]]
        out["market_sizing_bottom_up"] = market_sizing_bottom_up(segs)
    if "bcg_matrix" in d:
        out["bcg_matrix"] = bcg_matrix(**d["bcg_matrix"])
    if "ge_mckinsey_matrix" in d:
        out["ge_mckinsey_matrix"] = ge_mckinsey_matrix(d["ge_mckinsey_matrix"]["business_units"])
    if "five_forces" in d:
        out["five_forces"] = five_forces(**d["five_forces"])
    if "weighted_decision_matrix" in d:
        out["weighted_decision_matrix"] = weighted_decision_matrix(**d["weighted_decision_matrix"])
    return out
