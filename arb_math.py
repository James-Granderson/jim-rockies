from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 28

DEFAULT_VIG = Decimal("0.05")


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


def validate_fee_decimal(fee_decimal):
    value = _to_decimal(fee_decimal)

    if value < 0 or value >= 1:
        raise ValueError("Fee decimal must be between 0 and 1.")

    return value


def validate_vig(vig):
    value = _to_decimal(vig)

    if value < 0 or value >= 1:
        raise ValueError("Vig must be between 0 and 1.")

    return value


def apply_vig(decimal_odds, vig_factor=DEFAULT_VIG):
    d = _to_decimal(decimal_odds)
    v = validate_vig(vig_factor)

    if d <= 0:
        raise ValueError("Decimal odds must be greater than zero.")

    return d * (Decimal("1") - v)


def vig(decimal_odds, vig_factor=DEFAULT_VIG):
    return apply_vig(decimal_odds, vig_factor)


def apply_fee_decimal(decimal_odds, fee_decimal):
    base = _to_decimal(decimal_odds)
    fee = validate_fee_decimal(fee_decimal)
    return base * (Decimal("1") - fee)


def validate_stake(stake):
    value = _to_decimal(stake)

    if value <= 0:
        raise ValueError("Stake must be greater than zero.")

    return value


def arb_index(decimal_odds_a, decimal_odds_b, vig_factor=None, stake_a=None, stake_b=None):
    a = _to_decimal(decimal_odds_a)
    b = _to_decimal(decimal_odds_b)

    if a <= 0 or b <= 0:
        raise ValueError("Odds must be greater than zero.")

    if vig_factor is not None:
        a = apply_vig(a, vig_factor)
        b = apply_vig(b, vig_factor)

    if stake_a is not None or stake_b is not None:
        stake_a_value = _to_decimal(stake_a) if stake_a is not None else Decimal("1")
        stake_b_value = _to_decimal(stake_b) if stake_b is not None else stake_a_value

        if stake_a_value <= 0 or stake_b_value <= 0:
            raise ValueError("Stake values must be greater than zero.")

        total_stake = stake_a_value + stake_b_value
        payout_a = stake_a_value * a
        payout_b = stake_b_value * b
        profit_a = payout_a - total_stake
        profit_b = payout_b - total_stake

        return min(profit_a, profit_b)

    return (Decimal("1") / a) + (Decimal("1") / b)


def is_arbitrage(decimal_odds_a, decimal_odds_b, vig_factor=None, stake_a=None, stake_b=None):
    if stake_a is not None or stake_b is not None:
        stake_a_value = _to_decimal(stake_a) if stake_a is not None else Decimal("1")
        stake_b_value = _to_decimal(stake_b) if stake_b is not None else stake_a_value
        if stake_a_value <= 0 or stake_b_value <= 0:
            raise ValueError("Stake values must be greater than zero.")

        total_stake = stake_a_value + stake_b_value
        a = apply_vig(_to_decimal(decimal_odds_a), vig_factor) if vig_factor is not None else _to_decimal(decimal_odds_a)
        b = apply_vig(_to_decimal(decimal_odds_b), vig_factor) if vig_factor is not None else _to_decimal(decimal_odds_b)
        payout_a = stake_a_value * a
        payout_b = stake_b_value * b
        return (payout_a - total_stake) > 0 and (payout_b - total_stake) > 0

    return arb_index(decimal_odds_a, decimal_odds_b, vig_factor=vig_factor) < 1


def decimal_payout(stake, decimal_odds):
    s = _to_decimal(stake)
    d = _to_decimal(decimal_odds)

    if s < 0:
        raise ValueError("Stake cannot be negative.")

    return s * d


def direct_payout(stake, american_odds):
    return decimal_payout(stake, american_to_decimal(american_odds))


def payout(stake, american_odds):
    return direct_payout(stake, american_odds)


def implied_probability(decimal_odds, vig_factor=None):
    d = _to_decimal(decimal_odds)

    if d <= 0:
        raise ValueError("Decimal odds must be greater than zero.")

    if vig_factor is not None:
        d = apply_vig(d, vig_factor)

    return Decimal("1") / d


def probability_in_cents(decimal_odds, vig_factor=None):
    return implied_probability(decimal_odds, vig_factor=vig_factor) * Decimal("100")


def direct_probability(stake, payout):
    s = _to_decimal(stake)
    p = _to_decimal(payout)

    if p <= 0:
        raise ValueError("Payout must be greater than zero.")

    return (s / p) * Decimal("100")


