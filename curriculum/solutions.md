# Solution sketches & self-attack checklists

Since the AI won't always be available to attack your drafts, this file is
the substitute protocol: **draft first, on paper, completely — only then
read the sketch, and grade your draft against the "common holes" list.**
A draft you check before finishing teaches you nothing.

---

## Proof draft #0 — BV classical lower bounds

**(a) Deterministic, ≥ n queries.** Adversary argument. Maintain the set S of
secrets consistent with answers so far (initially 2ⁿ). A query x with answer
bit b keeps {s : s·x = b}; the adversary answers to keep the larger half, so
|S| shrinks by at most 2× per query. After q < n queries |S| ≥ 2^(n−q) ≥ 2,
two consistent secrets remain, and the algorithm errs on one of them. ∎

**(b) Randomized, Ω(n).** Yao: fix the uniform distribution over s; it
suffices to bound deterministic algorithms' average success. After q queries
x₁..x_q, the posterior on s is uniform on an affine subspace of dimension
≥ n − q; the algorithm's output is correct with probability ≤ 2^(q−n).
Success ≥ 2/3 forces q ≥ n − log₂(3/2). ∎ (Sharper than Ω(n): n − O(1).)

*Common holes:* (i) treating "1 bit per query" as a proof rather than
deriving the subspace structure; (ii) forgetting the adversary must answer
*consistently* with some s; (iii) in (b), bounding only worst-case error
instead of distributional error (Yao needs the latter).

## Proof draft #1 — Simon classical lower bound Ω(2^(n/2))

Sketch (randomized, via Yao against uniform s ≠ 0): condition on the event
that no collision f(xᵢ) = f(xⱼ) has been seen among q queries. Distinct
queries with no collision are consistent with every s ∉ {xᵢ ⊕ xⱼ}, a set of
size ≥ 2ⁿ − 1 − C(q,2); the answers are exchangeable across those s, so the
posterior is near-uniform and P(output = s) ≤ (C(q,2) + 1)/(2ⁿ − 1 − C(q,2))
+ P(collision). P(collision) ≤ C(q,2)/(2ⁿ − 1) since for fixed (xᵢ, xⱼ) the
event s = xᵢ⊕xⱼ has probability ≤ 1/(2ⁿ−1). Success ≥ 2/3 needs
C(q,2) = Ω(2ⁿ), i.e. q = Ω(2^(n/2)). ∎

*Common holes:* (i) proving only the birthday bound for a *specific*
strategy (uniform querying) instead of all strategies; (ii) not handling
adaptive queries — fix by conditioning on the transcript; (iii) ignoring
that a no-collision transcript still leaks the *negative* information
s ∉ {xᵢ⊕xⱼ} (bound its size, as above, don't wave at it).

## Proof draft #2 — Miller reduction (factoring → order finding)

Given odd composite N (not a prime power), random a coprime to N with order
r: if r is even and x = a^(r/2) ≢ −1 (mod N), then x² ≡ 1, x ≢ ±1, so
N | (x−1)(x+1) while dividing neither factor; gcd(x±1, N) are nontrivial.
The counting step (the real content — don't skip it): by CRT over the prime
power factors of N, for random a the order's 2-adic valuation is "spread,"
and P(r even ∧ a^(r/2) ≢ −1) ≥ 1/2. Draft the CRT argument in full; check
against Nielsen–Chuang Thm A4.13.

*Common holes:* forgetting "prime power" and "even N" exclusions (both have
classical poly algorithms — the reduction needs them excluded); asserting
the ≥ 1/2 probability without the CRT/valuation argument.

## Proof draft #3 — BBBV Ω(√N)

Hybrid argument. Run algorithm A for T queries on the empty oracle; let
q_x = Σ_t |α_{x,t}|² be the total query mass on item x (Σ_x q_x = T... with
unit mass per step, Σ_x Σ_t |α_{x,t}|² = T). There exists x with
Σ_t |α_{x,t}| ≤ Σ over light items: pick x minimizing query mass, q_x ≤ T/N.
Switching the oracle to mark x changes the final state by at most
2 Σ_t |α_{x,t}| ≤ 2√(T · q_x) ≤ 2T/√N (Cauchy–Schwarz). Distinguishing
marked from empty needs constant trace distance ⇒ T = Ω(√N). ∎

*Common holes:* the Cauchy–Schwarz step (Σ|α_t| vs √(T Σ|α_t|²)) done
backwards; forgetting the perturbation must be tracked through subsequent
unitaries (it's fine — unitaries preserve the error norm; say so).

## Trotter first-order bound

‖e^{-i(A+B)δ} − e^{-iAδ}e^{-iBδ}‖ ≤ ‖[A,B]‖δ²/2 + O(δ³) by Taylor expansion;
telescoping over n steps (unitarity ⇒ errors add): total ≤ n·(t/n)²‖[A,B]‖/2
= t²‖[A,B]‖/2n. Strang symmetrization cancels the δ² commutator term,
leaving δ³ (nested commutators) ⇒ t³/n². Your slopes: −1.0, −2.0 measured.

## Session-1 code exercise — reference BV implementation

Only read after yours is green:

```python
def bernstein_vazirani(oracle, n):
    psi = zero_state(n)
    for q in range(n):
        psi = apply(psi, H, [q])
    psi = apply(psi, oracle, list(range(n)))
    for q in range(n):
        psi = apply(psi, H, [q])
    return sample(psi, shots=1)[0]   # all amplitude sits on |s>
```

## The standing self-attack checklist (apply to EVERY proof you write)

1. Where exactly is each hypothesis used? (Unused hypothesis = wrong proof
   or wrong theorem.)
2. Does the argument survive an adversarial instance? Construct one.
3. Randomized baselines: did you prove the bound against distributions or
   only against deterministic strategies?
4. Adaptivity: does your argument secretly assume non-adaptive queries?
5. Constants and logs: does the claimed separation survive them?
6. Access models: are the quantum and classical sides given symmetric power?
   (The Tang question — ask it of your own claims first.)
