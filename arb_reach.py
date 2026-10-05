"""
arb_reach.py - Navigation distance engine for jim-rockies.
Operates strictly in probability space. All odds conversions and parsing
are delegated to arb_math.Odds.
"""

from decimal import Decimal, getcontext
from typing import List, Optional, Tuple
from arb_math import Odds, _to_decimal

getcontext().prec = 28

ONE_HUNDRED_PCT = Decimal("1.00")


class Vig:
    """
    Manages vig and cushion calculations.
    Assumed vig is mutable and defaults to 5% (0.05).
    """

    def __init__(self, assumed_vig: Decimal = Decimal("0.05")):
        self.assumed_vig: Decimal = _to_decimal(assumed_vig)

    def set_assumed_vig(self, new_vig: Decimal) -> None:
        """Mutates the assumed vig benchmark."""
        val = _to_decimal(new_vig)
        if val >= Decimal("1"):
            val = val / Decimal("100")
        if val < Decimal("0"):
            raise ValueError("Assumed vig cannot be negative.")
        self.assumed_vig = val

    @staticmethod
    def calculate_overround(prob_a: Decimal, prob_b: Decimal) -> Decimal:
        """Sum of implied probabilities."""
        return _to_decimal(prob_a) + _to_decimal(prob_b)

    @classmethod
    def calculate_observed_vig(cls, prob_a: Decimal, prob_b: Decimal) -> Decimal:
        """Observed vig = market overround - 100%."""
        return cls.calculate_overround(prob_a, prob_b) - ONE_HUNDRED_PCT

    @staticmethod
    def apply_vig(reference_base: Decimal, vig_value: Decimal) -> Decimal:
        """reference = base - vig (e.g., 1.00 - 0.05 = 0.95)."""
        return _to_decimal(reference_base) - _to_decimal(vig_value)

    def __repr__(self) -> str:
        return f"Vig(assumed={self.assumed_vig * Decimal('100'):.2f}%)"


class ReachReference:
    """
    Controls what probability target Reach measures against.
    Starts at neutral 100% and explicitly branches:
      - Branch A: Observed vig (derived from live market odds)
      - Branch B: Assumed vig (mutable hard-mode benchmark, e.g. 5%)
      - Branch C: Neutral (pure 100% baseline)
    """

    def __init__(self, vig: Optional[Vig] = None):
        self.vig: Vig = vig if vig is not None else Vig()
        self.base_reference: Decimal = ONE_HUNDRED_PCT
        self.mode: str = "assumed"
        self._observed_vig: Optional[Decimal] = None

    def reset_neutral(self) -> Decimal:
        """Branch C: 100% neutral baseline."""
        self.mode = "neutral"
        self._observed_vig = None
        return self.active_reference

    def use_assumed_vig(self, custom_assumed: Optional[Decimal] = None) -> Decimal:
        """Branch B: Assumed vig baseline (e.g. 100% - 5% = 95%)."""
        if custom_assumed is not None:
            self.vig.set_assumed_vig(custom_assumed)
        self.mode = "assumed"
        return self.active_reference

    def use_observed_vig(self, prob_a: Decimal, prob_b: Decimal) -> Decimal:
        """Branch A: Deducts live observed market vig from 100% base."""
        overround = self.vig.calculate_overround(prob_a, prob_b)
        if overround <= ONE_HUNDRED_PCT:
            edge = (ONE_HUNDRED_PCT - overround) * Decimal("100")
            raise ValueError(
                f"You already have an arb! Market overround is {overround * 100:.2f}% "
                f"(+{edge:.2f}% edge). There is no vig — head to the reference scale or execute."
            )

        self._observed_vig = self.vig.calculate_observed_vig(prob_a, prob_b)
        self.mode = "observed"
        return self.active_reference

    @property
    def active_reference(self) -> Decimal:
        if self.mode == "neutral":
            return self.base_reference
        elif self.mode == "assumed":
            return self.vig.apply_vig(self.base_reference, self.vig.assumed_vig)
        elif self.mode == "observed":
            if self._observed_vig is None:
                raise ValueError("Observed vig requested, but no market probabilities supplied.")
            return self.vig.apply_vig(self.base_reference, self._observed_vig)
        raise ValueError(f"Unknown reference mode: {self.mode}")

    def __repr__(self) -> str:
        return f"ReachReference(mode='{self.mode}', target={self.active_reference * Decimal('100'):.2f}%)"


class Reach:
    """
    Core navigation engine.
    Ingests an Odds instance as anchor, extracts pure probability,
    and calculates required target thresholds.
    """

    def __init__(
        self,
        anchor_odds: Odds,
        reference: Optional[ReachReference] = None,
        target_margin: Decimal = Decimal("0.00"),
    ):
        self.anchor_odds: Odds = anchor_odds
        self.reference: ReachReference = reference if reference is not None else ReachReference()

        m = _to_decimal(target_margin)
        if m >= Decimal("1"):
            m = m / Decimal("100")
        self.target_margin: Decimal = m

    @property
    def anchor_probability(self) -> Decimal:
        return self.anchor_odds.probability

    @property
    def acceptable_probability(self) -> Decimal:
        """Reach = Active Reference - Anchor Probability."""
        prob = self.reference.active_reference - self.anchor_probability
        if prob <= Decimal("0"):
            raise ValueError("Anchor probability consumes entire reference window.")
        return prob

    @property
    def ideal_probability(self) -> Decimal:
        """Opposing threshold factoring in desired extra profit cushion."""
        prob = self.acceptable_probability - self.target_margin
        if prob <= Decimal("0"):
            raise ValueError("Target margin exceeds available probability headroom.")
        return prob

    @property
    def acceptable_odds(self) -> Odds:
        """Target threshold returned as an Odds instance."""
        return Odds.from_probability(self.acceptable_probability)

    @property
    def ideal_odds(self) -> Odds:
        """Ideal threshold returned as an Odds instance."""
        return Odds.from_probability(self.ideal_probability)

    def spectrum(self, steps: int = 5) -> List[Tuple[Decimal, Odds]]:
        """Discrete stepping array between acceptable and ideal thresholds."""
        if steps < 2:
            return [(self.acceptable_probability, self.acceptable_odds)]

        step_size = (self.acceptable_probability - self.ideal_probability) / Decimal(steps - 1)
        results = []
        for i in range(steps):
            prob = self.acceptable_probability - (step_size * Decimal(i))
            results.append((prob, Odds.from_probability(prob)))
        return results


