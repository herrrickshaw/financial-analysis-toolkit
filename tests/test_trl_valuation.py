"""finmodel.trl_valuation: hand-computed against an independent calculation (not just a restatement of the
implementation) for the core risk-adjusted-value chain, plus the module's defining invariants -- TRL 9 carries
zero technical risk and zero remaining discounting, cumulative probability is a strict product over ONLY the
remaining stages (not stages already passed), and the TRL5->TRL7 uplift feeds straight into cap_table's own
tested round_math() -- and a full set of input-validation / data-consistency checks."""
import pytest

from finmodel import cap_table as CT
from finmodel import trl_valuation as TRL


def _stages():
    return [
        TRL.TRLStage(trl=5, probability_of_advancing=0.6, years_to_next_stage=1.0, capital_required=2_000_000, required_irr=0.60),
        TRL.TRLStage(trl=6, probability_of_advancing=0.7, years_to_next_stage=1.0, capital_required=3_000_000, required_irr=0.50),
        TRL.TRLStage(trl=7, probability_of_advancing=0.8, years_to_next_stage=1.0, capital_required=5_000_000, required_irr=0.40),
        TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0, capital_required=8_000_000, required_irr=0.30),
        TRL.TRLStage(trl=9),
    ]


def _inputs():
    return TRL.TRLValuationInputs(commercial_value=500_000_000, discount_rate=0.12, stages=_stages())


def test_trl_definitions_cover_all_nine_levels():
    assert set(TRL.TRL_DEFINITIONS) == set(range(1, 10))
    assert TRL.TRL_DEFINITIONS[5] == "Component and/or breadboard validation in a relevant environment"
    assert TRL.TRL_DEFINITIONS[7] == "System prototype demonstration in an operational environment"


def test_terminal_trl9_has_no_risk_and_no_discounting():
    inputs = _inputs()
    assert TRL.cumulative_probability_of_success(inputs, 9) == 1.0
    assert TRL.years_to_commercial(inputs, 9) == 0.0
    v9 = TRL.risk_adjusted_value(inputs, 9)
    assert v9["risk_adjusted_value"] == pytest.approx(inputs.commercial_value)


def test_cumulative_probability_only_multiplies_remaining_stages():
    inputs = _inputs()
    # from TRL 7: only TRL 7's and TRL 8's probabilities count, NOT TRL 5's or TRL 6's (already passed)
    assert TRL.cumulative_probability_of_success(inputs, 7) == pytest.approx(0.8 * 0.9)
    assert TRL.cumulative_probability_of_success(inputs, 5) == pytest.approx(0.6 * 0.7 * 0.8 * 0.9)


def test_risk_adjusted_value_matches_independent_hand_calculation():
    inputs = _inputs()
    v5 = TRL.risk_adjusted_value(inputs, 5)
    assert v5["cumulative_probability_of_success"] == pytest.approx(0.3024)
    assert v5["years_to_commercial"] == pytest.approx(4.0)
    assert v5["risk_adjusted_value"] == pytest.approx(96_090_333.45, rel=1e-6)

    v7 = TRL.risk_adjusted_value(inputs, 7)
    assert v7["cumulative_probability_of_success"] == pytest.approx(0.72)
    assert v7["years_to_commercial"] == pytest.approx(2.0)
    assert v7["risk_adjusted_value"] == pytest.approx(286_989_795.92, rel=1e-6)


def test_trl_uplift_from_5_to_7_matches_hand_calculation_and_feeds_round_math():
    inputs = _inputs()
    out = TRL.trl_uplift(inputs, 5, 7)
    assert out["value_uplift"] == pytest.approx(190_899_462.46, rel=1e-6)
    assert out["value_uplift_multiple"] == pytest.approx(2.9866666667, rel=1e-6)
    assert out["capital_required_to_advance"] == pytest.approx(2_000_000 + 3_000_000)  # TRL5's and TRL6's capital only

    rm = out["financing_round_math"]
    expected = CT.round_math(pre_money=out["from"]["risk_adjusted_value"], investment=out["capital_required_to_advance"])
    assert rm == pytest.approx(expected)


def test_trl_uplift_requires_to_after_from():
    with pytest.raises(ValueError, match="greater than"):
        TRL.trl_uplift(_inputs(), 7, 5)
    with pytest.raises(ValueError, match="greater than"):
        TRL.trl_uplift(_inputs(), 5, 5)


def test_trl_uplift_omits_financing_round_math_when_no_capital_is_needed():
    stages = [TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0, capital_required=0.0),
              TRL.TRLStage(trl=9)]
    inputs = TRL.TRLValuationInputs(commercial_value=100_000_000, discount_rate=0.10, stages=stages)
    out = TRL.trl_uplift(inputs, 8, 9)
    assert out["capital_required_to_advance"] == 0.0
    assert "financing_round_math" not in out


