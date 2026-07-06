# Autopsy 06 — Grover (1996), amplitude amplification, and the BBBV ceiling

## 1. The problem

Find the marked item among N with oracle access. Real pedigree (search/SAT
as generic problems), but note what's missing: **structure**. That absence
is the theme of this autopsy.

## 2. The classical wall

Θ(N) queries, trivially — and that triviality is the point. Nothing to
exploit means nothing for interference to grab.

## 3. The primitive

**Amplitude amplification** (the algorithm's real content, generalized by
Brassard–Høyer–Mosca–Tapp 2000): the state stays in the 2D plane spanned by
|marked⟩ and |rest⟩; oracle + diffusion compose into a rotation by
2θ, θ = arcsin(√(k/N)). After ~(π/4)√(N/k) steps the state points at
|marked⟩. See `grover.py`: the circuit matches sin²((2k+1)θ) to 1e−10 —
and **overshooting makes it worse** (rotation passes the target; run the
demo). Not a "keep trying" method: a precisely timed one.

The other export: **amplitude estimation** — phase-estimate the rotation to
estimate k/N with quadratically fewer samples than classical Monte Carlo.
This is the workhorse inside most claimed "quadratic speedup" applications
(finance, counting, planted-inference Kikuchi methods — our ground B).

## 4. The hardness evidence — and the ceiling

**BBBV (1997), proved before Grover was discovered:** any quantum algorithm
needs Ω(√N) queries for unstructured search. So quadratic is *optimal* —
a ceiling, not a floor. Proof shape (hybrid argument — draft it, solutions
file has the skeleton): run the algorithm on the all-zero oracle; total
query "attention" Σ_t |α_{x,t}|² across T steps bounds, per item x, how much
the final state can change if x were marked; an adversary marks the least-
attended item; distinguishing needs T = Ω(√N).

Generalization (Aaronson–Ambainis 2009 line): for *any* problem invariant
under permuting inputs, quantum speedup is at most polynomial. **No
structure ⇒ no exponential advantage — this theorem is why our hunt lives
exclusively in structured territory.**

Practical fine print for the honest ledger: on hardware, quadratic speedups
are expected to be eaten by fault-tolerance overhead for any feasible
problem size (error-corrected cycle time vs classical clock speed). Grover
is a magnificent subroutine and a terrible flagship.

## 5. The lesson — YOUR TURN

*(Own words. Prompts: why is "the ceiling was proved before the algorithm
existed" the healthiest event in this whole curriculum? What does the
2D-rotation picture say about where Grover's power actually comes from —
and why that power can't compound?)*

## Exercises

- [ ] **Proof draft #3:** the BBBV lower bound via the hybrid argument.
      Draft before reading the sketch in `curriculum/solutions.md`.
- [ ] Run the demo; explain the overshoot number: for n=6, 2k_opt = 12
      iterations gives p ≈ what, and why? (Compute (2·12+1)·θ.)
- [ ] Amplitude estimation in one paragraph: how does phase estimation on
      the Grover rotation turn k/N into a readable phase?
