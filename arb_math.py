def american_to_decimal(odds):

    if odds > 0:
        return 1 + (odds / 100.0)

    else:
        return 1 + (100.0 / abs(odds))


def multiplier_to_decimal(multiplier):

    value = str(multiplier).strip().lower().replace(" ", "")

    if value.endswith("x"):
        value = value[:-1]

    return float(value)


def decimal_payout(stake, decimal_odds):

    return stake * decimal_odds


def arb_index(decimal_odds_a, decimal_odds_b):

    return (1 / decimal_odds_a) + (1 / decimal_odds_b)


def is_arbitrage(decimal_odds_a, decimal_odds_b):

    return arb_index(decimal_odds_a, decimal_odds_b) < 1


def payout(stake, american_odds):

    if isinstance(american_odds, str):
        text = american_odds.strip().lower().replace(" ", "")

        if text.endswith("x"):
            return stake * multiplier_to_decimal(text)

        american_odds = float(text)

    if isinstance(american_odds, (int, float)):
        decimal_odds = american_to_decimal(american_odds)
        return stake * decimal_odds

    return stake * float(american_odds)


def hedge_result(stake_a, odds_a, stake_b, odds_b):

    total_stake = stake_a + stake_b

    payout_a = payout(stake_a, odds_a)
    payout_b = payout(stake_b, odds_b)

    result_a = payout_a - total_stake
    result_b = payout_b - total_stake

    return result_a, result_b


if __name__ == "__main__":

    use_odds = input(
        "Use American odds? (1 = yes, 0 = no): "
    )

    if use_odds == "1":

        odds_a = float(
            input("Enter American odds for outcome A: ")
        )

        odds_b = float(
            input("Enter American odds for outcome B: ")
        )

        decimal_a = american_to_decimal(odds_a)
        decimal_b = american_to_decimal(odds_b)

    elif use_odds == "0":

        multiplier_a = float(
            input("Enter multiplier for outcome A: ")
        )

        multiplier_b = float(
            input("Enter multiplier for outcome B: ")
        )

        decimal_a = multiplier_to_decimal(multiplier_a)
        decimal_b = multiplier_to_decimal(multiplier_b)

    else:

        print("Please enter 1 or 0.")
        exit()

    probability_a = 1 / decimal_a
    probability_b = 1 / decimal_b

    arb = arb_index(decimal_a, decimal_b)

    print(f"Decimal A: {decimal_a:.2f}")
    print(f"Decimal B: {decimal_b:.2f}")

    print(f"Implied Probability A: {probability_a * 100:.2f} %")
    print(f"Implied Probability B: {probability_b * 100:.2f} %")

    print(f"Arbitrage Percentage: {arb * 100:.2f} %")

    print(f"Arbitrage: {arb < 1}")
