import arb_math


RESET = "\033[0m"
RED = "\033[38;2;220;70;70m"
YELLOW = "\033[38;2;220;190;70m"
GREEN = "\033[38;2;70;210;90m"


def color_value(value, width=10):

    value = float(value)
    text = "$%+.2f" % value

    if value < 0:
        color = RED
    elif value > 0:
        color = GREEN
    else:
        color = YELLOW

    return color + text.ljust(width) + RESET


def color_dollar(value, width=10):

    text = "$%-8.0f" % value
    return GREEN + text.ljust(width) + RESET


def analyze_range(odds_a, odds_b, total_stake, use_odds):

    if use_odds == "1":

        decimal_a = arb_math.american_to_decimal(odds_a)
        decimal_b = arb_math.american_to_decimal(odds_b)

    else:

        decimal_a = arb_math.multiplier_to_decimal(odds_a)
        decimal_b = arb_math.multiplier_to_decimal(odds_b)

    index = arb_math.arb_index(decimal_a, decimal_b)
    odds_status = "ARB" if index < 1 else "NO ARB"

    scale = []

    for stake_a in range(int(total_stake) + 1):

        stake_b = total_stake - stake_a

        payout_a = arb_math.decimal_payout(
            stake_a,
            decimal_a
        )

        payout_b = arb_math.decimal_payout(
            stake_b,
            decimal_b
        )

        profit_a = payout_a - total_stake
        profit_b = payout_b - total_stake

        worst = min(profit_a, profit_b)
        best = max(profit_a, profit_b)

        scale.append({
            "stake_a": stake_a,
            "stake_b": stake_b,
            "profit_a": profit_a,
            "profit_b": profit_b,
            "worst": worst,
            "best": best
        })

    return index, odds_status, scale


def find_best_arb(scale):

    positions = []

    for r in scale:

        if r["profit_a"] >= 0 and r["profit_b"] >= 0:
            positions.append(r)

    if not positions:
        return None

    return max(
        positions,
        key=lambda x: (x["worst"], x["best"])
    )


def find_max_profit(scale):

    return max(
        scale,
        key=lambda x: x["best"]
    )


def find_best_high_ev(scale, high_ev_side):

    if high_ev_side == "A":
        favorite = "profit_a"
        hedge = "profit_b"
    else:
        favorite = "profit_b"
        hedge = "profit_a"

    best = None

    for r in scale:

        hedge_result = r[hedge]
        favorite_result = r[favorite]

        if best is None:
            best = r
            continue

        best_hedge_result = best[hedge]
        current_distance = abs(hedge_result)
        best_distance = abs(best_hedge_result)

        # Primary objective:
        # minimize the hedge-side loss / distance from zero.
        #
        # Secondary objective:
        # preserve as much high-EV profit as possible.
        if current_distance < best_distance:
            best = r

        elif current_distance == best_distance:

            if favorite_result > best[favorite]:
                best = r

    return best


def print_money(value, width=11):

    return color_value(value, width)


def print_stake(value, width=10):

    return color_dollar(value, width)


def print_high_ev_position(position, high_ev_side):

    if position is None:
        print("")
        print("NO HIGH-EV POSITION FOUND")
        return

    print("")
    print("HIGH-EV POSITION")
    print("----------------------------------------")

    if high_ev_side == "A":

        print("HIGH-EV SIDE: A")
        print("HEDGE SIDE:   B")

    else:

        print("HIGH-EV SIDE: B")
        print("HEDGE SIDE:   A")

    print("")
    print("A: %s" % print_stake(
        position["stake_a"]
    ))

    print("B: %s" % print_stake(
        position["stake_b"]
    ))

    print("")
    print("A WINS:  %s" % print_money(
        position["profit_a"]
    ))

    print("B WINS:  %s" % print_money(
        position["profit_b"]
    ))

    if high_ev_side == "A":

        favorite_profit = position["profit_a"]
        hedge_result = position["profit_b"]

    else:

        favorite_profit = position["profit_b"]
        hedge_result = position["profit_a"]

    print("")
    print("HIGH-EV PROFIT: %s" % print_money(
        favorite_profit
    ))

    print("HEDGE RESULT:   %s" % print_money(
        hedge_result
    ))

    print("")
    print("WORST CASE:  %s" % print_money(
        position["worst"]
    ))

    print("BEST CASE:   %s" % print_money(
        position["best"]
    ))


def print_hedge_range(scale, position):

    if position is None:
        return

    center = int(position["stake_a"])

    start = max(0, center - 5)
    end = min(len(scale) - 1, center + 5)

    print("")
    print("HEDGE RANGE")
    print("----------------------------------------")
    print("A STAKE    B STAKE    A WIN       B WIN")

    for i in range(start, end + 1):

        r = scale[i]

        print("%s %s %s %s" % (
            print_stake(r["stake_a"]),
            print_stake(r["stake_b"]),
            print_money(r["profit_a"]),
            print_money(r["profit_b"])
        ))


