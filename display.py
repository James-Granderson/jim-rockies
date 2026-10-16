import json


def load_events(filename="test_data.json"):
    with open(filename) as handle:
        payload = json.load(handle)
    return payload["events"]


def print_event(event):
    away = None
    home = None

    for team in event["teams"]:
        if team["is_away"]:
            away = team
        if team["is_home"]:
            home = team

    print()
    print("========================================")
    print("              JIM ROCKIES")
    print("========================================")
    print()
    print("{} @ {}".format(away["abbreviation"], home["abbreviation"]))
    print(away["name"], away["mascot"])
    print(home["name"], home["mascot"])
    print()

    print("MONEYLINE")
    print("----------------------------------------")

    for market in event["odds"]["moneyline"]:
        print(market["book"])
        print("  {}: {:+d}".format(
            away["abbreviation"],
            market[away["abbreviation"]],
        ))
        print("  {}: {:+d}".format(
            home["abbreviation"],
            market[home["abbreviation"]],
        ))
        print()

    print("RUN LINE")
    print("----------------------------------------")

    for market in event["odds"]["runline"]:
        print(market["book"])
        print("  {} {:+g}  {:+d}".format(
            away["abbreviation"],
            market[away["abbreviation"]],
            market[away["abbreviation"] + "_odds"],
        ))
        print("  {} {:+g}  {:+d}".format(
            home["abbreviation"],
            market[home["abbreviation"]],
            market[home["abbreviation"] + "_odds"],
        ))
        print()

    print("TOTAL")
    print("----------------------------------------")

    for market in event["odds"]["total"]:
        print(market["book"])
        print("  OVER  {:g}  {:+d}".format(market["line"], market["over"]))
        print("  UNDER {:g}  {:+d}".format(market["line"], market["under"]))

    print()
    print("========================================")


def main():
    for event in load_events():
        print_event(event)


if __name__ == "__main__":
    main()
