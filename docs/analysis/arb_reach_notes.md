

Our primitive is:

> **Vig-adjusted boundary = 95% − your side**
> **IDEAL = boundary − 5 percentage points = 90% − your side**

Imagine the board.

### Falcons–Packers

Current:

**ATL 31¢ / GB 70¢**

If you already own Atlanta:

```text
95 - 31 = 64%
64 - 5 = 59%
```

**IDEAL: GB 59%**

Current GB: **70%**
Target: **59%**

So GB needs to move **11 points** from where it is now. ([Polymarket][1])

---

### Bengals–Steelers

Current:

**CIN 63¢ / PIT 38¢**

If you own Cincinnati:

```text
95 - 63 = 32%
32 - 5 = 27%
```

**IDEAL: PIT 27%**

Current PIT: **38%**
Target: **27%**

That's an **11-point move**.

---

### Browns–Panthers

Current:

**CLE 43¢ / CAR 58¢**

If you own Cleveland:

```text
95 - 43 = 52%
52 - 5 = 47%
```

**IDEAL: CAR 47%**

Current CAR: **58%**
Target: **47%**

Again, **11 points**.

---

### Vikings–Buccaneers

Current:

**MIN 53¢ / TB 48¢**

If you own Minnesota:

```text
95 - 53 = 42%
42 - 5 = 37%
```

**IDEAL: TB 37%**

Current TB: **48%**
Target: **37%**

**11 points.** ([Polymarket][1])

---

### Cardinals–49ers

Current:

**ARI 22¢ / SF 79¢**

If you own Arizona:

```text
95 - 22 = 73%
73 - 5 = 68%
```

**IDEAL: SF 68%**

Current SF: **79%**
Target: **68%**

Again, **11 points**. ([Polymarket][1])

---

### Rams–Broncos

Current:

**LA 56¢ / DEN 45¢**

If you own LA:

```text
95 - 56 = 39%
39 - 5 = 34%
```

**IDEAL: DEN 34%**

Current DEN: **45¢**
Target: **34¢**

Again, **11 points**. ([Polymarket][1])

---

### Eagles–Bears

Current:

**PHI 68¢ / CHI 33¢**

If you own Philadelphia:

```text
95 - 68 = 27%
27 - 5 = 22%
```

**IDEAL: CHI 22%**

Current CHI: **33%**
Target: **22%**. ([Polymarket][1])

---

And **look at what just happened.**

Because we're doing:

**95 − A − 5**

the ideal is simply:

**90 − A**

So every one of these produces the same **11-point gap from the current opposing price** whenever the displayed pair is approximately 101% combined.

That's actually a useful sanity check for our primitive.

For example, Atlanta:

```text
ATL 31
GB  70
──────
   101
```

Our ideal:

```text
90 - 31 = 59
```

Distance:

```text
70 - 59 = 11
```

Vikings:

```text
MIN 53
TB  48
──────
   101

90 - 53 = 37

48 - 37 = 11
```

So **the primitive is behaving consistently against these current Polymarket moneylines.** ([Polymarket][1])

And that's exactly why this experiment is useful: **we're not trying to make `arb_reach` flexible yet. We're seeing whether the tiny piece of arithmetic we defined produces the target we expect from actual market numbers.**

One thing we will *not* bake in: calling that 5% a verified Polymarket fee. We're deliberately treating it as **our rudimentary vig assumption** for this experiment. The Polymarket page gives us the market prices; the economic fee mechanism is a separate question.

[1]: https://polymarket.com/sports/nfl?utm_source=chatgpt.com "NFL Odds & Predictions 2026 | Polymarket"
