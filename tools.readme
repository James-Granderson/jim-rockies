# Jim Rockies Tools Catalog

This file is a compact tool index for the project. The idea is that each file has a clear purpose and a clear "job" in the system, so the repo reads like a set of tools rather than a pile of scripts.

## Core math and contracts

### arb_math.py
Purpose: the trusted numerical engine.

What it does:
- converts American odds to decimal odds
- converts multipliers to decimal odds
- validates JR input constraints
- calculates implied probability and arbitrage index
- computes payouts and required odds
- keeps the math in Decimal for precision safety

This is the legal contract layer for all numeric inputs.

### arb_math_notes.md
Purpose: design notes and rules.

What it does:
- records the Decimal policy
- documents the validation rules for odds, multipliers, stakes, and target profit
- explains the difference between valid JR input and mathematically calculable but invalid values

### hedge_range_readme.md
Purpose: plain-English explanation of the range logic.

What it does:
- explains arb_reach.py and hedge_range.py
- documents the difference between arb, high-EV, and max-profit objectives
- describes how the stake range is evaluated

## Market / reach analysis tools

### arb_reach.py
Purpose: must-reach target calculator.

What it does:
- takes a single odds value
- computes the required decimal odds needed to hit a profit target
- prints the target range for $1 through $10 profit
- uses a fixed $100 reference stake

Think of this as: "what odds do I need to reach my target?"

### hedge_range.py
Purpose: stake split and hedge analysis.

What it does:
- takes equity A / B odds and total stake
- evaluates every stake split in the range
- computes profit for each side under each outcome
- identifies:
  - best arbitrage position
  - high-EV position
  - max-profit position
- prints hedge range and reference scale

Think of this as: "what should I stake on each side?"

## Event-level and market tools

### event_arb.py
Purpose: event-level arbitrage analysis.

What it does:
- loads a market/event payload
- identifies away and home teams
- finds the best odds for each side
- evaluates whether the event has an arbitrage condition

Think of this as: "analyze a specific market event."

### scraper.py
Purpose: data acquisition.

What it does:
- fetches sportsbook / market data
- collects odds from external sources
- prepares data for downstream analysis

This is the ingestion layer.

### display.py
Purpose: formatting and presentation helpers.

What it does:
- color formatting
- readable output for financial values
- display wrappers for report output

### config.py
Purpose: project configuration.

What it does:
- stores runtime settings
- holds project-specific defaults and parameters

## Utility and support tools

### get_test.py
Purpose: quick data / sampling utility.

What it does:
- used for testing / fetch / inspect flows
- useful for debugging data inputs and outputs

### jim_rockies.py
Purpose: top-level project runner / workflow entry point.

What it does:
- can coordinate the project’s main analysis flow
- may serve as the broader orchestration layer

### prizepicks.html
Purpose: front-end or display artifact.

What it does:
- local HTML/demo output for odds or market presentation

### test_decimal_arb_math.py
Purpose: regression protection for numeric correctness.

What it does:
- verifies Decimal conversion behavior
- verifies invalid input rejection
- validates the JR numerical contract

## Interpretation model

The repo is best understood as a set of small tools with distinct jobs:

- data gathering
- odds conversion and validation
- arbitrage detection
- hedge optimization
- output formatting
- market event analysis

The tool boundaries are intentionally separate so that each component can be tested and reasoned about independently.

## Rule of thumb

If a file is doing math, it belongs in the arb_math / odds-validation layer.
If a file is deciding a stake split or selecting a position, it belongs in the hedge-range layer.
If a file is pulling market data, it belongs in the scraper / data layer.
If a file is mostly output or display, it belongs in display / formatting.

This is the mental model for the project.
