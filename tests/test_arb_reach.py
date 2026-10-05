from decimal import Decimal

from arb_reach import Reach, ReachReference


def test_reference_defaults_to_assumed_vig_branch():
    ref = ReachReference()
    assert ref.active_reference == Decimal("0.95")

    ref.use_assumed_vig(Decimal("0.06"))
    assert ref.active_reference == Decimal("0.94")

    ref.use_observed_vig(Decimal("0.60"), Decimal("0.40"))
    assert ref.active_reference == Decimal("0.94")


def test_reach_targets_and_ideal_margin_are_calculated_from_reference():
    ref = ReachReference()
    ref.use_assumed_vig(Decimal("0.05"))

    reach = Reach(
        anchor_probability=Decimal("0.55"),
        opposing_probability=Decimal("0.60"),
        reach_reference=ref,
        ideal_margin=Decimal("0.05"),
    )

    assert reach.reference == Decimal("0.95")
    assert reach.target_probability == Decimal("0.40")
    assert reach.distance_to_target == Decimal("0.20")
    assert reach.remaining_reach == Decimal("0.35")
    assert reach.ideal_target_odds.decimal_odds == Decimal("2.857142857142857142857142857")


def test_generate_spectrum_starts_at_current_opp_and_stops_at_ideal_target():
    ref = ReachReference()
    ref.use_assumed_vig(Decimal("0.05"))

    reach = Reach(
        anchor_probability=Decimal("0.55"),
        opposing_probability=Decimal("0.60"),
        reach_reference=ref,
        ideal_margin=Decimal("0.05"),
    )

    states = list(reach.generate_spectrum(step=Decimal("0.05")))
    assert states[0].probability == Decimal("0.60")
    assert states[-1].probability == Decimal("0.35")
    assert states[0].distance_from_opp == Decimal("0.00")
