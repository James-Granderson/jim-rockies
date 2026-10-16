Jim Rockies

Quantitative sports-market analysis: sportsbook pricing, live market movement,
arbitrage conditions, and asymmetric position structures.

This project treats sportsbook odds as market prices. It analyzes the
relationship between prices for different outcomes, not just predicted winners.

Python 3 is required. On macOS, `python` often still points at Python 2.7.
Use `python3`:

    python3 arb_math.py
    python3 event_arb.py
    python3 display.py
    python3 hedge_range.py
    python3 hedge_test.py

Live fetch (optional):

    export RUNDOWN_ENDPOINT="your-endpoint"
    export RUNDOWN_API_KEY="your-key"
    python3 jim_rockies.py

Core modules

- arb_math.py: American/decimal conversion, implied probability, arb index,
  payouts, hedge results
- event_arb.py: best moneyline prices from test_data.json and arb detection
- hedge_range.py: stake allocations for a fixed bankroll, including best arb,
  high-EV, and max-profit positions
- display.py: print moneyline, run line, and total markets from test_data.json
- jim_rockies.py: fetch live market data using RUNDOWN_ENDPOINT / RUNDOWN_API_KEY

Do not commit API keys. Keep them in the environment.