def direct_arb(stake_a, payout_a, stake_b, payout_b):
    total_stake = _to_decimal(stake_a) + _to_decimal(stake_b)
    payout_a = _to_decimal(payout_a)
    payout_b = _to_decimal(payout_b)

    arb = (payout_a > total_stake) and (payout_b > total_stake)
    profit_a = payout_a - total_stake
    profit_b = payout_b - total_stake

    return {
        "stake_a": _to_decimal(stake_a),
        "stake_b": _to_decimal(stake_b),
        "total_stake": total_stake,
        "payout_a": payout_a,
        "payout_b": payout_b,
        "profit_if_a_wins": profit_a,
        "profit_if_b_wins": profit_b,
        "arb": arb,
        "profit_a": profit_a,
        "profit_b": profit_b,
    }


def hedge_result(stake_a, odds_a, stake_b, odds_b):
    total_stake = _to_decimal(stake_a) + _to_decimal(stake_b)

    payout_a = direct_payout(stake_a, odds_a)
    payout_b = direct_payout(stake_b, odds_b)

    result_a = payout_a - total_stake
    result_b = payout_b - total_stake

    return result_a, result_b


def required_odds(decimal_odds, stake, target_profit):
    d = _to_decimal(decimal_odds)
    s = _to_decimal(stake)
    p = _to_decimal(target_profit)

    if d <= 1:
        raise ValueError("Decimal odds must be greater than 1.")

    if s <= 0:
        raise ValueError("Stake must be greater than zero.")

    if p <= 0:
        raise ValueError("Target profit must be greater than zero.")

    return (s + p) / s


def required_hedge_odds(stake_a, odds_a, target_profit):
    s = _to_decimal(stake_a)
    d = _to_decimal(odds_a)
    p = _to_decimal(target_profit)

    if s <= 0:
        raise ValueError("Stake A must be greater than zero.")
    if d <= 1:
        raise ValueError("Side A odds must be greater than 1.")
    if p <= 0:
        raise ValueError("Target profit must be greater than zero.")

    payout_a = s * d
    required_b_stake = payout_a - s - p

    if required_b_stake <= 0:
        raise ValueError("This profit target is not achievable with the current odds.")

    return payout_a / required_b_stake


def normalize_side(stake=None, odds=None, payout=None, vig_factor=DEFAULT_VIG):
    resolved_stake = _to_decimal(stake) if stake is not None else None
    resolved_odds = _to_decimal(odds) if odds is not None else None
    resolved_payout = _to_decimal(payout) if payout is not None else None
    resolved_vig = validate_vig(vig_factor)

    if resolved_stake is not None and resolved_stake <= 0:
        raise ValueError("Stake must be greater than zero.")
    if resolved_odds is not None and resolved_odds <= 0:
        raise ValueError("Odds must be greater than zero.")
    if resolved_payout is not None and resolved_payout <= 0:
        raise ValueError("Payout must be greater than zero.")

    if resolved_payout is not None and resolved_stake is not None and resolved_odds is None:
        resolved_odds = resolved_payout / resolved_stake

    if resolved_odds is not None and resolved_stake is not None and resolved_payout is None:
        resolved_payout = resolved_stake * resolved_odds

    if resolved_odds is not None and resolved_payout is not None and resolved_stake is None:
        resolved_stake = resolved_payout / resolved_odds

    if resolved_stake is None and resolved_payout is None and resolved_odds is None:
        raise ValueError("At least one of stake, odds, or payout must be provided.")

    if resolved_stake is None:
        resolved_stake = resolved_payout / resolved_odds

    if resolved_odds is None:
        if resolved_payout is None:
            raise ValueError("Cannot infer odds without either payout or stake.")
        resolved_odds = resolved_payout / resolved_stake

    if resolved_payout is None:
        resolved_payout = resolved_stake * resolved_odds

    return {
        "stake": resolved_stake,
        "odds": resolved_odds,
        "payout": resolved_payout,
        "vig_factor": resolved_vig,
        "vig_adjusted_odds": apply_vig(resolved_odds, resolved_vig),
    }


def normalize_market(stake_a=None, odds_a=None, payout_a=None, stake_b=None, odds_b=None, payout_b=None, vig_factor=DEFAULT_VIG):
    side_a = normalize_side(stake=stake_a, odds=odds_a, payout=payout_a, vig_factor=vig_factor)
    side_b = normalize_side(stake=stake_b, odds=odds_b, payout=payout_b, vig_factor=vig_factor)

    return {
        "stake_a": side_a["stake"],
        "stake_b": side_b["stake"],
        "odds_a": side_a["odds"],
        "odds_b": side_b["odds"],
        "payout_a": side_a["payout"],
        "payout_b": side_b["payout"],
        "vig_factor": side_a["vig_factor"],
        "vig_adjusted_odds_a": side_a["vig_adjusted_odds"],
        "vig_adjusted_odds_b": side_b["vig_adjusted_odds"],
    }


