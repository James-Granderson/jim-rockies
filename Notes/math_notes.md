# Math Notes for Jim Rockies

## 1. Decimals and Percentages

Ultimate tip: Use knowledge

A decimal represents a fraction of 1.

Examples:

0.10 = 10%
0.25 = 25%
0.50 = 50%
0.75 = 75%
1.00 = 100%

### Decimal -> Percentage

Multiply by 100.

decimal * 100 = percentage

Example:

0.35 * 100 = 35%

### Percentage -> Decimal

Divide by 100.

percentage / 100 = decimal

Example:

35 / 100 = 0.35


## 2. Why We Use Decimals in Programming

Computers often represent proportions as decimals because
they are convenient for calculations.

Example:

probability = 0.35

This means:

probability = 35%


## 3. Important Mental Model

Decimal:
    "How much of 1?"

Percentage:
    "How much out of 100?"

So:

0.35 = 35/100 = 35%

😂 Got you. **Game-screen mode.** No skipping invisible steps.



---

# 🎮 ARB MATH — EXECUTION SCREEN

**Starting state**

```text
Variables:     NONE
Functions:     NONE
```

Python begins reading line 1.

---

### MOVE 1 — CREATE FUNCTION

```python
def american_to_decimal(odds):
```

Python says:

> "Create a function named `american_to_decimal`."

It does **not** run the function yet.

```text
Functions:
    american_to_decimal()

Variables:
    NONE
```

---

### MOVE 2 — CREATE FUNCTION

```python
def arb_index(decimal_odds_a, decimal_odds_b):
```

Python creates another function.

Still **not running it**.

```text
Functions:
    american_to_decimal()
    arb_index()

Variables:
    NONE
```

---

### MOVE 3 — CREATE FUNCTION

```python
def is_arbitrage(decimal_odds_a, decimal_odds_b):
```

Again, Python just stores the function.

```text
Functions:
    american_to_decimal()
    arb_index()
    is_arbitrage()

Variables:
    NONE
```

Now we've finished defining the tools.

---

# 🎮 PLAYER INPUT

Python reaches:

```python
odds_a = float(input("Enter American odds for outcome A: "))
```

### MOVE 4 — CALL `input()`

```text
CALL:
    input("Enter American odds for outcome A: ")
```

Screen:

```text
Enter American odds for outcome A:
```

You type:

```text
200
```

`input()` returns:

```text
"200"
```

Notice:

```text
"200"
```

is **text**.

---

### MOVE 5 — CALL `float()`

Python immediately feeds `"200"` into:

```python
float("200")
```

Result:

```text
200.0
```

Then assignment happens:

```python
odds_a = 200.0
```

### STATE

```text
odds_a = 200.0
```

---

# 🎮 SECOND INPUT

### MOVE 6 — CALL `input()`

```python
input("Enter American odds for outcome B: ")
```

You type:

```text
300
```

`input()` returns:

```text
"300"
```

---

### MOVE 7 — CALL `float()`

```python
float("300")
```

returns:

```text
300.0
```

Then:

```python
odds_b = 300.0
```

### STATE

```text
odds_a = 200.0
odds_b = 300.0
```

---

# 🎮 CONVERSION

### MOVE 8 — CALL FUNCTION

Python reaches:

```python
decimal_a = american_to_decimal(odds_a)
```

Substitute the variable:

```python
american_to_decimal(200.0)
```

Python **enters the function**.

Inside:

```text
odds = 200.0
```

---

### MOVE 9 — CHECK CONDITION

```python
if odds > 0:
```

Python asks:

```text
200.0 > 0?
```

Result:

```text
TRUE
```

So Python takes the `if` branch.

---

### MOVE 10 — CALCULATE

```python
1 + (odds / 100)
```

Substitute:

```text
1 + (200.0 / 100)
```

Then:

```text
1 + 2.0
```

Then:

```text
3.0
```

---

### MOVE 11 — RETURN

```python
return 3.0
```

Python **leaves the function** and sends `3.0` back here:

```python
decimal_a = american_to_decimal(odds_a)
```

Therefore:

```text
decimal_a = 3.0
```

### STATE

