def american_to_decimal(odds):
    if odds > 0:
        return 1 + (odds / 100.0)
    return 1 + (100.0 / abs(odds))


def implied_probability(decimal_odds):
    return 1 / decimal_odds


def arb_index(decimal_odds_a, decimal_odds_b):
    return implied_probability(decimal_odds_a) + implied_probability(decimal_odds_b)


def is_arbitrage(decimal_odds_a, decimal_odds_b):
    return arb_index(decimal_odds_a, decimal_odds_b) < 1


def payout(stake, american_odds):
    return stake * american_to_decimal(american_odds)


def hedge_result(stake_a, odds_a, stake_b, odds_b):
    total_stake = stake_a + stake_b
    result_a = payout(stake_a, odds_a) - total_stake
    result_b = payout(stake_b, odds_b) - total_stake
    return result_a, result_b


if __name__ == "__main__":
    odds_a = float(input("Enter American odds for outcome A: "))
    odds_b = float(input("Enter American odds for outcome B: "))

    decimal_a = american_to_decimal(odds_a)
    decimal_b = american_to_decimal(odds_b)

    probability_a = implied_probability(decimal_a)
    probability_b = implied_probability(decimal_b)
    arb = arb_index(decimal_a, decimal_b)

    print("Implied Probability A: {:.2f}%".format(probability_a * 100))
    print("Implied Probability B: {:.2f}%".format(probability_b * 100))
    print("Arbitrage Percentage: {:.2f}%".format(arb * 100))
    print("Arbitrage:", is_arbitrage(decimal_a, decimal_b))
