import arb_math


RESET = "\033[0m"
RED = "\033[38;2;220;70;70m"
YELLOW = "\033[38;2;220;190;70m"
GREEN = "\033[38;2;70;210;90m"


def color_value(value, width=10):
    value = float(value)
    text = "${:+.2f}".format(value)

    if value < 0:
        color = RED
    elif value > 0:
        color = GREEN
    else:
        color = YELLOW

    return color + text.ljust(width) + RESET


def color_dollar(value, width=10):
    text = "${:<8.0f}".format(value)
    return GREEN + text.ljust(width) + RESET


def analyze_range(odds_a, odds_b, total_stake):
    decimal_a = arb_math.american_to_decimal(odds_a)
    decimal_b = arb_math.american_to_decimal(odds_b)
    index = arb_math.arb_index(decimal_a, decimal_b)
    odds_status = "ARBITRAGE" if arb_math.is_arbitrage(decimal_a, decimal_b) else "NO ARBITRAGE"

    scale = []

    for stake_a in range(int(total_stake) + 1):
        stake_b = total_stake - stake_a
        payout_a = arb_math.payout(stake_a, odds_a)
        payout_b = arb_math.payout(stake_b, odds_b)
        profit_a = payout_a - total_stake
        profit_b = payout_b - total_stake

        scale.append({
            "stake_a": stake_a,
            "stake_b": stake_b,
            "profit_a": profit_a,
            "profit_b": profit_b,
            "worst": min(profit_a, profit_b),
            "best": max(profit_a, profit_b),
        })

    return index, odds_status, scale


def find_best_arb(scale):
    positions = [
        row for row in scale
        if row["profit_a"] >= 0 and row["profit_b"] >= 0
    ]

    if not positions:
        return None

    return max(positions, key=lambda x: (x["worst"], x["best"]))


def find_max_profit(scale):
    return max(scale, key=lambda x: x["best"])


def find_best_high_ev(scale, high_ev_side):
    if high_ev_side == "A":
        favorite = "profit_a"
        hedge = "profit_b"
    else:
        favorite = "profit_b"
        hedge = "profit_a"

    best = None

    for row in scale:
        hedge_result = row[hedge]
        favorite_result = row[favorite]

        if best is None:
            best = row
            continue

        current_distance = abs(hedge_result)
        best_distance = abs(best[hedge])

        if current_distance < best_distance:
            best = row
        elif current_distance == best_distance and favorite_result > best[favorite]:
            best = row

    return best


def print_money(value, width=11):
    return color_value(value, width)


def print_stake(value, width=10):
    return color_dollar(value, width)


def print_high_ev_position(position, high_ev_side):
    print()
    print("HIGH-EV POSITION")
    print("----------------------------------------")

    if high_ev_side == "A":
        print("HIGH-EV SIDE: A")
        print("HEDGE SIDE:   B")
        favorite_profit = position["profit_a"]
        hedge_result = position["profit_b"]
    else:
        print("HIGH-EV SIDE: B")
        print("HEDGE SIDE:   A")
        favorite_profit = position["profit_b"]
        hedge_result = position["profit_a"]

    print()
    print("A: {}".format(print_stake(position["stake_a"])))
    print("B: {}".format(print_stake(position["stake_b"])))
    print()
    print("A WINS:  {}".format(print_money(position["profit_a"])))
    print("B WINS:  {}".format(print_money(position["profit_b"])))
    print()
    print("HIGH-EV PROFIT: {}".format(print_money(favorite_profit)))
    print("HEDGE RESULT:   {}".format(print_money(hedge_result)))
    print()
    print("WORST CASE:  {}".format(print_money(position["worst"])))
    print("BEST CASE:   {}".format(print_money(position["best"])))


