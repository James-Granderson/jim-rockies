# Arb Math Notes

## Core rule

Jim Rockies numeric inputs must be validated before entering the math layer. The math layer is a trusted domain that assumes its inputs are already legal JR values.

The intended flow is:

RAW INPUT
  -> syntax validation
  -> kind validation
  -> domain validation
  -> Decimal conversion
  -> JR math
  -> display

This is better than scattering defensive checks throughout formulas.

## Why Decimal

The project must avoid float-based precision drift. A value like `2.52` must remain exact as `Decimal("2.52")`.

Never do this:

Decimal(float(multiplier))

That preserves float representation error. The correct pattern is:

Decimal("2.52")

## Decimal conversion boundary

All calculation inputs should be converted to Decimal at the boundary, not later in the pipeline. Once a value is accepted as a valid JR numeric input, the rest of the arithmetic should remain in Decimal.

## Validation constraints

### Multiplier

Allowed to exist only when all of the following are true:
- numeric
- finite
- greater than 1
- not zero
- not negative
- not NaN
- not infinity

Examples:
- valid: 1.01, 1.10, 2.00, 3.5
- invalid: 0, 1.00, -2, NaN, infinity

### American odds

American odds must follow the actual betting math domain:
- positive odds must be at least +100
- negative odds must be at most -100
- zero is invalid
- values between -100 and +100 are invalid

Examples:
- valid: +100, +150, -110, -200
- invalid: 0, +50, -50, +99, -99

### Stakes and target profit

- stake must be greater than zero
- target profit must be greater than zero
- no zero, negative, NaN, or infinity values

## Important distinction

A value being mathematically calculable does not automatically make it valid JR input.

Python can calculate things like:
- 1 / 0
- 1 / -2
- 0-valued odds

But those are not necessarily valid JR inputs. JR should define and enforce its legal domain explicitly.

## Contract for arb_math

`arb_math` is the trusted computational layer. It should assume:
- inputs are already validated
- values are Decimal where appropriate
- no float drift is entering the system

The layer is responsible for exact arithmetic, not for making guesses about invalid user data.

## Current implementation

The code now follows this pattern:
- boundary validation functions for multipliers, American odds, stakes, and target profits
- Decimal conversion at the boundary
- Decimal-based arithmetic throughout the calculation chain
- tests covering valid and invalid inputs

This preserves fidelity between what JR accepts and what JR actually calculates.
