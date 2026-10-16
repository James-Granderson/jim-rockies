"""
arb_math.py - Core mathematical base, arb evaluation, and state storage.
"""

from collections import deque
from decimal import Decimal, InvalidOperation, getcontext
from typing import Deque, List, Optional

getcontext().prec = 28


def _to_decimal(value):
    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Value must be numeric.") from exc


def validate_american_odds(odds):
    value = _to_decimal(odds)

    if value == 0 or abs(value) < 100:
        raise ValueError("American odds must be +/-100 or greater.")

    return value


def american_to_decimal(odds):
    value = validate_american_odds(odds)

    if value > 0:
        return Decimal("1") + (value / Decimal("100"))

    return Decimal("1") + (Decimal("100") / abs(value))


def validate_multiplier(multiplier):
    value = _to_decimal(multiplier)

    if value <= 1:
        raise ValueError("Multiplier must be greater than 1.")

    return value


def multiplier_to_decimal(multiplier):
    return validate_multiplier(multiplier)


def validate_stake(stake):
    value = _to_decimal(stake)

    if value <= 0:
        raise ValueError("Stake must be greater than zero.")

    return value


def decimal_payout(stake, decimal_odds):
    s = _to_decimal(stake)
    d = _to_decimal(decimal_odds)

    if s < 0:
        raise ValueError("Stake cannot be negative.")

    return s * d


def implied_probability(decimal_odds):
    d = _to_decimal(decimal_odds)

    if d <= 0:
        raise ValueError("Decimal odds must be greater than zero.")

    return Decimal("1") / d


class Odds:
    """
    A single price, held internally as decimal odds -- the one
    computational base everything in this project runs through.
    """

    def __init__(self, decimal_odds):
        self.decimal = _to_decimal(decimal_odds)

        if self.decimal <= 0:
            raise ValueError("Decimal odds must be greater than zero.")

    @classmethod
    def from_decimal(cls, decimal_odds):
        return cls(decimal_odds)

    @classmethod
    def from_american(cls, american_odds):
        return cls(american_to_decimal(american_odds))

    @classmethod
    def from_multiplier(cls, multiplier):
        return cls(multiplier_to_decimal(multiplier))

    @classmethod
    def from_probability(cls, probability):
        p = _to_decimal(probability)

        # Normalize whole percentages/cents (e.g., 38.57 -> 0.3857)
        if p >= Decimal("1"):
            p = p / Decimal("100")

        if p <= 0 or p >= 1:
            raise ValueError("Probability must be between 0 and 1 (or 0 and 100%).")

        return cls(Decimal("1") / p)

    @classmethod
    def from_stake_and_payout(cls, stake, payout):
        s = validate_stake(stake)
        p = _to_decimal(payout)
        if p <= 0:
            raise ValueError("Payout must be greater than zero.")
        return cls(p / s)

    @property
    def probability(self):
        return implied_probability(self.decimal)

    def payout(self, stake):
        return decimal_payout(stake, self.decimal)

    def arb_index(self, other):
        """Theoretical arb check -- sum of implied probabilities (< 1.00 = arb)."""
        return self.probability + other.probability

    def is_arbitrage(self, other, stake_a=None, stake_b=None):
        if stake_a is not None or stake_b is not None:
            stake_a_value = _to_decimal(stake_a) if stake_a is not None else Decimal("1")
            stake_b_value = _to_decimal(stake_b) if stake_b is not None else stake_a_value

            if stake_a_value <= 0 or stake_b_value <= 0:
                raise ValueError("Stake values must be greater than zero.")

            total_stake = stake_a_value + stake_b_value
            payout_a = self.payout(stake_a_value)
            payout_b = other.payout(stake_b_value)

            return (payout_a > total_stake) and (payout_b > total_stake)

        return self.arb_index(other) < 1

    def __repr__(self):
        return f"Odds(decimal={self.decimal})"


class Concretes:
    """
    Immutable representation of all concrete mathematical facts calculated
    for a given market state. Stored without presentation formatting so
    any module or downstream interface can inspect the variables directly.
    """

    def __init__(
        self,
        odds_a: Odds,
        odds_b: Odds,
        stake_a: Optional[Decimal] = None,
        stake_b: Optional[Decimal] = None,
        payout_a: Optional[Decimal] = None,
        payout_b: Optional[Decimal] = None,
    ):
        self.odds_a: Odds = odds_a
        self.odds_b: Odds = odds_b
        self.decimal_a: Decimal = odds_a.decimal
        self.decimal_b: Decimal = odds_b.decimal

        self.prob_a: Decimal = odds_a.probability
        self.prob_b: Decimal = odds_b.probability

        self.arb_index: Decimal = odds_a.arb_index(odds_b)
        self.is_theoretical_arb: bool = self.arb_index < Decimal("1.00")

        overround_pct = self.arb_index * Decimal("100")
        if self.is_theoretical_arb:
            self.market_vig: Decimal = Decimal("0.00")
            self.guaranteed_margin: Decimal = Decimal("100") - overround_pct
        else:
            self.market_vig: Decimal = overround_pct - Decimal("100")
            self.guaranteed_margin: Decimal = Decimal("0.00")

        self.stake_a: Optional[Decimal] = _to_decimal(stake_a) if stake_a is not None else None
        self.stake_b: Optional[Decimal] = _to_decimal(stake_b) if stake_b is not None else None

        if self.stake_a is not None and self.stake_b is not None:
            self.total_stake: Optional[Decimal] = self.stake_a + self.stake_b
            self.payout_a: Optional[Decimal] = (
                _to_decimal(payout_a) if payout_a is not None else self.odds_a.payout(self.stake_a)
            )
            self.payout_b: Optional[Decimal] = (
                _to_decimal(payout_b) if payout_b is not None else self.odds_b.payout(self.stake_b)
            )
            self.profit_a: Optional[Decimal] = self.payout_a - self.total_stake
            self.profit_b: Optional[Decimal] = self.payout_b - self.total_stake
            self.is_realized_arb: Optional[bool] = (
                self.payout_a > self.total_stake and self.payout_b > self.total_stake
            )
        else:
            self.total_stake = None
            self.payout_a = None
            self.payout_b = None
            self.profit_a = None
            self.profit_b = None
            self.is_realized_arb = None


