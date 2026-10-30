"""Probability, payout, and stake relationships for the Jim Rockies Wave.

Wave is a single-side economic model. It does not determine whether two
opposing prices create arbitrage. Given a probability, it converts between
stake and payout, or sweeps a probability range to show the stake required to
reach a fixed net-profit target.

All public calculations use ``Decimal`` values. Probabilities are represented
as decimals between zero and one (for example, ``Decimal("0.60")`` is 60%).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable


CENT = Decimal("0.01")
ONE = Decimal("1")
DEFAULT_START = Decimal("0.01")
DEFAULT_END = Decimal("0.99")
DEFAULT_INCREMENT = Decimal("0.01")
DEFAULT_TARGET_PROFIT = Decimal("100")
DEFAULT_STAKE = Decimal("100")


def _decimal(value: Decimal | int | str, label: str) -> Decimal:
    """Convert a public numeric input without introducing float rounding."""

    try:
        return value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{label} must be a valid decimal value.") from error


def validate_probability(probability: Decimal | int | str) -> Decimal:
    """Return a probability strictly inside the binary payout interval."""

    value = _decimal(probability, "Probability")
    if not (Decimal("0") < value < ONE):
        raise ValueError("Probability must be greater than 0 and less than 1.")
    return value


def validate_positive(value: Decimal | int | str, label: str) -> Decimal:
    """Return a positive Decimal for money and range inputs."""

    result = _decimal(value, label)
    if result <= 0:
        raise ValueError(f"{label} must be greater than 0.")
    return result


def payout_from_stake(
    probability: Decimal | int | str,
    stake: Decimal | int | str,
) -> Decimal:
    """Calculate total payout from probability and stake.

    ``Payout = Stake / Probability``.
    """

    probability_value = validate_probability(probability)
    stake_value = validate_positive(stake, "Stake")
    return stake_value / probability_value


def stake_for_payout(
    probability: Decimal | int | str,
    payout: Decimal | int | str,
) -> Decimal:
    """Calculate the required stake for a desired total payout.

    ``Stake = Payout * Probability``.
    """

    probability_value = validate_probability(probability)
    payout_value = validate_positive(payout, "Payout")
    return payout_value * probability_value


@dataclass(frozen=True)
class WavePoint:
    """One probability state in a Wave calculation."""

    probability: Decimal
    required_stake: Decimal
    total_payout: Decimal
    profit: Decimal


def target_profit_point(
    probability: Decimal | int | str,
    target_profit: Decimal | int | str,
) -> WavePoint:
    """Calculate the stake and payout required to reach a target profit.

    For a target profit ``T`` and probability ``p``:

    ``Stake = (T * p) / (1 - p)``
    ``Payout = Stake + T``
    """

    probability_value = validate_probability(probability)
    target_value = validate_positive(target_profit, "Target profit")
    required_stake = (target_value * probability_value) / (ONE - probability_value)
    total_payout = required_stake + target_value
    return WavePoint(
        probability=probability_value,
        required_stake=required_stake,
        total_payout=total_payout,
        profit=target_value,
    )


def fixed_stake_point(
    probability: Decimal | int | str,
    stake: Decimal | int | str,
) -> WavePoint:
    """Calculate payout and profit for a fixed stake at one probability."""

    probability_value = validate_probability(probability)
    stake_value = validate_positive(stake, "Stake")
    total_payout = payout_from_stake(probability_value, stake_value)
    return WavePoint(
        probability=probability_value,
        required_stake=stake_value,
        total_payout=total_payout,
        profit=total_payout - stake_value,
    )


def _probability_range(
    start: Decimal,
    end: Decimal,
    increment: Decimal,
) -> Iterable[Decimal]:
    """Yield an inclusive probability range, adding the endpoint when needed."""

    current = start
    while current <= end:
        yield current
        current += increment

    if current - increment != end:
        yield end


def generate_wave(
    target_profit: Decimal | int | str = DEFAULT_TARGET_PROFIT,
    start_probability: Decimal | int | str = DEFAULT_START,
    end_probability: Decimal | int | str = DEFAULT_END,
    increment: Decimal | int | str = DEFAULT_INCREMENT,
) -> list[WavePoint]:
    """Generate an inclusive fixed-profit sweep across probability states."""

    target_value = validate_positive(target_profit, "Target profit")
    start_value = validate_probability(start_probability)
    end_value = validate_probability(end_probability)
    increment_value = validate_positive(increment, "Increment")

    if start_value > end_value:
        raise ValueError("Start probability cannot exceed end probability.")

    return [
        target_profit_point(probability, target_value)
        for probability in _probability_range(
            start_value,
            end_value,
            increment_value,
        )
    ]


def generate_stake_wave(
    stake: Decimal | int | str = DEFAULT_STAKE,
    start_probability: Decimal | int | str = DEFAULT_START,
    end_probability: Decimal | int | str = DEFAULT_END,
    increment: Decimal | int | str = DEFAULT_INCREMENT,
) -> list[WavePoint]:
    """Generate an inclusive sweep with one fixed stake at every probability."""

    stake_value = validate_positive(stake, "Stake")
    start_value = validate_probability(start_probability)
    end_value = validate_probability(end_probability)
    increment_value = validate_positive(increment, "Increment")

    if start_value > end_value:
        raise ValueError("Start probability cannot exceed end probability.")

    return [
        fixed_stake_point(probability, stake_value)
        for probability in _probability_range(
            start_value,
            end_value,
            increment_value,
        )
    ]


def _money(value: Decimal) -> str:
    return f"${value.quantize(CENT):,.2f}"


def _percent(value: Decimal) -> str:
    return f"{(value * 100).quantize(CENT):,.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Jim Rockies Arb Wave.")
    parser.add_argument(
        "--mode",
        choices=("target-profit", "fixed-stake"),
        default="target-profit",
        help="Choose the fixed target profit or fixed stake calculation.",
    )
    parser.add_argument("--target-profit", default="100", help="Net profit target in dollars.")
    parser.add_argument("--stake", default="100", help="Fixed stake in dollars.")
    parser.add_argument("--start-percent", default="1", help="Starting probability percentage.")
    parser.add_argument("--end-percent", default="99", help="Ending probability percentage.")
    parser.add_argument("--increment-percent", default="1", help="Probability increment percentage.")
    args = parser.parse_args()

    start_probability = _decimal(args.start_percent, "Start percentage") / 100
    end_probability = _decimal(args.end_percent, "End percentage") / 100
    increment = _decimal(args.increment_percent, "Increment percentage") / 100
    if args.mode == "fixed-stake":
        rows = generate_stake_wave(args.stake, start_probability, end_probability, increment)
    else:
        rows = generate_wave(args.target_profit, start_probability, end_probability, increment)

    print("Probability | Required stake | Total payout | Profit")
    print("------------|-----------------|--------------|-------")
    for row in rows:
        print(
            f"{_percent(row.probability):>11} | "
            f"{_money(row.required_stake):>15} | "
            f"{_money(row.total_payout):>12} | "
            f"{_money(row.profit):>7}"
        )


if __name__ == "__main__":
    main()
