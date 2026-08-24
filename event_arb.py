import json
import arb_math

data = open("test_data.json").read()
payload = json.loads(data)

event = payload["events"][0]

away = None
home = None

for team in event["teams"]:
    if team["is_away"]:
        away = team
    if team["is_home"]:
        home = team

away_odds = []
home_odds = []

for market in event["odds"]["moneyline"]:
    away_odds.append(market[away["abbreviation"]])
    home_odds.append(market[home["abbreviation"]])

best_away = max(away_odds)
best_home = max(home_odds)

decimal_away = arb_math.american_to_decimal(best_away)
decimal_home = arb_math.american_to_decimal(best_home)

arb = arb_math.arb_index(decimal_away, decimal_home)

print ""
print away["name"], "@", home["name"]
print ""
print "Best", away["abbreviation"], ":", best_away
print "Best", home["abbreviation"], ":", best_home
print ""
print "Arbitrage Percentage:", arb * 100, "%"
print "Arbitrage:", arb < 1
