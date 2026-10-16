import json
import arb_math


def load_event(filename="test_data.json"):
    with open(filename) as handle:
        payload = json.load(handle)
    return payload["events"][0]


def get_teams(event):
    away = None
    home = None

    for team in event["teams"]:
        if team["is_away"]:
            away = team
        if team["is_home"]:
            home = team

    return away, home


def get_best_odds(event, away, home):
    best_away = None
    best_home = None

    for market in event["odds"]["moneyline"]:
        away_odds = market[away["abbreviation"]]
        home_odds = market[home["abbreviation"]]

        if best_away is None or away_odds > best_away:
            best_away = away_odds

        if best_home is None or home_odds > best_home:
            best_home = home_odds

    return best_away, best_home


def analyze_event(event):
    away, home = get_teams(event)
    best_away, best_home = get_best_odds(event, away, home)

    decimal_away = arb_math.american_to_decimal(best_away)
    decimal_home = arb_math.american_to_decimal(best_home)
    arb = arb_math.arb_index(decimal_away, decimal_home)
    is_arbitrage = arb_math.is_arbitrage(decimal_away, decimal_home)

    return {
        "away": away,
        "home": home,
        "best_away": best_away,
        "best_home": best_home,
        "arb": arb,
        "is_arbitrage": is_arbitrage,
    }


def main():
    result = analyze_event(load_event())
    away = result["away"]
    home = result["home"]

    print("{} @ {}".format(away["abbreviation"], home["abbreviation"]))
    print("Best {}: {:+g}".format(away["abbreviation"], result["best_away"]))
    print("Best {}: {:+g}".format(home["abbreviation"], result["best_home"]))
    print("Arb index: {:.4f}".format(result["arb"]))
    print("Arbitrage:", result["is_arbitrage"])
    return result


if __name__ == "__main__":
    main()