class Information:
    """
    State accumulator and memory manager. Bounded ring buffer
    to prevent memory buildup.
    """

    def __init__(self, max_history: int = 1000):
        self._history: Deque[Concretes] = deque(maxlen=max_history)
        self.active: Optional[Concretes] = None

    def record(
        self,
        odds_a: Odds,
        odds_b: Odds,
        stake_a: Optional[Decimal] = None,
        stake_b: Optional[Decimal] = None,
        payout_a: Optional[Decimal] = None,
        payout_b: Optional[Decimal] = None,
    ) -> Concretes:
        snapshot = Concretes(odds_a, odds_b, stake_a, stake_b, payout_a, payout_b)
        self.active = snapshot
        self._history.append(snapshot)
        return snapshot

    @property
    def latest(self) -> Optional[Concretes]:
        return self.active

    @property
    def stack(self) -> List[Concretes]:
        return list(self._history)

    def flush(self) -> None:
        self._history.clear()
        self.active = None


if __name__ == "__main__":
    print("\n=== ARB MATH ENGINE ===")
    print("1) Check arb by Market Prices / Odds")
    print("2) Direct Stake + Payout Arb Check")
    print("")

    mode = input("Select calculation mode (1 or 2): ").strip()
    info = Information()

    if mode == "1":
        print("\nSelect Odds Format:")
        print("1) Decimal / Multiplier (e.g., 2.10, 1.95)")
        print("2) American Odds (e.g., +110, -120)")
        print("3) Probability / Cents (e.g., 55.38, 52.33, or 0.55)")

        odds_choice = input("Choice (1-3): ").strip()
        if odds_choice == "1":
            parser = Odds.from_multiplier
            label = "multiplier/decimal"
        elif odds_choice == "2":
            parser = Odds.from_american
            label = "American odds"
        elif odds_choice == "3":
            parser = Odds.from_probability
            label = "probability / % / cents (e.g., 55.38 or 0.55)"
        else:
            print("Invalid choice.")
            raise SystemExit(1)

        odds_a = parser(Decimal(input(f"Side A {label}: ")))
        odds_b = parser(Decimal(input(f"Side B {label}: ")))

        stake_a_in = None
        stake_b_in = None
        stake_input = input("\nTest realized stake split? Enter Stake A (or blank to skip): ").strip()
        if stake_input:
            stake_a_in = Decimal(stake_input)
            stake_b_in = Decimal(input("Enter Stake B: "))

        entry = info.record(odds_a, odds_b, stake_a=stake_a_in, stake_b=stake_b_in)

    elif mode == "2":
        print("\n--- Direct Stake & Payout Evaluation ---")
        stake_a = Decimal(input("Stake A: "))
        payout_a = Decimal(input("Payout A: "))
        stake_b = Decimal(input("Stake B: "))
        payout_b = Decimal(input("Payout B: "))

        odds_a = Odds.from_stake_and_payout(stake_a, payout_a)
        odds_b = Odds.from_stake_and_payout(stake_b, payout_b)

        entry = info.record(
            odds_a,
            odds_b,
            stake_a=stake_a,
            stake_b=stake_b,
            payout_a=payout_a,
            payout_b=payout_b,
        )

    else:
        print("Invalid choice.")
        raise SystemExit(1)

    print("\n" + "=" * 50)
    print(f"Side A Price: Decimal {entry.decimal_a:.3f} | Prob: {entry.prob_a * 100:.2f}%")
    print(f"Side B Price: Decimal {entry.decimal_b:.3f} | Prob: {entry.prob_b * 100:.2f}%")
    print("-" * 50)
    print(f"Arb Index        : {entry.arb_index:.4f} ({entry.arb_index * Decimal('100'):.2f}%)")
    print(f"Theoretical Arb  : {'YES (< 100%)' if entry.is_theoretical_arb else 'NO (>= 100%)'}")
    if not entry.is_theoretical_arb:
        print(f"Market Vig       : +{entry.market_vig:.2f}%")
    else:
        print(f"Guaranteed Margin: +{entry.guaranteed_margin:.2f}%")

    if entry.total_stake is not None:
        print("-" * 50)
        print(f"Total Capital Outflow : ${entry.total_stake:.2f}")
        print(f"A: Stake ${entry.stake_a:.2f} -> Payout ${entry.payout_a:.2f} | Net: ${entry.profit_a:+.2f}")
        print(f"B: Stake ${entry.stake_b:.2f} -> Payout ${entry.payout_b:.2f} | Net: ${entry.profit_b:+.2f}")
        print(f"Realized Arb          : {'YES' if entry.is_realized_arb else 'NO'}")
    print("=" * 50)