def to_american_str(decimal_odds: Decimal) -> str:
    """Helper to cleanly display Odds in American format."""
    if decimal_odds >= Decimal("2.00"):
        val = (decimal_odds - Decimal("1.00")) * Decimal("100")
        return f"+{val:.0f}"
    else:
        val = Decimal("100") / (decimal_odds - Decimal("1.00"))
        return f"-{val:.0f}"


if __name__ == "__main__":
    print("\n=== ARB REACH NAVIGATION ENGINE ===")
    print("1) Multiplier / Decimal (e.g., 2.74, 1.45)")
    print("2) American Odds (e.g., +174, -140)")
    print("3) Probability / % / Cents (e.g., 36.50, 63.50)")

    fmt_choice = input("Select Board Format (1-3, default 1): ").strip() or "1"

    if fmt_choice == "1":
        parser = Odds.from_multiplier
        prompt_label = "multiplier/decimal"
    elif fmt_choice == "2":
        parser = Odds.from_american
        prompt_label = "American odds"
    elif fmt_choice == "3":
        parser = Odds.from_probability
        prompt_label = "probability/%/cents"
    else:
        print("Invalid choice.")
        raise SystemExit(1)

    # 1. Capture the board upfront
    try:
        raw_a = input(f"Side A [Planted Anchor] ({prompt_label}): ").strip()
        anchor = parser(raw_a)

        raw_b = input(f"Side B [Current Opposing] ({prompt_label}): ").strip()
        board_b = parser(raw_b)
    except Exception as err:
        print(f"\n[ERROR] Invalid price entry: {err}")
        raise SystemExit(1)

    print("\n[Board Ingested]")
    print(f"  Side A (Anchor) : {anchor.probability * 100:.2f}% | Decimal {anchor.decimal:.3f}")
    print(f"  Side B (Current): {board_b.probability * 100:.2f}% | Decimal {board_b.decimal:.3f}")

    # 2. Select Reference Baseline
    print("\n--- Reference Baseline ---")
    print("1) Assumed Vig (Default: 5% cushion -> 95% target baseline)")
    print("2) Observed Vig (Use current Side B above to measure live market overround)")
    print("3) Neutral (Pure 100% break-even baseline)")

    ref_choice = input("Choice (1-3, default 1): ").strip() or "1"
    ref = ReachReference()

    if ref_choice == "1":
        custom_vig = input("Enter assumed vig % (press Enter for default 5%): ").strip()
        try:
            if custom_vig:
                ref.use_assumed_vig(Decimal(custom_vig))
            else:
                ref.use_assumed_vig()
        except ValueError as err:
            print(f"\n[ERROR] {err}")
            raise SystemExit(1)

    elif ref_choice == "2":
        try:
            ref.use_observed_vig(anchor.probability, board_b.probability)
        except ValueError as err:
            print(f"\n[ERROR] {err}")
            raise SystemExit(1)

    elif ref_choice == "3":
        ref.reset_neutral()

    # 3. Target Cushion / Margin
    margin_in = input("\nTarget extra profit margin % (e.g., 2 for 2%, or Enter for 0%): ").strip()
    margin = Decimal(margin_in) if margin_in else Decimal("0.00")

    reach_engine = Reach(anchor, reference=ref, target_margin=margin)

    try:
        acc_prob = reach_engine.acceptable_probability * Decimal("100")
        acc_dec = reach_engine.acceptable_odds.decimal
    except ValueError as err:
        print(f"\n[ERROR] {err}")
        raise SystemExit(1)

    print("\n" + "=" * 55)
    print(f"Planted Anchor     : {reach_engine.anchor_probability * 100:.2f}% (Decimal {anchor.decimal:.3f})")
    print(f"Active Reference   : {ref.mode.upper()} ({ref.active_reference * 100:.2f}% baseline)")
    print("-" * 55)
    print("TARGET OPPOSING LINE REQUIRED:")
    print(f"Acceptable Floor   : <= {acc_prob:.2f}% (Decimal {acc_dec:.3f} | {to_american_str(acc_dec)})")

    if margin > 0:
        try:
            ideal_prob = reach_engine.ideal_probability * Decimal("100")
            ideal_dec = reach_engine.ideal_odds.decimal
            print(f"Ideal (+{margin}% margin): <= {ideal_prob:.2f}% (Decimal {ideal_dec:.3f} | {to_american_str(ideal_dec)})")

            print("\n--- Transition Spectrum (5 Ticks) ---")
            for idx, (p, odds) in enumerate(reach_engine.spectrum(5), 1):
                print(f"  Step {idx}: <= {p * 100:.2f}% -> Decimal {odds.decimal:.3f} ({to_american_str(odds.decimal)})")
        except ValueError as err:
            print(f"\n[ERROR] {err}")
            raise SystemExit(1)

    print("=" * 55)