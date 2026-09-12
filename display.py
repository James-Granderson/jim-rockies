import json

data = open("test_data.json").read()
payload = json.loads(data)

for event in payload["events"]:

    teams = event["teams"]

    away = None
    home = None

    for team in teams:
        if team["is_away"]:
            away = team
        if team["is_home"]:
            home = team

    print("")
    print("========================================")
    print("              JIM ROCKIES")
    print("========================================")
    print("")
    print(away["abbreviation"], "@", home["abbreviation"])
    print(away["name"], away["mascot"])
    print(home["name"], home["mascot"])
    print("")

    print("MONEYLINE")
    print("----------------------------------------")

    for market in event["odds"]["moneyline"]:
        print(market["book"])
        print("  %s: %+d" % (
            away["abbreviation"],
            market[away["abbreviation"]]
        ))
        print("  %s: %+d" % (
            home["abbreviation"],
            market[home["abbreviation"]]
        ))
        print("")

    print("RUN LINE")
    print("----------------------------------------")

    for market in event["odds"]["runline"]:
        print(market["book"])

        print("  %s %+g  %+d" % (
            away["abbreviation"],
            market[away["abbreviation"]],
            market[away["abbreviation"] + "_odds"]
        ))

        print("  %s %+g  %+d" % (
            home["abbreviation"],
            market[home["abbreviation"]],
            market[home["abbreviation"] + "_odds"]
        ))

        print("")

    print("TOTAL")
    print("----------------------------------------")

    for market in event["odds"]["total"]:
        print(market["book"])
        print("  OVER  %g  %+d" % (
            market["line"],
            market["over"]
        ))
        print("  UNDER %g  %+d" % (
            market["line"],
            market["under"]
        ))

    print("")
    print("========================================")
