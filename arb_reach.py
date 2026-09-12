import arb_math
from decimal import Decimal, InvalidOperation


REFERENCE_STAKE = 100


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


def calculate_reach(decimal_odds, target_profit):

    return arb_math.required_odds(
        decimal_odds,
        REFERENCE_STAKE,
        target_profit
    )


if __name__ == "__main__":

    use_american = input(
        "Use American odds? (1 = yes, 0 = no): "
    ).strip()

    if use_american == "1":

        odds = parse_decimal_input(
            "Enter American odds: ",
            arb_math.validate_american_odds
        )
        decimal_odds = arb_math.american_to_decimal(odds)

    elif use_american == "0":

        multiplier = parse_decimal_input(
            "Enter multiplier: ",
            arb_math.validate_multiplier
        )
        decimal_odds = arb_math.multiplier_to_decimal(multiplier)

    else:

        print("Please enter 1 or 0.")
        exit()

    print()
    print(f"Decimal odds: {decimal_odds:.2f}")
    print()
    print("MUST REACH")
    print("------------------------------")

    for target_profit in range(1, 11):

        required = calculate_reach(
            decimal_odds,
            target_profit
        )

        print(
            f"${target_profit:.2f} -> "
            f"{required:.2f}x"
        )