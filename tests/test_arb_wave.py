from decimal import Decimal

import pytest

from arb_wave import (
    fixed_stake_point,
    generate_stake_wave,
    generate_wave,
    payout_from_stake,
    stake_for_payout,
    target_profit_point,
)


def test_wave_target_profit_matches_reference_example():
    rows = generate_wave(
        target_profit=Decimal("100"),
        start_probability=Decimal("0.10"),
        end_probability=Decimal("0.90"),
        increment=Decimal("0.10"),
    )

    assert rows[0].required_stake.quantize(Decimal("0.01")) == Decimal("11.11")
    assert rows[4].required_stake == Decimal("100")
    assert rows[-1].required_stake == Decimal("900")
    assert all(row.profit == Decimal("100") for row in rows)


def test_wave_preserves_both_directions_of_the_relationship():
    payout = payout_from_stake(Decimal("0.60"), Decimal("100"))
    stake = stake_for_payout(Decimal("0.60"), payout)

    assert payout == Decimal("166.6666666666666666666666666667")
    assert stake == Decimal("100.0000000000000000000000000000")


def test_target_profit_rejects_boundary_probabilities():
    with pytest.raises(ValueError):
        target_profit_point(Decimal("0"), Decimal("100"))

    with pytest.raises(ValueError):
        target_profit_point(Decimal("1"), Decimal("100"))


def test_fixed_stake_mode_matches_payout_and_profit_formulas():
    point = fixed_stake_point(Decimal("0.60"), Decimal("100"))

    assert point.required_stake == Decimal("100")
    assert point.total_payout.quantize(Decimal("0.01")) == Decimal("166.67")
    assert point.profit == point.total_payout - point.required_stake
    assert point.profit.quantize(Decimal("0.01")) == Decimal("66.67")


def test_fixed_stake_wave_keeps_stake_constant_across_probabilities():
    rows = generate_stake_wave(
        stake=Decimal("100"),
        start_probability=Decimal("0.10"),
        end_probability=Decimal("0.90"),
        increment=Decimal("0.10"),
    )

    assert all(row.required_stake == Decimal("100") for row in rows)
    assert rows[0].total_payout == Decimal("1000")
    assert rows[-1].profit.quantize(Decimal("0.01")) == Decimal("11.11")


def test_wave_appends_an_inclusive_end_probability():
    rows = generate_wave(
        target_profit=Decimal("100"),
        start_probability=Decimal("0.40"),
        end_probability=Decimal("0.70"),
        increment=Decimal("0.10"),
    )

    assert rows[-1].probability == Decimal("0.70")
