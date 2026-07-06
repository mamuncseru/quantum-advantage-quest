# Solution sketches & self-attack checklists

!!! warning "Protocol"

    This file substitutes for a live adversary: **draft first, on paper,
    completely — only then read the sketch**, and grade your draft against
    the "common holes" list. A draft you check before finishing teaches you
    nothing.

---

## Proof draft #0 — BV classical lower bounds

**(a) Deterministic, $\ge n$ queries.** Adversary argument. Maintain the set
$S$ of secrets consistent with the answers so far (initially $|S| = 2^n$). A
query $x$ answered with bit $b$ keeps $\{s : s\cdot x = b\}$; the adversary
answers to keep the larger half, so $|S|$ shrinks by at most $2\times$ per
query. After $q < n$ queries $|S| \ge 2^{\,n-q} \ge 2$: two consistent
secrets remain, and the algorithm errs on one of them. $\blacksquare$

**(b) Randomized, $\Omega(n)$.** Yao's principle: fix the uniform
distribution over $s$ and bound deterministic algorithms' average success.
After $q$ queries the posterior on $s$ is uniform on an affine subspace of
dimension $\ge n - q$, so the output is correct with probability
$\le 2^{\,q-n}$. Success $\ge 2/3$ forces $q \ge n - \log_2(3/2)$.
$\blacksquare$ *(sharper than $\Omega(n)$: it's $n - O(1)$.)*

??? failure "Common holes"

    1. Treating "1 bit per query" as a proof rather than deriving the
       subspace structure.
    2. Forgetting the adversary must answer *consistently* with some $s$.
    3. In (b), bounding worst-case error instead of distributional error —
       Yao needs the latter.

## Proof draft #1 — Simon classical lower bound $\Omega(2^{n/2})$

Sketch (randomized, Yao against uniform $s \ne 0$): condition on seeing no
collision among $q$ (adaptive) queries. A no-collision transcript is
consistent with every $s \notin \{x_i \oplus x_j\}$ — at least
$2^n - 1 - \binom{q}{2}$ secrets — and the answers are exchangeable across
them, so

$$
P(\text{output} = s) \;\le\;
\frac{\binom{q}{2} + 1}{\,2^n - 1 - \binom{q}{2}\,} \; + \; P(\text{collision}),
\qquad
P(\text{collision}) \le \frac{\binom{q}{2}}{2^n - 1}.
$$

Success $\ge 2/3$ needs $\binom{q}{2} = \Omega(2^n)$, i.e.
$q = \Omega(2^{n/2})$. $\blacksquare$

??? failure "Common holes"

    1. Proving the birthday bound only for *uniform* querying instead of all
       strategies.
    2. Not handling adaptive queries — fix by conditioning on the transcript.
    3. Hand-waving away the *negative* information a no-collision transcript
       leaks ($s \notin \{x_i \oplus x_j\}$) — bound its size, as above.

## Proof draft #2 — Miller reduction (factoring → order finding)

Given odd composite $N$ (not a prime power) and random $a$ coprime to $N$
with order $r$: if $r$ is even and $x = a^{r/2} \not\equiv -1 \pmod N$, then
$x^2 \equiv 1$, $x \not\equiv \pm 1$, so $N \mid (x-1)(x+1)$ while dividing
neither factor; $\gcd(x \pm 1, N)$ are nontrivial. **The counting step is the
real content** — don't skip it: by CRT over the prime-power factors of $N$,
the 2-adic valuations of the per-factor orders are independent enough that

$$
P\big(r \text{ even} \;\wedge\; a^{r/2} \not\equiv -1\big) \;\ge\; \tfrac12 .
$$

Draft the CRT argument in full; check against Nielsen–Chuang Thm A4.13.

??? failure "Common holes"

    Forgetting the "odd" and "not a prime power" exclusions (both have
    classical poly algorithms — the reduction needs them excluded); asserting
    the $\ge 1/2$ probability without the valuation argument.

## Proof draft #3 — BBBV $\Omega(\sqrt N)$

Hybrid argument. Run algorithm $\mathcal{A}$ for $T$ steps on the empty
oracle; let $q_x = \sum_t |\alpha_{x,t}|^2$ be the total query mass on item
$x$, so $\sum_x q_x = T$. Some $x^\*$ has $q_{x^\*} \le T/N$. Switching the
oracle to mark $x^\*$ perturbs the final state by at most

$$
2 \sum_t |\alpha_{x^\*,t}|
\;\le\; 2\sqrt{T \cdot q_{x^\*}}
\;\le\; \frac{2T}{\sqrt N}
\qquad \text{(Cauchy–Schwarz)},
$$

and unitarity preserves the accumulated error norm through subsequent steps.
Distinguishing marked from empty needs constant trace distance
$\Rightarrow T = \Omega(\sqrt N)$. $\blacksquare$

??? failure "Common holes"

    The Cauchy–Schwarz step done backwards
    ($\sum_t |\alpha_t|$ vs $\sqrt{T \sum_t |\alpha_t|^2}$); forgetting to
    argue the perturbation survives subsequent unitaries (it does — say why).

## Trotter first-order bound

$\big\| e^{-i(A+B)\delta} - e^{-iA\delta} e^{-iB\delta} \big\|
\le \tfrac12 \|[A,B]\|\,\delta^2 + O(\delta^3)$ by Taylor expansion;
unitarity makes errors add across the $n$ slices (telescoping), so the total
is $\le \tfrac{t^2 \|[A,B]\|}{2n}$. Strang symmetrization cancels the
$\delta^2$ commutator term, leaving nested commutators at $\delta^3$
$\Rightarrow t^3/n^2$. Measured slopes in `predecessors/08`: $-1.0$, $-2.0$.

## Session-1 code exercise — reference BV implementation

??? example "Only open after your version is green"

    ```python
    def bernstein_vazirani(oracle, n):
        psi = zero_state(n)
        for q in range(n):
            psi = apply(psi, H, [q])
        psi = apply(psi, oracle, list(range(n)))
        for q in range(n):
            psi = apply(psi, H, [q])
        return sample(psi, shots=1)[0]   # all amplitude sits on |s⟩
    ```

## The standing self-attack checklist

Apply to EVERY proof you write — curriculum and hunt phase alike:

1. Where exactly is each hypothesis used? (An unused hypothesis means a wrong
   proof or a wrong theorem.)
2. Does the argument survive an adversarial instance? Construct one.
3. Randomized baselines: did you prove the bound against distributions, or
   only against deterministic strategies?
4. Adaptivity: does your argument secretly assume non-adaptive queries?
5. Constants and logs: does the claimed separation survive them?
6. **Access models: are the quantum and classical sides given symmetric
   power?** (The Tang question — ask it of your own claims first.)
