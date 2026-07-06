# Autopsy 02 — Bernstein–Vazirani (1993)

## 1. The problem

Oracle access to f(x) = s·x mod 2 for a hidden s ∈ {0,1}ⁿ. **Find s.**
n bits of information hidden inside a linear structure.

Who cared: this comes from "Quantum Complexity Theory" (Bernstein & Vazirani,
STOC 1993) — the paper that *defined* BQP. They needed evidence separating BQP
from BPP; this problem is the building block, and its recursive version
(Recursive Fourier Sampling) gave the first superpolynomial oracle separation
against BPP. The problem served complexity theory, not applications — but this
time the separation survives randomness.

## 2. The classical wall

Each classical query f(x) returns ONE bit; s contains n bits. So n queries are
necessary — and n suffice (query the unit vectors e₁,...,eₙ; f(eᵢ) = sᵢ).
Unlike Deutsch–Jozsa, **randomization does not help**: the lower bound is
information-theoretic, Ω(n) even for bounded-error randomized algorithms.

Honest ledger across our first two autopsies:
- DJ: exponential separation, but **fragile** (dies vs randomized baseline).
- BV: only n vs 1 — polynomial — but **robust**.
- Big AND robust at once = Simon (1994), next session. That's the escalation
  that provoked Shor.

## 3. The primitive

**The circuit is IDENTICAL to Deutsch–Jozsa.** Same Hadamard sandwich, same
single phase-oracle call. Only the promise changed.

Why it works: (−1)^(s·x) is a *character* of the group Z₂ⁿ, and H^⊗n is the
Fourier transform over Z₂ⁿ. The Fourier transform of a character is a delta
function: after the sandwich, ALL amplitude sits on |s⟩. One measurement, all
n bits.

The general mechanism, named: **Fourier sampling.** A quantum computer can
prepare Σₓ f̂(x)... more precisely, measuring after H^⊗n samples y with
probability |ĝ(y)|² where g(x) = (−1)^f(x). Sampling from the Fourier spectrum
costs ONE query. Classically, one sample from |ĝ|² can cost exponentially many
evaluations of f. Problems whose answer is written in the *Fourier support*
are quantum-native.

## 4. The hardness evidence

Information-theoretic, unconditional, robust to randomness — the cleanest kind
of lower bound we will ever see, and also the reason it caps at n vs 1: counting
bits can never give more than a factor-n separation. To beat it you need the
answer hidden in a way where each classical query reveals *almost nothing*,
not just few bits (Simon's move).

## 5. The lesson — YOUR TURN

*(One paragraph, own words. Hints to react to: where exactly did the power come
from, given that the gates are identical to DJ's? What problem-shape wants
"answer = location of Fourier mass"? Z₂ⁿ is the baby group — what changes when
the group becomes Z_N? That question is Week 2.)*

## Exercises

### Code (make the tests green)

- [ ] Implement `bernstein_vazirani(oracle, n)` in `bernstein_vazirani.py`.
      `pytest predecessors/02-bernstein-vazirani` must pass.
      Honor system: exactly ONE `apply` of the oracle.

### Proof draft #0 (I attack this at the start of Session 2)

- [ ] Draft, below, the classical lower bound: (a) any deterministic algorithm
      needs ≥ n queries; (b) any randomized algorithm with success probability
      ≥ 2/3 needs Ω(n) queries. Make (b) rigorous — "each query gives one bit"
      is intuition, not a proof. (Routes: information-theoretic / counting over
      the 2ⁿ candidate secrets, or an adversary argument. Yao's principle is
      your friend for (b).)

### Proof draft (yours)

*(write here)*
