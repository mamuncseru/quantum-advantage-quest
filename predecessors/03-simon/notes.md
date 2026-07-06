# Autopsy 03 — Simon (1994)

## 1. The problem

Oracle f: {0,1}ⁿ → {0,1}ⁿ, promised 2-to-1 with a hidden XOR mask:
f(x) = f(y) iff y = x ⊕ s. **Find s.**

Who cared: nobody, yet — like Deutsch–Jozsa it's a designed problem. But this
one was designed to fix DJ's fatal flaw: an exponential separation that
*survives randomness*. Simon's paper was initially rejected; one of its
referees was Peter Shor, who saw what it implied. Within months Shor had
replaced the group Z₂ⁿ with Z_N and factoring fell. **Simon's problem is the
most consequential "useless" problem in the history of computing.**

## 2. The classical wall

Any classical algorithm (randomized included) needs Ω(2^(n/2)) queries.
Intuition: values of f at distinct points look uniformly random until you hit
a *collision* f(x) = f(x⊕s) — and by the birthday bound you need ~2^(n/2)
samples to find one. Until a collision appears, everything you've seen is
consistent with exponentially many candidate s values — each query eliminates
almost nothing. **That is the design principle DJ lacked**: not "each query
gives few bits" (BV's wall, capped at factor n) but "each query gives almost
zero information about s until an exponentially rare event."

## 3. The primitive

Same Hadamard sandwich, one new register:

    |0>|0> --H^n on reg 1--> sum_x |x>|0> --O_f--> sum_x |x>|f(x)>
           --H^n on reg 1--> measure reg 1 -> y

The second register entangles each |x⟩ with its f-value; since f is constant
exactly on the cosets {x, x⊕s}, interference happens *within cosets*:
amplitude at y picks up (−1)^(x·y) + (−1)^((x⊕s)·y) = (−1)^(x·y)(1 + (−1)^(s·y)),
which vanishes unless **s·y = 0**. So each run returns a uniform sample from
the subspace orthogonal to s. Collect n−1 independent samples, solve the
linear system over GF(2) (see `simon.py`), read off s.

Note the escalation from BV: there the Fourier transform put all mass ON the
answer; here it puts mass on a random element of a subspace *determined by*
the answer, and classical post-processing (Gaussian elimination) finishes the
job. **Quantum samples + classical algebra** — remember this hybrid shape;
Shor has exactly the same architecture (quantum samples + continued fractions).

## 4. The hardness evidence

Unconditional in the query model: Ω(2^(n/2)) vs O(n) — exponential AND robust
to classical randomness. The catch, as always: it's an *oracle* separation.
To make it real you must instantiate a function that (a) provably hides a coset
structure and (b) is efficiently computable. Nobody has done it for Z₂ⁿ in a
way that matters — but doing it for Z_N is literally Shor's algorithm
(f(j) = a^j mod N hides the subgroup rZ). The oracle result was the blueprint;
the instantiation was the revolution.

## 5. The lesson — YOUR TURN

*(Own words. React to: what property of the PROBLEM made each query nearly
worthless classically but a full subspace-sample quantumly? Why did hiding the
structure in a promise about f — rather than in f's values — matter?)*

## Exercises

- [ ] Run `python predecessors/03-simon/simon.py`; read `simon()` against §3
      until the coset-interference step is obvious.
- [ ] **Proof draft #1 (the real one):** prove the classical Ω(2^(n/2)) lower
      bound. Sketch in `curriculum/solutions.md` — draft yours BEFORE reading;
      then attack your own draft against the holes listed there.
- [ ] One-paragraph answer: Simon needs n−1 *independent* samples. Why does
      coupon-collector-style dependence cost only O(n) expected samples, not
      more? (Each new sample is independent-uniform in the orthogonal subspace.)
- [ ] Write §5.
