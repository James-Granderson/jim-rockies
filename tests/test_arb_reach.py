from decimal import Decimal

import pytest

from core.arb_math import Odds
from core.arb_reach import Reach, ReachReference, Vig


def test_reference_defaults_to_assumed_vig_branch():
    ref = ReachReference()
    assert ref.active_reference == Decimal("0.95")

    ref.use_assumed_vig(Decimal("0.06"))
    assert ref.active_reference == Decimal("0.94")

    ref.use_observed_vig(Decimal("0.60"), Decimal("0.40"))
    assert ref.active_reference == Decimal("1.00")


def test_reach_targets_and_ideal_margin_are_fractional():
    reach = Reach(
        Odds.from_probability(Decimal("0.55")),
        reference=ReachReference(),
        target_margin=Decimal("0.05"),
    )

    assert reach.reference.active_reference == Decimal("0.95")
    assert reach.acceptable_probability == Decimal("0.40")
    assert reach.ideal_probability == Decimal("0.35")
    assert reach.ideal_odds.decimal == Decimal("2.857142857142857142857142857")


def test_generate_spectrum_starts_at_acceptable_and_stops_at_ideal():
    reach = Reach(
        Odds.from_probability(Decimal("0.55")),
        reference=ReachReference(),
        target_margin=Decimal("0.05"),
    )

    states = list(reach.spectrum(steps=2))
    assert states[0][0] == Decimal("0.40")
    assert states[-1][0] == Decimal("0.35")


def test_vig_and_margin_reject_percent_units_inside_core():
    with pytest.raises(ValueError, match="fraction"):
        Vig(Decimal("5"))
    with pytest.raises(ValueError, match="fraction"):
        Reach(Odds.from_probability(Decimal("0.55")), target_margin=Decimal("5"))


def test_observed_reference_allows_exact_break_even_but_rejects_arb():
    ref = ReachReference()
    assert ref.use_observed_vig(Decimal("0.50"), Decimal("0.50")) == Decimal("1")
    with pytest.raises(ValueError, match="already have an arb"):
        ref.use_observed_vig(Decimal("0.49"), Decimal("0.50"))
