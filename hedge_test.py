import arb_math

dodgers_stake = float(input("Dodgers stake: "))
dodgers_odds = float(input("Dodgers American odds: "))

rockies_stake = float(input("Rockies stake: "))
rockies_odds = float(input("Rockies American odds: "))

total_stake = dodgers_stake + rockies_stake

dodgers_payout = arb_math.payout(dodgers_stake, dodgers_odds)
rockies_payout = arb_math.payout(rockies_stake, rockies_odds)

dodgers_result = dodgers_payout - total_stake
rockies_result = rockies_payout - total_stake

print("")
print("========================================")
print("           HEDGE ANALYSIS")
print("========================================")
print("")

print("Total Staked:", total_stake)
print("")

print("DODGERS WIN")
print("  Dodgers payout:", dodgers_payout)
print("  Net:", dodgers_result)
print("")

print("ROCKIES WIN")
print("  Rockies payout:", rockies_payout)
print("  Net:", rockies_result)
print("")

print("WORST CASE:", min(dodgers_result, rockies_result))
print("BEST CASE:", max(dodgers_result, rockies_result))

print("")
print("========================================")
