import arb_math
from decimal import Decimal, InvalidOperation


REFERENCE_STAKE = Decimal("100")


def parse_decimal_input(prompt, validator):

    while True:
        raw = input(prompt).strip()

        try:
            value = Decimal(raw)
        except InvalidOperation:
            print("Invalid input. Please enter a valid numeric value.")
            continue

        try:
            return validator(value)
        except ValueError as error:
            print(f"Invalid value: {error}")


def calculate_reach(stake_a, decimal_odds, target_profit):

    return arb_math.required_hedge_odds(
        stake_a,
        decimal_odds,
        target_profit
    )


def detect_arb(stake_a, odds_a, stake_b, odds_b, vig_factor=None):
    return arb_math.is_arbitrage(
        odds_a,
        odds_b,
        vig_factor=vig_factor,
        stake_a=stake_a,
        stake_b=stake_b,
    )


def reach_probability(stake_a, decimal_odds, target_profit):
    required = calculate_reach(stake_a, decimal_odds, target_profit)
    return arb_math.implied_probability(required)


def print_formula_trace(stake_a, odds_a):
    print("FORMULA TRACE")
    print("----------------------------------------")
    print("Safety default: if a required value is missing, use vig = 5% and adjust odds as odds × (1 - vig).")
    print("Payout A = Stake A × Odds A")
    print(f"Payout A = ${stake_a} × {odds_a:.2f} = ${stake_a * odds_a:.2f}")
    print("Required hedge stake B = Payout A - Stake A - Target Profit")
    print("Required odds B = Payout A / Required hedge stake B")
    print("Implied probability B = 1 / Required odds B")
    print("----------------------------------------")


if __name__ == "__main__":

    input_mode = input(
        "Input type: (1) American odds, (2) multiplier, (3) stake + payout: "
    ).strip()

    if input_mode == "1":

        odds = parse_decimal_input(
            "Enter American odds: ",
            arb_math.validate_american_odds
        )
        decimal_odds = arb_math.american_to_decimal(odds)
        stake_a = parse_decimal_input(
            "Enter stake on side A: ",
            arb_math.validate_stake
        )

    elif input_mode == "2":

        multiplier = parse_decimal_input(
            "Enter multiplier: ",
            arb_math.validate_multiplier
        )
        decimal_odds = arb_math.multiplier_to_decimal(multiplier)
        stake_a = parse_decimal_input(
            "Enter stake on side A: ",
            arb_math.validate_stake
        )

    elif input_mode == "3":

        stake_a = parse_decimal_input(
            "Enter stake on side A: ",
            arb_math.validate_stake
        )
        payout_a = parse_decimal_input(
            "Enter payout on side A: ",
            lambda value: value
        )
        if payout_a <= stake_a:
            raise ValueError("Payout A must be greater than stake A.")
        decimal_odds = payout_a / stake_a

    else:

        print("Please enter 1, 2, or 3.")
        exit()

    print()
    print(f"Stake A: ${stake_a}")
    print(f"Side A odds: {decimal_odds:.2f}x")
    print()
    print_formula_trace(stake_a, decimal_odds)
    print()
    print("MUST REACH (other side minimum odds)")
    print("------------------------------")

    for target_profit in range(1, 11):

        required = calculate_reach(
            stake_a,
            decimal_odds,
            target_profit
        )
        probability = reach_probability(
            stake_a,
            decimal_odds,
            target_profit
        )

        print(
            f"${target_profit:.2f} target -> "
            f"{required:.2f}x "
            f"({probability * Decimal('100'):.2f}% implied)"
        )