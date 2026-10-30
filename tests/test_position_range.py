from decimal import Decimal

import pytest

from core.position_range import evaluate_position


def test_position_range_uses_fixed_original_stake_and_defined_endpoints():
    result = evaluate_position(
        original_stake=Decimal("78"),
        odds_a=Decimal("2.00"),
        odds_b=Decimal("2.00"),
        range_multiplier=Decimal("2"),
        candidate_points=3,
    )

    assert result.minimum_additional_stake == Decimal("78")
    assert result.maximum_additional_stake == Decimal("156")
    assert result.points[0].additional_stake == Decimal("78")
    assert result.points[-1].additional_stake == Decimal("156")
    assert result.points[0].profit_if_a_wins == Decimal("0")
    assert result.points[0].profit_if_b_wins == Decimal("0")


def test_position_range_calculates_both_outcomes_and_thresholds():
    result = evaluate_position(
        original_stake=Decimal("100"),
        odds_a=Decimal("2.00"),
        odds_b=Decimal("2.50"),
        range_multiplier=Decimal("1"),
        candidate_points=2,
        target_profit_b=Decimal("20"),
    )
    point = result.points[0]

    assert point.additional_stake == Decimal("50")
    assert point.payout_if_b_wins == Decimal("125.0")
    assert point.profit_if_a_wins == Decimal("50")
    assert point.profit_if_b_wins == Decimal("-25.0")
    assert point.break_even_probability == Decimal("1") / Decimal("3")
    assert point.target_probability == Decimal("50") / Decimal("170")


def test_position_range_accounts_for_fees_in_effective_probabilities():
    result = evaluate_position(
        original_stake=Decimal("100"),
        odds_a=Decimal("2.00"),
        odds_b=Decimal("2.50"),
        range_multiplier=Decimal("1"),
        candidate_points=2,
        fee_b=Decimal("0.10"),
    )

    assert result.effective_odds_b == Decimal("2.250")
    assert result.market_probability_b == Decimal("0.4")
    assert result.effective_probability_b == Decimal("0.4444444444444444444444444444")


def test_position_range_applies_spending_limit_without_changing_range():
    result = evaluate_position(
        original_stake=Decimal("100"),
        odds_a=Decimal("2.00"),
        odds_b=Decimal("2.00"),
        range_multiplier=Decimal("2"),
        candidate_points=3,
        spending_limit=Decimal("100"),
    )

    assert len(result.points) == 3
    assert [point.within_spending_limit for point in result.points] == [True, True, False]


def test_position_range_reports_equal_payout_stake_when_inside_range():
    result = evaluate_position(
        original_stake=Decimal("100"),
        odds_a=Decimal("2.00"),
        odds_b=Decimal("2.50"),
        range_multiplier=Decimal("2"),
        candidate_points=5,
    )

    assert result.equal_payout_in_range is True
    assert result.equal_payout_stake == Decimal("80")


def test_position_range_rejects_invalid_candidate_count():
    with pytest.raises(ValueError):
        evaluate_position(100, 2, 2, 2, 1)
