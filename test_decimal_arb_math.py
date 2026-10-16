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


def test_vig_adjusts_decimal_odds_and_hedge_stake():
    adjusted = arb_math.apply_vig(Decimal("2.00"))
    assert adjusted == Decimal("1.90")

    result = arb_math.hedge_stake(Decimal("100"), Decimal("2.00"), Decimal("1.90"))
    assert result == Decimal("105.2631578947368421052631579")


def test_probabilities_in_range_for_hedge_refs():
    values = arb_math.hedge_stake_range(Decimal("100"), Decimal("2.00"), Decimal("1.90"), spread=Decimal("0.05"), step=Decimal("0.01"))
    assert len(values) >= 2
    assert values[0]["odds_b"] <= Decimal("1.90")
    assert values[-1]["odds_b"] >= Decimal("1.90")


def test_required_hedge_odds_matches_profit_target_formula():
    required = arb_math.required_hedge_odds(Decimal("100"), Decimal("2.22"), Decimal("1"))
    assert required > Decimal("1.80")
    assert required < Decimal("1.90")


def test_normalize_side_and_market_data_are_defensive():
    side_a = arb_math.normalize_side(stake=Decimal("100"), odds=Decimal("2.22"))
    assert side_a["stake"] == Decimal("100")
    assert side_a["odds"] == Decimal("2.22")
    assert side_a["payout"] == Decimal("222")

    side_b = arb_math.normalize_side(stake=Decimal("100"), payout=Decimal("180"))
    assert side_b["odds"] == Decimal("1.80")
    assert side_b["payout"] == Decimal("180")

    market = arb_math.normalize_market(
        stake_a=Decimal("100"),
        odds_a=Decimal("2.22"),
        stake_b=Decimal("100"),
        payout_b=Decimal("180"),
    )
    assert market["odds_b"] == Decimal("1.80")
    assert market["vig_factor"] == Decimal("0.05")


def test_mvp_calc_layer_uses_decimal_math():
    normalized = arb_math.normalize_odds("3.00")
    assert normalized["decimal_odds"] == Decimal("3.00")
    assert normalized["implied_probability_pct"] == Decimal("33.33")

    gross_revenue_target = (Decimal("30.00") * normalized["decimal_odds"]).quantize(Decimal("0.01"))
    assert gross_revenue_target == Decimal("90.00")
    assert isinstance(gross_revenue_target, Decimal)


def test_make_arbitrage_screen_uses_95_percent_landmark_and_10pct_window():
    rows = arb_math.make_arbitrage(
        prob_a=Decimal("0.40"),
        stake=Decimal("30.00"),
        odds_a=Decimal("3.00"),
        start_prob_b=Decimal("0.80"),
        end_prob_b=Decimal("0.10"),
        step=Decimal("0.01"),
    )
    assert rows
    assert rows[0]["target_wall"] == Decimal("0.55")
    assert all(row["prob_b"] <= Decimal("0.55") for row in rows)
    assert all(row["prob_b"] >= Decimal("0.45") for row in rows)
    assert all(row["fixed_profit_target"] == Decimal("30.00") for row in rows)


def test_reach_window_enforces_hard_cap_and_10pct_band():
    prob_a = Decimal("0.40")
    wall = arb_math.target_prob_b(prob_a)
    assert wall == Decimal("0.55")
    assert arb_math.is_loss_bound(prob_a, Decimal("0.60")) is True
    assert arb_math.is_valid_prob_b_window(prob_a, Decimal("0.55")) is True
    assert arb_math.is_valid_prob_b_window(prob_a, Decimal("0.45")) is True
    assert arb_math.is_valid_prob_b_window(prob_a, Decimal("0.60")) is False


def test_make_arbitrage_scan_filters_to_actionable_zone():
    rows = arb_math.scan_probability_field(
        prob_a=Decimal("0.40"),
        stake=Decimal("30.00"),
        odds_a=Decimal("3.00"),
        start_prob_b=Decimal("0.80"),
        end_prob_b=Decimal("0.10"),
        step=Decimal("0.01"),
    )
    assert rows
    assert all(row["prob_b"] <= Decimal("0.55") for row in rows)
    assert all(row["prob_b"] >= Decimal("0.45") for row in rows)