def test_vc_method_cross_check_matches_cap_table_directly():
    inputs = _inputs()
    out = TRL.vc_method_cross_check(inputs, 5)
    capital = TRL.capital_required_between(inputs, 5, 9)
    years = TRL.years_to_commercial(inputs, 5)
    expected = CT.vc_method_valuation(investment_amount=capital, target_exit_value=inputs.commercial_value,
                                      years_to_exit=years, target_irr=0.60)
    assert out == pytest.approx(expected)


def test_vc_method_cross_check_requires_required_irr():
    stages = [TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0, capital_required=1_000_000),
              TRL.TRLStage(trl=9)]
    inputs = TRL.TRLValuationInputs(commercial_value=100_000_000, discount_rate=0.10, stages=stages)
    with pytest.raises(ValueError, match="required_irr"):
        TRL.vc_method_cross_check(inputs, 8)


def test_vc_method_cross_check_requires_capital():
    stages = [TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0, required_irr=0.30),
              TRL.TRLStage(trl=9)]
    inputs = TRL.TRLValuationInputs(commercial_value=100_000_000, discount_rate=0.10, stages=stages)
    with pytest.raises(ValueError, match="capital_required"):
        TRL.vc_method_cross_check(inputs, 8)


def test_trl_out_of_range_rejected():
    with pytest.raises(ValueError, match="between 1 and 9"):
        TRL.TRLStage(trl=10, probability_of_advancing=0.5)


def test_probability_out_of_range_rejected():
    with pytest.raises(ValueError, match="probability_of_advancing"):
        TRL.TRLStage(trl=5, probability_of_advancing=1.5)
    with pytest.raises(ValueError, match="probability_of_advancing"):
        TRL.TRLStage(trl=5, probability_of_advancing=0.0)


def test_terminal_trl9_rejects_a_probability():
    stages = [TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0),
              TRL.TRLStage(trl=9, probability_of_advancing=0.5)]
    with pytest.raises(ValueError, match="terminal"):
        TRL.TRLValuationInputs(commercial_value=1.0, discount_rate=0.1, stages=stages)


def test_non_terminal_stage_requires_a_probability():
    stages = [TRL.TRLStage(trl=8, years_to_next_stage=1.0), TRL.TRLStage(trl=9)]
    with pytest.raises(ValueError, match="needs a probability_of_advancing"):
        TRL.TRLValuationInputs(commercial_value=1.0, discount_rate=0.1, stages=stages)


def test_gaps_in_trl_sequence_rejected():
    stages = [TRL.TRLStage(trl=5, probability_of_advancing=0.5, years_to_next_stage=1.0), TRL.TRLStage(trl=9)]
    with pytest.raises(ValueError, match="no gaps"):
        TRL.TRLValuationInputs(commercial_value=1.0, discount_rate=0.1, stages=stages)


def test_duplicate_trl_rejected():
    stages = [TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0),
              TRL.TRLStage(trl=8, probability_of_advancing=0.8, years_to_next_stage=1.0), TRL.TRLStage(trl=9)]
    with pytest.raises(ValueError, match="duplicate"):
        TRL.TRLValuationInputs(commercial_value=1.0, discount_rate=0.1, stages=stages)


def test_by_trl_missing_stage_raises():
    inputs = TRL.TRLValuationInputs(commercial_value=1.0, discount_rate=0.1,
                                    stages=[TRL.TRLStage(trl=8, probability_of_advancing=0.9, years_to_next_stage=1.0), TRL.TRLStage(trl=9)])
    with pytest.raises(ValueError, match="not modeled"):
        inputs.by_trl(5)


def test_implausible_discount_rate_rejected():
    with pytest.raises(ValueError, match="discount_rate"):
        TRL.TRLValuationInputs(commercial_value=1.0, discount_rate=5.0, stages=[TRL.TRLStage(trl=9)])


def test_from_dict_end_to_end():
    out = TRL.from_dict({
        "commercial_value": 500_000_000, "discount_rate": 0.12,
        "stages": [
            {"trl": 5, "probability_of_advancing": 0.6, "years_to_next_stage": 1.0, "capital_required": 2_000_000, "required_irr": 0.60},
            {"trl": 6, "probability_of_advancing": 0.7, "years_to_next_stage": 1.0, "capital_required": 3_000_000, "required_irr": 0.50},
            {"trl": 7, "probability_of_advancing": 0.8, "years_to_next_stage": 1.0, "capital_required": 5_000_000, "required_irr": 0.40},
            {"trl": 8, "probability_of_advancing": 0.9, "years_to_next_stage": 1.0, "capital_required": 8_000_000, "required_irr": 0.30},
            {"trl": 9},
        ],
        "value_at_trl": 5,
        "uplift": {"from_trl": 5, "to_trl": 7},
        "vc_method_cross_check_trl": 5,
    })
    assert out["risk_adjusted_value"]["risk_adjusted_value"] == pytest.approx(96_090_333.45, rel=1e-6)
    assert out["uplift"]["value_uplift"] == pytest.approx(190_899_462.46, rel=1e-6)
    assert out["vc_method_cross_check"]["implied_pre_money_valuation"] > 0
