from decimal import Decimal

import pytest
from decimal import Decimal

import arb_math
import hedge_range


def test_american_to_decimal_returns_decimal():
    result = arb_math.american_to_decimal(110)
    assert result == Decimal("2.10")
    assert isinstance(result, Decimal)


def test_multiplier_to_decimal_preserves_input_precision():
    result = arb_math.multiplier_to_decimal("2.52")
    assert result == Decimal("2.52")
    assert isinstance(result, Decimal)


def test_arb_index_uses_decimal_math():
    result = arb_math.arb_index(Decimal("2.5"), Decimal("2.5"))
    assert result == Decimal("0.8")
    assert isinstance(result, Decimal)


def test_invalid_multiplier_is_rejected():
    with pytest.raises(ValueError):
        arb_math.multiplier_to_decimal("1.00")

    with pytest.raises(ValueError):
        arb_math.multiplier_to_decimal("0")


def test_invalid_american_odds_are_rejected():
    with pytest.raises(ValueError):
        arb_math.american_to_decimal(0)

    with pytest.raises(ValueError):
        arb_math.american_to_decimal(50)

    with pytest.raises(ValueError):
        arb_math.american_to_decimal(-50)


def test_invalid_target_profit_is_rejected():
    with pytest.raises(ValueError):
        arb_math.required_odds(Decimal("2.00"), Decimal("100"), Decimal("0"))

    with pytest.raises(ValueError):
        arb_math.required_odds(Decimal("2.00"), Decimal("100"), Decimal("-1"))


def test_zero_stake_is_allowed_for_internal_range_calculations():
    result = arb_math.decimal_payout(0, Decimal("2.5"))
    assert result == Decimal("0")

    result = arb_math.payout(0, 110)
    assert result == Decimal("0")

    with pytest.raises(ValueError):
        arb_math.validate_stake(0)


def test_get_number_returns_decimal_for_range_calculations(monkeypatch):
    inputs = iter(["2.52"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    result = hedge_range.get_number("Enter multiplier: ", mode="multiplier")

    assert result == Decimal("2.52")
    assert isinstance(result, Decimal)
