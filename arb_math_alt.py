from decimal import Decimal

class concretes:
    def __init__(self, multiplier, american_odds, probability, payout_a, payout_b, odds, stake_a, stake_b)

class odds:
def __init__(self, multiplier, american_odds, probability):
self.multiplier = multiplier
self.american_odds = american_odds
self.probability = probability

def convert_odds(self):

def request_odds(self):
    request_odds = input("Enter 1 for multiplier, 2 for American Odds (e.g. -110, +110), or 3 for implied probability")
    
    if request_odds = 1:
        printf("Enter multiplier odds")
     elif request_odds = 2:
         printf("Enter American Odds")
      elif request_odds = 3:
        printf("Enter implied probability")
        else:
         return False


class is_arbitrage:
    def __init__(self, payout_a, payout_b, odds_a, odds_b, stake_a, stake_b):
        self.payout_a = payout_a
        self.payout_b = payout_b
        self.odds_a = odds_a
        self.odds_b = odds_b
        self.stake_a = stake_a
        self.stake_b = stake_b

        def check_arbitrage(self):
            if (self.payout_a >= self.payout_b):
                return True
                or ((1/ odds) + (1 / odds) < 1)
            else:
                return False