def print_reference_scale(scale):

    print("")
    print("REFERENCE SCALE")
    print("----------------------------------------")
    print("A STAKE    B STAKE    A WIN       B WIN")

    step = 5

    for i in range(0, len(scale), step):

        r = scale[i]

        print("%s %s %s %s" % (
            print_stake(r["stake_a"]),
            print_stake(r["stake_b"]),
            print_money(r["profit_a"]),
            print_money(r["profit_b"])
        ))

    if (len(scale) - 1) % step != 0:

        r = scale[-1]

        print("%s %s %s %s" % (
            print_stake(r["stake_a"]),
            print_stake(r["stake_b"]),
            print_money(r["profit_a"]),
            print_money(r["profit_b"])
        ))


def get_number(prompt):

    while True:

        try:
            value = input(prompt).strip()
            value = value.lower().replace(" ", "")

            if value.endswith("x"):
                value = value[:-1]

            return float(value)

        except ValueError:

            print("")
            print("Invalid input. Please enter a number.")
            print("")


def get_side():

    while True:

        side = input(
            "Which side is your HIGH-EV side? (A/B): "
        ).strip().upper()

        if side in ("A", "B"):
            return side

        print("")
        print("Please enter A or B.")
        print("")


if __name__ == "__main__":

    print("")
    print("========================================")
    print("          ARB / HEDGE ANALYSIS")
    print("========================================")
    print("")

    try:

        use_odds = input(
            "Use American odds or multiplier? (1 = odds, 0 = multiplier): "
        )

        if use_odds == "1":

            odds_a = get_number(
                "Enter American odds for outcome A: "
            )

            odds_b = get_number(
                "Enter American odds for outcome B: "
            )

        elif use_odds == "0":

            odds_a = get_number(
                "Enter multiplier for outcome A: "
            )

            odds_b = get_number(
                "Enter multiplier for outcome B: "
            )

        else:

            raise ValueError(
                "Please enter 1 for odds or 0 for multiplier."
            )

        total_stake = get_number(
            "Enter total stake: "
        )

        if total_stake <= 0:
            raise ValueError(
                "Total stake must be greater than zero."
            )

        high_ev_side = get_side()

        index, odds_status, scale = analyze_range(
            odds_a,
            odds_b,
            total_stake,
            use_odds
        )

        best_arb = find_best_arb(scale)
        best_high_ev = find_best_high_ev(
            scale,
            high_ev_side
        )
        max_profit = find_max_profit(scale)

        print("")
        print("A: %+g" % odds_a)
        print("B: %+g" % odds_b)
        print("Stake: $%.2f" % total_stake)
        print("")

        if use_odds == "1":
            decimal_a = arb_math.american_to_decimal(odds_a)
            decimal_b = arb_math.american_to_decimal(odds_b)
        else:
            decimal_a = arb_math.multiplier_to_decimal(odds_a)
            decimal_b = arb_math.multiplier_to_decimal(odds_b)

        is_arb = arb_math.is_arbitrage(decimal_a, decimal_b)

        prob_a = 1.0 / decimal_a
        prob_b = 1.0 / decimal_b
        prob_a_pct = prob_a * 100.0
        prob_b_pct = prob_b * 100.0

        a_label = "%sx" % odds_a if use_odds == "0" else "%+g" % odds_a
        b_label = "%sx" % odds_b if use_odds == "0" else "%+g" % odds_b

        if prob_a_pct + prob_b_pct < 100:
            relation = "< 100%"
        elif prob_a_pct + prob_b_pct > 100:
            relation = "> 100%"
        else:
            relation = "= 100%"

        print("ARB INDEX: %.4f" % index)
        print("%.2f%% + %.2f%% %s -> %s" % (
            prob_a_pct,
            prob_b_pct,
            relation,
            "ARB" if is_arb else "NO ARB"
        ))
        print("ARB: %s" % ("YES" if is_arb else "NO"))

        if best_arb:

            print("")
            print("BEST ARB POSITION")
            print("----------------------------------------")

            print("A: %s" % print_stake(
                best_arb["stake_a"]
            ))

            print("B: %s" % print_stake(
                best_arb["stake_b"]
            ))

            print("")
            print("A WINS:  %s" % print_money(
                best_arb["profit_a"]
            ))

            print("B WINS:  %s" % print_money(
                best_arb["profit_b"]
            ))

            print("")
            print("GUARANTEED: %s" % print_money(
                best_arb["worst"]
            ))

            print("MAXIMUM:   %s" % print_money(
                best_arb["best"]
            ))

        else:

            print("")
            print("NO ARBITRAGE POSITION")

        print_high_ev_position(
            best_high_ev,
            high_ev_side
        )

        print("")
        print("MAXIMUM PROFIT POSITION")
        print("----------------------------------------")

        print("A: %s" % print_stake(
            max_profit["stake_a"]
        ))

        print("B: %s" % print_stake(
            max_profit["stake_b"]
        ))

        print("")
        print("A WINS:  %s" % print_money(
            max_profit["profit_a"]
        ))

        print("B WINS:  %s" % print_money(
            max_profit["profit_b"]
        ))

        print("")
        print("MAXIMUM: %s" % print_money(
            max_profit["best"]
        ))

        print_hedge_range(
            scale,
            best_high_ev
        )

        print_reference_scale(
            scale
        )

        print("")
        print("========================================")

    except ValueError as error:

        print("")
        print("ERROR:", error)
        print("")
        print("Please check your inputs and try again.")

    except Exception as error:

        print("")
        print("UNEXPECTED ERROR:", error)
        print("")
        print("The calculation could not be completed.")