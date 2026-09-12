from decimal import Decimal, InvalidOperation


def _coerce_decimal(value, *, allow_multiplier_suffix=False, label="value"):

    if value is None or isinstance(value, bool):
        raise ValueError(f"{label} must be a numeric value.")

    if isinstance(value, Decimal):
        dec = value
    elif isinstance(value, int):
        dec = Decimal(value)
    elif isinstance(value, float):
        dec = Decimal(str(value))
    else:
        text = str(value).strip().lower().replace(" ", "")

        if allow_multiplier_suffix and text.endswith("x"):
            text = text[:-1]

        try:
            dec = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(f"{label} must be numeric.") from exc

    if not dec.is_finite():
        raise ValueError(f"{label} must be finite.")

    return dec


def validate_decimal_odds(value, *, label="decimal odds"):

    dec = _coerce_decimal(value, label=label)

    if dec <= Decimal("1"):
        raise ValueError(f"{label} must be greater than 1.")

    return dec


def validate_multiplier(value):

    dec = _coerce_decimal(value, allow_multiplier_suffix=True, label="multiplier")

    if dec <= Decimal("1"):
        raise ValueError("Multiplier must be greater than 1.")

    return dec


def validate_american_odds(value):

    dec = _coerce_decimal(value, label="American odds")

    if dec == Decimal("0"):
        raise ValueError("American odds cannot be zero.")

    if dec > 0:
        if dec < Decimal("100"):
            raise ValueError("Positive American odds must be at least +100.")
    elif dec < 0:
        if dec > Decimal("-100"):
            raise ValueError("Negative American odds must be at most -100.")
    else:
        raise ValueError("American odds cannot be zero.")

    return dec


def validate_target_profit(value):

    dec = _coerce_decimal(value, label="target profit")

    if dec <= 0:
        raise ValueError("Target profit must be greater than zero.")

    return dec


def validate_stake(value, *, allow_zero=False):

    dec = _coerce_decimal(value, label="stake")

    if allow_zero:
        if dec < 0:
            raise ValueError("Stake cannot be negative.")
        return dec

    if dec <= 0:
        raise ValueError("Stake must be greater than zero.")

    return dec


def american_to_decimal(odds):

    odds_decimal = validate_american_odds(odds)

    if odds_decimal > 0:
        return Decimal("1") + (odds_decimal / Decimal("100"))

    return Decimal("1") + (Decimal("100") / abs(odds_decimal))


def multiplier_to_decimal(multiplier):

    return validate_multiplier(multiplier)


def decimal_payout(stake, decimal_odds):

    stake_decimal = validate_stake(stake, allow_zero=True)
    odds_decimal = validate_decimal_odds(decimal_odds)
    return stake_decimal * odds_decimal


def arb_index(decimal_odds_a, decimal_odds_b):

    odds_a = validate_decimal_odds(decimal_odds_a, label="decimal odds A")
    odds_b = validate_decimal_odds(decimal_odds_b, label="decimal odds B")

    return (Decimal("1") / odds_a) + (Decimal("1") / odds_b)


def is_arbitrage(decimal_odds_a, decimal_odds_b):

    return arb_index(decimal_odds_a, decimal_odds_b) < Decimal("1")


def payout(stake, american_odds):

    stake_decimal = validate_stake(stake, allow_zero=True)

    if isinstance(american_odds, str):
        text = american_odds.strip().lower().replace(" ", "")

        if text.endswith("x"):
            return stake_decimal * validate_multiplier(text)

        american_odds = validate_american_odds(text)

    if isinstance(american_odds, (int, float, Decimal)):
        decimal_odds = american_to_decimal(american_odds)
        return stake_decimal * decimal_odds

    return stake_decimal * validate_decimal_odds(american_odds)


def hedge_result(stake_a, odds_a, stake_b, odds_b):

    total_stake = validate_stake(stake_a, allow_zero=True) + validate_stake(stake_b, allow_zero=True)

    payout_a = payout(stake_a, odds_a)
    payout_b = payout(stake_b, odds_b)

    result_a = payout_a - total_stake
    result_b = payout_b - total_stake

    return result_a, result_b


def required_odds(decimal_odds_a, total_stake, target_profit):

    odds_a = validate_decimal_odds(decimal_odds_a, label="decimal odds A")
    total_stake = validate_stake(total_stake)
    profit_target = validate_target_profit(target_profit)
    guaranteed_return = total_stake + profit_target
    denominator = total_stake - (guaranteed_return / odds_a)

    if denominator == 0:
        raise ValueError("Required odds denominator cannot be zero.")

    return guaranteed_return / denominator


if __name__ == "__main__":

    use_odds = input(
        "Use American odds? (1 = yes, 0 = no): "
    )

    if use_odds == "1":

        odds_a = Decimal(
            input("Enter American odds for outcome A: ")
        )

        odds_b = Decimal(
            input("Enter American odds for outcome B: ")
        )

        decimal_a = american_to_decimal(odds_a)
        decimal_b = american_to_decimal(odds_b)

    elif use_odds == "0":

        multiplier_a = input("Enter multiplier for outcome A: ")
        multiplier_b = input("Enter multiplier for outcome B: ")

        decimal_a = multiplier_to_decimal(multiplier_a)
        decimal_b = multiplier_to_decimal(multiplier_b)

    else:

        print("Please enter 1 or 0.")
        exit()

    probability_a = Decimal("1") / decimal_a
    probability_b = Decimal("1") / decimal_b

    arb = arb_index(decimal_a, decimal_b)

    print(f"Decimal A: {decimal_a:.2f}")
    print(f"Decimal B: {decimal_b:.2f}")

    print(f"Implied Probability A: {probability_a * Decimal('100'):.2f} %")
    print(f"Implied Probability B: {probability_b * Decimal('100'):.2f} %")

    print(f"Arbitrage Percentage: {arb * Decimal('100'):.2f} %")

    print(f"Arbitrage: {arb < Decimal('1')}")
