def american_to_decimal(odds):

    if odds > 0:
        return 1 + (odds / 100.0)

    else:
        return 1 + (100.0 / abs(odds))


def arb_index(decimal_odds_a, decimal_odds_b):

    return (1 / decimal_odds_a) + (1 / decimal_odds_b)


def is_arbitrage(decimal_odds_a, decimal_odds_b):

    return arb_index(decimal_odds_a, decimal_odds_b) < 1


def payout(stake, american_odds):

    decimal_odds = american_to_decimal(american_odds)

    return stake * decimal_odds


def hedge_result(stake_a, odds_a, stake_b, odds_b):

    total_stake = stake_a + stake_b

    payout_a = payout(stake_a, odds_a)
    payout_b = payout(stake_b, odds_b)

    result_a = payout_a - total_stake
    result_b = payout_b - total_stake

    return result_a, result_b


if __name__ == "__main__":

    odds_a = float(input("Enter American odds for outcome A: "))

    odds_b = float(input("Enter American odds for outcome B: "))

    decimal_a = american_to_decimal(odds_a)

    decimal_b = american_to_decimal(odds_b)

    probability_a = 1 / decimal_a

    probability_b = 1 / decimal_b

    arb = arb_index(decimal_a, decimal_b)

    print "Implied Probability A:", probability_a * 100, "%"

    print "Implied Probability B:", probability_b * 100, "%"

    print "Arbitrage Percentage:", arb * 100, "%"

    print "Arbitrage:", arb < 1