def print_hedge_range(scale, position):
    center = int(position["stake_a"])
    start = max(0, center - 5)
    end = min(len(scale) - 1, center + 5)

    print()
    print("HEDGE RANGE")
    print("----------------------------------------")
    print("A STAKE    B STAKE    A WIN       B WIN")

    for i in range(start, end + 1):
        row = scale[i]
        print("{} {} {} {}".format(
            print_stake(row["stake_a"]),
            print_stake(row["stake_b"]),
            print_money(row["profit_a"]),
            print_money(row["profit_b"]),
        ))


def print_reference_scale(scale):
    print()
    print("REFERENCE SCALE")
    print("----------------------------------------")
    print("A STAKE    B STAKE    A WIN       B WIN")

    step = 5

    for i in range(0, len(scale), step):
        row = scale[i]
        print("{} {} {} {}".format(
            print_stake(row["stake_a"]),
            print_stake(row["stake_b"]),
            print_money(row["profit_a"]),
            print_money(row["profit_b"]),
        ))

    if (len(scale) - 1) % step != 0:
        row = scale[-1]
        print("{} {} {} {}".format(
            print_stake(row["stake_a"]),
            print_stake(row["stake_b"]),
            print_money(row["profit_a"]),
            print_money(row["profit_b"]),
        ))


def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print()
            print("Invalid input. Please enter a number.")
            print()


def get_side():
    while True:
        side = input("Which side is your HIGH-EV side? (A/B): ").strip().upper()
        if side in ("A", "B"):
            return side
        print()
        print("Please enter A or B.")
        print()


if __name__ == "__main__":
    print()
    print("========================================")
    print("          ARB / HEDGE ANALYSIS")
    print("========================================")
    print()

    try:
        odds_a = get_number("Enter American odds for outcome A: ")
        odds_b = get_number("Enter American odds for outcome B: ")
        total_stake = get_number("Enter total stake: ")

        if total_stake <= 0:
            raise ValueError("Total stake must be greater than zero.")

        high_ev_side = get_side()
        index, odds_status, scale = analyze_range(odds_a, odds_b, total_stake)
        best_arb = find_best_arb(scale)
        best_high_ev = find_best_high_ev(scale, high_ev_side)
        max_profit = find_max_profit(scale)

        print()
        print("A: {:+g}".format(odds_a))
        print("B: {:+g}".format(odds_b))
        print("Stake: ${:.2f}".format(total_stake))
        print()
        print("ARB INDEX: {:.4f}".format(index))
        print("STATUS:", odds_status)

        if best_arb:
            print()
            print("BEST ARB POSITION")
            print("----------------------------------------")
            print("A: {}".format(print_stake(best_arb["stake_a"])))
            print("B: {}".format(print_stake(best_arb["stake_b"])))
            print()
            print("A WINS:  {}".format(print_money(best_arb["profit_a"])))
            print("B WINS:  {}".format(print_money(best_arb["profit_b"])))
            print()
            print("GUARANTEED: {}".format(print_money(best_arb["worst"])))
            print("MAXIMUM:   {}".format(print_money(best_arb["best"])))
        else:
            print()
            print("NO ARBITRAGE POSITION")

        print_high_ev_position(best_high_ev, high_ev_side)

        print()
        print("MAXIMUM PROFIT POSITION")
        print("----------------------------------------")
        print("A: {}".format(print_stake(max_profit["stake_a"])))
        print("B: {}".format(print_stake(max_profit["stake_b"])))
        print()
        print("A WINS:  {}".format(print_money(max_profit["profit_a"])))
        print("B WINS:  {}".format(print_money(max_profit["profit_b"])))
        print()
        print("MAXIMUM: {}".format(print_money(max_profit["best"])))

        print_hedge_range(scale, best_high_ev)
        print_reference_scale(scale)

        print()
        print("========================================")

    except ValueError as error:
        print()
        print("ERROR:", error)
        print()
        print("Please check your inputs and try again.")

    except Exception as error:
        print()
        print("UNEXPECTED ERROR:", error)
        print()
        print("The calculation could not be completed.")
