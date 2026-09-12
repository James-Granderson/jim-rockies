# Hedge Range and Reach Notes

This file explains the two main analysis scripts in plain language.

## 1) arb_reach.py

Purpose:
- Given one decimal odds value, compute the multiplier required to reach a target profit level.
- This is the "Must Reach" calculator.

What it does:
- takes a single odds value
- uses a reference stake of $100
- computes the required odds for each target profit from $1 to $10

The high-level idea:
- if the current odds are too low, you need a higher required result to hit your target
- the script shows what odds you must reach to hit each profit threshold

Example:
- $1 target -> required decimal odds x
- $2 target -> required decimal odds x
- ...
- $10 target -> required decimal odds x

This file is not about range analysis or hedging. It is about checking the required threshold to reach a profit target.

## 2) hedge_range.py

Purpose:
- analyze a two-side market across all possible stake splits
- identify the best arbitrage position
- identify the best high-EV position
- identify the max-profit position
- show the hedge range and reference scale

This is the main "what do I stake on each side?" tool.

### Inputs
- odds A and odds B
- total stake
- which side is the high-EV side

### Core calculation
For each possible stake split from 0 to total stake:
- stake A = i
- stake B = total stake - i

For each split, calculate:
- payout if A wins
- payout if B wins
- net profit for A side
- net profit for B side
- worst-case result
- best-case result

This creates a full range of outcomes, not just one fixed stake split.

## The three objectives in hedge_range.py

### A) Best arb position

This is the safest arbitrage position.

The script looks for positions where both outcomes are non-negative.

The chosen result is the position maximizing:
- worst-case result
- then best-case result

This is the best guaranteed arb split.

### B) High-EV position

This is the edge-focused position.

It targets the side the user has selected as the higher expected value side.

The logic is:
- choose the side the user called "high EV"
- compare profit on that side versus profit on the hedge side
- prefer the split where the hedge side loss is minimized
- then prefer the split with the biggest high-EV profit

This means:
- it is not simply trying to maximize total profit
- it is trying to maximize the favored side while limiting downside on the hedge side

So the core idea is:

"If I believe side A is the better bet, how do I split the stake to maximize A's upside while keeping B's downside as small as possible?"

This is a risk-adjusted, edge-focused stake allocation.

### C) Max profit position

This is the pure maximum-upside position.

The script looks for the stake split with the largest best-case result.

This may produce a larger upside but may also involve a bigger downside.

This is different from the high-EV position, which is more about directional edge and control of the hedge side.

## Why this matters

The script is not just one algorithm. It is actually three different objectives packed into one tool:

- arb safety
- high-EV optimization
- pure max profit

If you do not clearly separate them, the output reads like nonsense because the code is answering different questions with the same range data.

## Important distinction

The phrase "best" depends on the goal:

- best for arbitrage = safest guaranteed position
- best for high EV = maximize edge while containing hedge loss
- best for max profit = maximize top-end upside

## Practical rule of thumb

- Use arb_reach.py for required-return thresholds.
- Use hedge_range.py for stake split decisions.
- Interpret the outputs by objective, not by a single hidden definition of "best."

## Design recommendation

The code should be documented in terms of objective, not just formulas.

The real questions are:

1. Are we looking for guaranteed arbitrage?
2. Are we looking for a high-EV directional stake split?
3. Are we looking for maximum upside regardless of downside?

Once those objectives are explicit, the code becomes much easier to reason about.
