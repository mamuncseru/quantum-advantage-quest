# Autopsy 01 — Deutsch–Jozsa (1992)

## 1. The problem

Promise problem. Oracle access to f: {0,1}ⁿ → {0,1}, **promised** to be either
constant (same value everywhere) or balanced (each value on exactly half the
inputs). Decide which, minimizing oracle queries.

Who cared about this problem before quantum computing? **Nobody.** It was
reverse-engineered to fit the mechanism: Deutsch (1985) asked "can interference
compute something with provably fewer queries, even in principle?" and the
problem was constructed as a showcase. DJ is a solution in search of a problem —
knowing that is part of the lesson, not a dismissal.

## 2. The classical wall

- Deterministic exact: 2ⁿ⁻¹ + 1 queries in the worst case (you can see half the
  inputs agree and still not know).
- **Randomized:** O(1) queries for bounded error. Sample k random inputs; any
  disagreement ⇒ balanced; all-equal ⇒ constant, wrong with probability ≤ 2^-(k-1)
  under the promise.

So the "exponential separation" holds only against deterministic *exact*
computation. The wall is real but thin.

## 3. The primitive

Hadamard sandwich around one phase-oracle call:

    |0...0>  --H^n-->  uniform  --O_f-->  sum_x (-1)^f(x) |x> / 2^(n/2)  --H^n-->  measure

Amplitude of |0...0> at the end:  2⁻ⁿ Σₓ (−1)^f(x)  — the **mean** of (−1)^f.
Constant f ⇒ ±1 (certainty). Balanced f ⇒ exactly 0 (never observed).

Two ideas that outlive the algorithm:
- **Phase kickback** moves data into phases: |x⟩|−⟩ → (−1)^f(x)|x⟩|−⟩
  (see `qsim/test_qsim.py::test_phase_kickback_ties_the_two_oracle_forms`).
- H^⊗n is the **Fourier transform over Z₂ⁿ**; the |0...0⟩ amplitude is the
  Fourier coefficient of (−1)^f at frequency 0. One query, one *global*
  property of f. Superposition alone computes nothing readable; interference
  concentrating a global property onto a measurable state is the whole game.

## 4. The hardness evidence

Only vs. deterministic exact classical computation; the randomized baseline
collapses the gap to O(1) vs 1. **This is the field's founding weak-baseline
incident (1992)** — the first named quantum algorithm's advantage dies against
the right classical baseline. What genuinely survives: the exact/deterministic
separation, and — much more importantly — the mechanism.

Also pin the query-model fine print here, once and for all: the model charges
one unit per oracle call and nothing for having the oracle. A query separation
becomes a real-world separation only when the oracle can be *instantiated* by
an efficient circuit for a problem someone cares about. Shor instantiated;
most oracle results never do. (Our `phase_oracle` builds a dense 2ⁿ matrix —
exponential classical work the model doesn't count. Feel that.)

## 5. The lesson — YOUR TURN

*(One paragraph, your own words: what SHAPE of problem does this mechanism
want? What died against the randomized baseline, and what survived? This
paragraph becomes a Problem-Shape Catalog entry in week 5.)*

## Exercises

- [ ] Run `python predecessors/01-deutsch-jozsa/deutsch_jozsa.py`; read the code
      against section 3 until every line is obvious.
- [ ] The demo includes an f OUTSIDE the promise (AND of two bits, p₀ = 1/4).
      In one sentence: why is the promise load-bearing for the interference
      pattern, not just for interpreting the output?
- [ ] Write section 5.