```text
odds_a    = 200.0
odds_b    = 300.0
decimal_a = 3.0
```

---

# 🎮 SECOND CONVERSION

### MOVE 12

```python
decimal_b = american_to_decimal(odds_b)
```

Becomes:

```python
american_to_decimal(300.0)
```

Inside:

```text
odds = 300.0
```

Check:

```text
300.0 > 0?
```

TRUE.

Calculate:

```text
1 + (300 / 100)
= 1 + 3
= 4.0
```

Return:

```text
4.0
```

Assignment:

```text
decimal_b = 4.0
```

### STATE

```text
odds_a    = 200.0
odds_b    = 300.0
decimal_a = 3.0
decimal_b = 4.0
```

---

# 🎮 PROBABILITY

### MOVE 13

```python
probability_a = 1 / decimal_a
```

Substitute:

```text
1 / 3.0
```

Result:

```text
0.3333333333...
```

Assignment:

```text
probability_a = 0.3333333333...
```

---

### MOVE 14

```python
probability_b = 1 / decimal_b
```

Substitute:

```text
1 / 4.0
```

Result:

```text
0.25
```

Assignment:

```text
probability_b = 0.25
```

### STATE

```text
odds_a         = 200.0
odds_b         = 300.0
decimal_a      = 3.0
decimal_b      = 4.0
probability_a  = 0.333333...
probability_b  = 0.25
```

---

# 🎮 ARBITRAGE FUNCTION

### MOVE 15 — CALL

```python
arb = arb_index(decimal_a, decimal_b)
```

Substitute:

```python
arb_index(3.0, 4.0)
```

Enter function:

```text
decimal_odds_a = 3.0
decimal_odds_b = 4.0
```

---

### MOVE 16 — CALCULATE

Function contains:

```python
return (1 / decimal_odds_a) + (1 / decimal_odds_b)
```

Substitute:

```text
(1 / 3.0) + (1 / 4.0)
```

Calculate:

```text
0.333333... + 0.25
```

Result:

```text
0.583333...
```

---

### MOVE 17 — RETURN

Function returns:

```text
0.583333...
```

Back to:

```python
arb = arb_index(decimal_a, decimal_b)
```

Assignment:

```text
arb = 0.583333...
```

### FINAL STATE

```text
odds_a         = 200.0
odds_b         = 300.0

decimal_a      = 3.0
decimal_b      = 4.0

probability_a  = 0.333333...
probability_b  = 0.25

arb            = 0.583333...
```

---

# 🎮 DISPLAY

Now Python executes:

```python
print "Implied Probability A:", probability_a * 100, "%"
```

### MOVE 18

Take:

```text
probability_a
```

which is:

```text
0.333333...
```

Multiply:

```text
0.333333... × 100
```

Result:

```text
33.3333... 
```

Then print `%` as a literal piece of text.

Screen:

```text
Implied Probability A: 33.3333333333 %
```

Same process for B:

```text
0.25 × 100
= 25.0
```

Screen:

```text
Implied Probability B: 25.0 %
```

---

### MOVE 19 — ARBITRAGE PERCENTAGE

```python
arb * 100
```

Substitute:

```text
0.583333... × 100
```

Result:

```text
58.3333...
```

Screen:

```text
Arbitrage Percentage: 58.3333333333 %
```

---

### MOVE 20 — BOOLEAN TEST

Finally:

```python
arb < 1
```

Substitute:

```text
0.583333... < 1
```

Python evaluates the statement.

```text
TRUE
```

Screen:

```text
Arbitrage: True
```

---

# 🏁 GAME OVER

Final output:

```text
Implied Probability A: 33.3333333333 %
Implied Probability B: 25.0 %
Arbitrage Percentage: 58.3333333333 %
Arbitrage: True
```

And **this is the style I'll use when we're learning the code**: don't just tell you “the function converts the odds.” We'll literally track:

```text
CREATE
→ CALL
→ PASS ARGUMENT
→ ENTER FUNCTION
→ ASSIGN PARAMETER
→ CHECK CONDITION
→ CALCULATE
→ RETURN
→ ASSIGN RESULT
→ NEXT CALL
```

Because that's the actual execution story.
