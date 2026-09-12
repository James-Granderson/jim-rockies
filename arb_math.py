def american_to_decimal(odds):
    if odds > 0:
        return 1 + (odds / 100.0)
    else:
        return 1 + (100.0 / abs(odds))


def parse_to_decimal_odds(odds_input: str | int | float) -> float:
    """Normalizes input (American odds or multiplier strings) into decimal odds format."""
    if isinstance(odds_input, (int, float)):
        return american_to_decimal(float(odds_input))

    if isinstance(odds_input, str):
        text = odds_input.strip().lower().replace(" ", "")
        if text.endswith("x"):
            val = float(text[:-1])
            if val <= 0:
                raise ValueError("Multiplier must be greater than 0.")
            return val
        return american_to_decimal(float(text))

    raise TypeError(f"Unsupported odds type: {type(odds_input)}")


def decimal_payout(stake: float, decimal_odds: float) -> float:
    """Calculates total payout given a stake and decimal odds."""
    if stake < 0:
        raise ValueError("Stake cannot be negative.")
    if decimal_odds <= 0:
        raise ValueError("Decimal odds must be greater than 0.")
    return stake * decimal_odds


def payout(stake: float, odds_input: str | int | float) -> float:
    """Calculates payout by normalizing odds input to decimal odds first."""
    decimal_odds = parse_to_decimal_odds(odds_input)
    return decimal_payout(stake, decimal_odds)


def arb_index(decimal_odds_a: float, decimal_odds_b: float) -> float:
    """Calculates the arbitrage index (implied probability sum)."""
    if decimal_odds_a <= 0 or decimal_odds_b <= 0:
        raise ValueError("Decimal odds must be strictly positive.")
    return (1.0 / decimal_odds_a) + (1.0 / decimal_odds_b)


def is_arbitrage(decimal_odds_a: float, decimal_odds_b: float) -> bool:
    """Returns True if an arbitrage opportunity exists."""
    return arb_index(decimal_odds_a, decimal_odds_b) < 1.0


def hedge_result(stake_a: float, odds_a: str | float, stake_b: float, odds_b: str | float) -> tuple[float, float]:
    """Calculates net profit/loss for both outcomes of a two-way hedge."""
    total_stake = stake_a + stake_b
    net_a = payout(stake_a, odds_a) - total_stake
    net_b = payout(stake_b, odds_b) - total_stake
    return net_a, net_b


def required_odds(decimal_odds_a: float, total_stake: float, target_profit: float) -> float:
    """Calculates required decimal odds on Outcome B to lock in target profit."""
    guaranteed_return = total_stake + target_profit
    denominator = total_stake - (guaranteed_return / decimal_odds_a)
    
    if denominator <= 0:
        raise ValueError("Target profit is unachievable with the given stake and Outcome A odds.")
    
    return guaranteed_return / denominator


if __name__ == "__main__":
    use_odds = input("Use American odds? (1 = yes, 0 = no): ").strip()

    try:
        if use_odds == "1":
            odds_a_raw = input("Enter American odds for outcome A: ")
            odds_b_raw = input("Enter American odds for outcome B: ")
            decimal_a = parse_to_decimal_odds(odds_a_raw)
            decimal_b = parse_to_decimal_odds(odds_b_raw)

        elif use_odds == "0":
            mult_a_raw = input("Enter multiplier for outcome A (e.g. 2.5 or 2.5x): ")
            mult_b_raw = input("Enter multiplier for outcome B (e.g. 1.8 or 1.8x): ")
            decimal_a = parse_to_decimal_odds(mult_a_raw if mult_a_raw.endswith("x") else f"{mult_a_raw}x")
            decimal_b = parse_to_decimal_odds(mult_b_raw if mult_b_raw.endswith("x") else f"{mult_b_raw}x")

        else:
            print("Invalid selection. Please enter 1 or 0.")
            exit(1)

        prob_a = 1 / decimal_a
        prob_b = 1 / decimal_b
        arb = arb_index(decimal_a, decimal_b)

        print(f"\nDecimal A: {decimal_a:.2f}")
        print(f"Decimal B: {decimal_b:.2f}")
        print(f"Implied Probability A: {prob_a * 100:.2f}%")
        print(f"Implied Probability B: {prob_b * 100:.2f}%")
        print(f"Arbitrage Percentage: {arb * 100:.2f}%")
        print(f"Arbitrage Opportunity: {is_arbitrage(decimal_a, decimal_b)}")

    except (ValueError, TypeError) as err:
        print(f"\nExecution Error: {err}")
        exit(1)
