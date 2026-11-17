"""finmodel.safe_notes: hand-verified against the post-money SAFE's defining invariant (a SAFE's ownership % of
the SAFE-only post-conversion cap table must equal investment/valuation_cap exactly, independent of how many
OTHER SAFEs stack alongside it -- that's the entire point YC's 2018 post-money SAFE redesign), plus the cap-vs-
discount "whichever price is lower wins" rule and a few input-validation / data-consistency checks."""
import pytest

from finmodel import cap_table as CT
from finmodel import safe_notes as SN


def test_single_capped_safe_ownership_matches_investment_over_cap():
    conversion = SN.convert_safes([SN.SAFE("Seed", investment=1_000_000, valuation_cap=5_000_000)],
                                  pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)
    safe = conversion["safes"][0]
    assert safe["regime"] == "cap"
    assert safe["ownership_pct_of_post_conversion_cap_table"] == pytest.approx(0.20, abs=1e-9)
    assert conversion["post_conversion_fully_diluted_shares"] == pytest.approx(10_000_000)


def test_stacked_capped_safes_each_keep_their_own_intended_ownership():
    # the defining post-money SAFE property: SAFE A's cap implies 20% ownership, SAFE B's implies 5% -- and
    # BOTH must land exactly on those figures despite converting together, because post-money SAFEs dilute
    # only each other and the founders, never each note's own promised ownership percentage.
    safes = [SN.SAFE("A", investment=1_000_000, valuation_cap=5_000_000),
             SN.SAFE("B", investment=500_000, valuation_cap=10_000_000)]
    conversion = SN.convert_safes(safes, pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)
    by_name = {s["name"]: s for s in conversion["safes"]}
    assert by_name["A"]["ownership_pct_of_post_conversion_cap_table"] == pytest.approx(0.20, abs=1e-9)
    assert by_name["B"]["ownership_pct_of_post_conversion_cap_table"] == pytest.approx(0.05, abs=1e-9)
    total_issued = conversion["total_shares_issued"]
    assert 8_000_000 + total_issued == pytest.approx(conversion["post_conversion_fully_diluted_shares"])


def test_discount_only_safe_ignores_the_circular_cap_solver():
    conversion = SN.convert_safes([SN.SAFE("Bridge", investment=500_000, discount_rate=0.20)],
                                  pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)
    safe = conversion["safes"][0]
    assert safe["regime"] == "discount"
    assert safe["conversion_price"] == pytest.approx(0.80)
    assert safe["shares"] == pytest.approx(500_000 / 0.80)


def test_cap_wins_when_it_gives_a_lower_price_than_the_discount():
    conversion = SN.convert_safes([SN.SAFE("Note", investment=1_000_000, valuation_cap=5_000_000, discount_rate=0.10)],
                                  pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)
    safe = conversion["safes"][0]
    assert safe["regime"] == "cap"
    assert safe["conversion_price"] == pytest.approx(0.5)
    assert safe["shares"] == pytest.approx(2_000_000)


def test_discount_wins_when_the_cap_is_too_generous_to_bind():
    conversion = SN.convert_safes([SN.SAFE("Note", investment=1_000_000, valuation_cap=20_000_000, discount_rate=0.10)],
                                  pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)
    safe = conversion["safes"][0]
    assert safe["regime"] == "discount"
    assert safe["conversion_price"] == pytest.approx(0.90)


def test_infeasible_combined_caps_raise():
    safes = [SN.SAFE("A", investment=5_000_000, valuation_cap=1_000_000),
             SN.SAFE("B", investment=5_000_000, valuation_cap=1_000_000)]
    with pytest.raises(ValueError, match="infeasible"):
        SN.convert_safes(safes, pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)


def test_safe_requires_a_cap_or_a_discount():
    with pytest.raises(ValueError, match="needs a valuation_cap"):
        SN.SAFE("Empty", investment=100_000)


def test_duplicate_safe_names_rejected():
    safes = [SN.SAFE("A", investment=100_000, valuation_cap=1_000_000),
             SN.SAFE("A", investment=200_000, valuation_cap=2_000_000)]
    with pytest.raises(ValueError, match="unique"):
        SN.convert_safes(safes, pre_safe_fully_diluted_shares=1_000_000, round_price_per_share=1.0)


def test_to_holders_feeds_directly_into_cap_table_simulate_rounds():
    safes = [SN.SAFE("Seed", investment=1_000_000, valuation_cap=5_000_000, investor_name="Seed investor")]
    conversion = SN.convert_safes(safes, pre_safe_fully_diluted_shares=8_000_000, round_price_per_share=1.0)
    safe_holders = SN.to_holders(conversion)
    assert safe_holders[0].name == "Seed investor"
    assert safe_holders[0].shares == pytest.approx(2_000_000)

    founders = [CT.Holder("Founders", 8_000_000)]
    rounds = [CT.Round("Series A", pre_money=10_000_000, investment=3_000_000, investor_name="Series A investor")]
    result = CT.simulate_rounds(founders + safe_holders, rounds)
    ownership = result.ownership()
    assert ownership["Seed investor"] == pytest.approx(2_000_000 / 13_000_000)
    assert sum(ownership.values()) == pytest.approx(1.0)


def test_from_dict_end_to_end_with_cap_table_round():
    out = SN.from_dict({
        "safes": [{"name": "Seed", "investment": 1_000_000, "valuation_cap": 5_000_000, "investor_name": "Seed investor"}],
        "pre_safe_fully_diluted_shares": 8_000_000,
        "round_price_per_share": 1.0,
        "cap_table_round": {
            "other_initial_holders": [{"name": "Founders", "shares": 8_000_000}],
            "rounds": [{"name": "Series A", "pre_money": 10_000_000, "investment": 3_000_000, "investor_name": "Series A investor"}],
            "exit_proceeds": 20_000_000,
        },
    })
    assert out["conversion"]["safes"][0]["ownership_pct_of_post_conversion_cap_table"] == pytest.approx(0.20, abs=1e-9)
    assert sum(out["cap_table"]["ownership"].values()) == pytest.approx(1.0)
    assert sum(out["exit_waterfall"]["payouts"].values()) == pytest.approx(20_000_000)


def test_round_math_solves_the_missing_figure():
    out = CT.round_math(pre_money=8_000_000, investment=2_000_000)
    assert out["post_money"] == pytest.approx(10_000_000)
    assert out["new_investor_ownership_pct"] == pytest.approx(0.20)

    out2 = CT.round_math(post_money=10_000_000, investment=2_000_000)
    assert out2["pre_money"] == pytest.approx(8_000_000)

    out3 = CT.round_math(pre_money=8_000_000, post_money=10_000_000)
    assert out3["investment"] == pytest.approx(2_000_000)


def test_round_math_rejects_wrong_number_of_inputs():
    with pytest.raises(ValueError, match="exactly two"):
        CT.round_math(pre_money=1.0)
    with pytest.raises(ValueError, match="exactly two"):
        CT.round_math(pre_money=1.0, post_money=2.0, investment=1.0)


def test_round_math_rejects_inconsistent_inputs():
    with pytest.raises(ValueError, match="negative"):
        CT.round_math(pre_money=10_000_000, post_money=5_000_000)


def test_from_dict_handles_round_math_alone():
    out = CT.from_dict({"round_math": {"pre_money": 8_000_000, "investment": 2_000_000}})
    assert out["round_math"]["post_money"] == pytest.approx(10_000_000)
    assert "cap_table" not in out
