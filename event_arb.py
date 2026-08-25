import json
import arb_math


def load_event(filename="test_data.json"):
    data = open(filename).read()
    payload = json.loads(data)
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

    best_away, best_home = get_best_odds(
        event,
        away,
        home
    )

    decimal_away = arb_math.american_to_decimal(best_away)
    decimal_home = arb_math.american_to_decimal(best_home)

    arb = arb_math.arb_index(
        decimal_away,
        decimal_home
    )

    return {
        "away": away,
        "home": home,
        "best_away": best_away,
        "best_home": best_home,
        "arb": arb
    }


def main():
    event = load_event()
    return analyze_event(event)


if __name__ == "__main__":
    main()