def hedge_stake(stake_a, odds_a, odds_b):
    """
    Calculate the stake needed on side B to hedge an existing position on side A.
    stake_a: amount already wagered on side A
    odds_a: decimal odds of side A
    odds_b: decimal odds of side B
    returns: stake to place on side B to lock in profit
    """
    a = _to_decimal(stake_a)
    odds_a_dec = _to_decimal(odds_a)
    odds_b_dec = _to_decimal(odds_b)

    if a <= 0:
        raise ValueError("Stake A must be greater than zero.")
    if odds_a_dec <= 0 or odds_b_dec <= 0:
        raise ValueError("Odds must be greater than zero.")

    return (a * odds_a_dec) / odds_b_dec


def hedge_stake_range(stake_a, odds_a, odds_b_center, spread=Decimal("0.05"), step=Decimal("0.01"), vig_factor=DEFAULT_VIG):
    """Return a list of hedge-stake references around a center odds value."""
    a = _to_decimal(stake_a)
    odds_a_dec = _to_decimal(odds_a)
    center = _to_decimal(odds_b_center)
    spread_dec = _to_decimal(spread)
    step_dec = _to_decimal(step)

    if a <= 0:
        raise ValueError("Stake A must be greater than zero.")
    if odds_a_dec <= 0 or center <= 0:
        raise ValueError("Odds must be greater than zero.")
    if spread_dec < 0:
        raise ValueError("Spread must be non-negative.")
    if step_dec <= 0:
        raise ValueError("Step must be greater than zero.")

    start = center - spread_dec
    end = center + spread_dec
    samples = []

    total_steps = int(((end - start) / step_dec).to_integral_value()) + 1
    for index in range(total_steps):
        odds_b = start + (step_dec * index)
        samples.append({
            "odds_b": odds_b,
            "stake_b": hedge_stake(a, odds_a_dec, odds_b),
            "arb": is_arbitrage(odds_a_dec, odds_b, vig_factor=vig_factor),
            "probability": implied_probability(odds_b, vig_factor=vig_factor),
        })

    return samples


if __name__ == "__main__":

    print("")
    print("ARB MATH")
    print("1) American odds -> decimal odds")
    print("   Example: 110 or -110")
    print("2) Multiplier -> decimal odds")
    print("   Example: 2.50")
    print("3) Direct probability in cents")
    print("   Example: stake=20, payout=38.65")
    print("4) Direct stake + payout arb check")
    print("   Example: stake A=20, payout A=38.65 | stake B=37.62, payout B=19.65")
    print("")

    choice = input("Choose an option (1-4): ").strip()

    if choice == "1":
        odds = Decimal(input("American odds (example: 110 or -110): "))
        decimal_odds = american_to_decimal(odds)
        implied = probability_in_cents(decimal_odds)
        print(f"Decimal odds: {decimal_odds}")
        print(f"Implied probability: {implied}%")

    elif choice == "2":
        multiplier = Decimal(input("Multiplier (example: 2.50): "))
        decimal_odds = multiplier_to_decimal(multiplier)
        implied = probability_in_cents(decimal_odds)
        print(f"Decimal odds: {decimal_odds}")
        print(f"Implied probability: {implied}%")

    elif choice == "3":
        stake = Decimal(input("Stake (example: 20): "))
        payout = Decimal(input("Payout (example: 38.65): "))
        implied = direct_probability(stake, payout)
        print(f"Direct probability: {implied}%")
        print(f"Net on this side: {payout - stake}")

    elif choice == "4":
        stake_a = Decimal(input("Stake A (example: 20): "))
        payout_a = Decimal(input("Payout A (example: 38.65): "))
        stake_b = Decimal(input("Stake B (example: 37.62): "))
        payout_b = Decimal(input("Payout B (example: 19.65): "))

        result = direct_arb(stake_a, payout_a, stake_b, payout_b)

        print(f"Total stake: {result['total_stake']}")
        print(f"A payout: {result['payout_a']} | A profit: {result['profit_a']}")
        print(f"B payout: {result['payout_b']} | B profit: {result['profit_b']}")
        print(f"ARB: {result['arb']}")

    else:
        print("Invalid choice.")
