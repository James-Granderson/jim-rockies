"""Position Range analysis for an already-placed side A position.

Hedge Range distributes a new total stake between two sides. Position Range
keeps the original side A stake fixed and evaluates only additional stake H
placed on side B.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

from . import arb_math


ONE = Decimal("1")
ZERO = Decimal("0")


def _decimal(value: Decimal | int | str, label: str) -> Decimal:
    try:
        return value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{label} must be numeric.") from error


def _positive(value: Decimal | int | str, label: str) -> Decimal:
    result = _decimal(value, label)
    if result <= ZERO:
        raise ValueError(f"{label} must be greater than zero.")
    return result


def _nonnegative(value: Decimal | int | str, label: str) -> Decimal:
    result = _decimal(value, label)
    if result < ZERO:
        raise ValueError(f"{label} cannot be negative.")
    return result


def _effective_odds(decimal_odds: Decimal, fee: Decimal) -> Decimal:
    return arb_math.apply_fee_decimal(decimal_odds, fee)


@dataclass(frozen=True)
class PositionPoint:
    """One candidate additional stake in the Position Range."""

    additional_stake: Decimal
    payout_if_b_wins: Decimal
    profit_if_a_wins: Decimal
    profit_if_b_wins: Decimal
    worst_case: Decimal
    best_case: Decimal
    is_arbitrage: bool
    break_even_probability: Decimal
    target_probability: Decimal
    within_spending_limit: bool


@dataclass(frozen=True)
class PositionRangeResult:
    """The complete range and derived recommendations."""

    original_stake: Decimal
    range_multiplier: Decimal
    effective_odds_a: Decimal
    effective_odds_b: Decimal
    market_probability_b: Decimal
    effective_probability_b: Decimal
    minimum_additional_stake: Decimal
    maximum_additional_stake: Decimal
    equal_payout_stake: Optional[Decimal]
    equal_payout_in_range: bool
    recommendation_kind: str
    recommendation: Optional[PositionPoint]
    points: list[PositionPoint]


def _candidate_stakes(
    minimum: Decimal,
    maximum: Decimal,
    candidate_points: int,
) -> list[Decimal]:
    if candidate_points < 2:
        raise ValueError("Candidate points must be at least 2.")
    step = (maximum - minimum) / Decimal(candidate_points - 1)
    return [minimum + (step * index) for index in range(candidate_points)]


def evaluate_position(
    original_stake: Decimal | int | str,
    odds_a: Decimal | int | str,
    odds_b: Decimal | int | str,
    range_multiplier: Decimal | int | str,
    candidate_points: int,
    target_profit_b: Decimal | int | str = ZERO,
    fee_a: Decimal | int | str = ZERO,
    fee_b: Decimal | int | str = ZERO,
    spending_limit: Optional[Decimal | int | str] = None,
) -> PositionRangeResult:
    """Evaluate the fixed-original-stake Position Range."""

    original = _positive(original_stake, "Original stake")
    odds_a_value = _positive(odds_a, "Side A decimal odds")
    odds_b_value = _positive(odds_b, "Side B decimal odds")
    multiplier = _positive(range_multiplier, "Range multiplier")
    target = _nonnegative(target_profit_b, "Target B profit")
    fee_a_value = arb_math.validate_fee_decimal(fee_a)
    fee_b_value = arb_math.validate_fee_decimal(fee_b)
    limit = _nonnegative(spending_limit, "Spending limit") if spending_limit is not None else None

    effective_a = _effective_odds(odds_a_value, fee_a_value)
    effective_b = _effective_odds(odds_b_value, fee_b_value)
    minimum = (multiplier * original) / Decimal("2")
    maximum = multiplier * original
    stakes = _candidate_stakes(minimum, maximum, int(candidate_points))
    points = []
    for additional in stakes:
        payout_b = additional * effective_b
        profit_a = (original * effective_a) - original - additional
        profit_b = payout_b - original - additional
        denominator = original + additional
        target_denominator = denominator + target
        points.append(
            PositionPoint(
                additional_stake=additional,
                payout_if_b_wins=payout_b,
                profit_if_a_wins=profit_a,
                profit_if_b_wins=profit_b,
                worst_case=min(profit_a, profit_b),
                best_case=max(profit_a, profit_b),
                is_arbitrage=profit_a >= ZERO and profit_b >= ZERO,
                break_even_probability=additional / denominator,
                target_probability=additional / target_denominator,
                within_spending_limit=limit is None or additional <= limit,
            )
        )

    equal_payout_stake = (original * effective_a) / effective_b
    equal_payout_in_range = minimum <= equal_payout_stake <= maximum
    eligible = [point for point in points if point.within_spending_limit]
    arbitrage_points = [point for point in eligible if point.is_arbitrage]
    if arbitrage_points:
        recommendation_kind = "arbitrage"
        recommendation = max(arbitrage_points, key=lambda point: (point.worst_case, point.best_case))
    elif eligible:
        recommendation_kind = "hedge"
        recommendation = max(eligible, key=lambda point: (point.worst_case, point.best_case))
    else:
        recommendation_kind = "none_within_spending_limit"
        recommendation = None

    return PositionRangeResult(
        original_stake=original,
        range_multiplier=multiplier,
        effective_odds_a=effective_a,
        effective_odds_b=effective_b,
        market_probability_b=arb_math.implied_probability(odds_b_value),
        effective_probability_b=arb_math.implied_probability(effective_b),
        minimum_additional_stake=minimum,
        maximum_additional_stake=maximum,
        equal_payout_stake=equal_payout_stake if equal_payout_in_range else None,
        equal_payout_in_range=equal_payout_in_range,
        recommendation_kind=recommendation_kind,
        recommendation=recommendation,
        points=points,
    )
