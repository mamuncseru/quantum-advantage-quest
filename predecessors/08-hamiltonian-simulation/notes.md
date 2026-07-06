# Autopsy 09 — Hamiltonian simulation: Trotter → LCU → qubitization

*Feynman's original problem — the reason quantum computing exists.*

## 1. The problem

Given a local Hamiltonian $H$ and time $t$, apply $e^{-iHt}$. Proposed by
Feynman in 1982 as the founding use case, and the customer base is real and
enormous: chemistry, materials, nuclear and lattice physics.

## 2. The classical wall

Exact statevector costs $2^n$. The *serious* walls are the structured
classical methods — and each fails for a stated mechanism:

| Classical method | Mechanism of failure |
|---|---|
| Tensor networks | cost $\sim \exp(\text{entanglement})$; linear growth under 2D quench dynamics |
| Quantum Monte Carlo | sign problem (fermions, frustration) |
| Pauli-path / sparse methods | low noise and high circuit "magic" |

This is hardness with a mechanism, not "we couldn't simulate it" — and per
our 2026 frontier sweep, it is the only bucket of *empirical* advantage
claims that survived contact with classical algorithms.

## 3. The primitive — three generations

**1 · Trotter (Lloyd 1996).** Slice time; the error is commutator-sized:

$$
\Big\| e^{-i(A+B)t} - \big(e^{-iAt/n}\,e^{-iBt/n}\big)^n \Big\|
\;\le\; \frac{t^2\,\|[A,B]\|}{2n} ,
$$

and the symmetric (Strang) splitting cancels the first commutator term,
giving $O(t^3/n^2)$. We don't take this on faith:

<figure markdown="span">
  ![Measured Trotter error slopes](fig-slopes.svg#only-light)
  ![Measured Trotter error slopes](fig-slopes-dark.svg#only-dark)
  <figcaption>Measured on a 6-qubit transverse-field Ising chain: fitted
  slopes −1.0 and −2.0, exactly the commutator bounds. Simple, often best in
  practice; the weakness is poly(1/ε) cost in target error.</figcaption>
</figure>

**2 · LCU** (Berry–Childs–Cleve–Kothari–Somma). Write the evolution as a
Linear Combination of Unitaries, implement with ancillas + amplitude
amplification — the first exponential improvement in the $1/\varepsilon$
dependence.

**3 · Qubitization** (Low–Chuang). Block-encode $H/\alpha$ in a unitary; the
walk operator rotates each eigenspace by $\arccos(\lambda)$ (next autopsy),
achieving the optimal $O\big(\alpha t + \log(1/\varepsilon)\big)$. The
normalization $\alpha$ — how much of the unitary's budget $H$ occupies — is
now the whole game in applied work.

## 4. The hardness evidence

Simulating local-Hamiltonian dynamics to $1/\mathrm{poly}$ precision is
**BQP-complete** — generic dequantization would collapse BQP to BPP. That is
the strongest hardness footing any application area has.

!!! warning "The honest fine print"

    BQP-completeness is *worst-case*. The instances chemists care about may
    still be classically easy — and tensor-network people keep proving some
    are. The advantage frontier in simulation is **instance-wise**, which is
    why baseline discipline (Rule 1) decides everything here.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    "Quantum-native input": the problem is ABOUT a quantum object, so no
    classical access-model trick (à la Tang, Autopsy 11) can even be
    formulated. Which of our hunting grounds inherits this immunity? And
    where can asymptotic optimality (qubitization) still lose to Trotter in
    practice?

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/08-hamiltonian-simulation/trotter.py
    .venv/bin/pytest predecessors/08-hamiltonian-simulation -q
    ```

- [ ] Prove the first-order bound above (BCH truncation + telescoping;
      sketch in `curriculum/solutions.md`).
- [ ] The Strang splitting kills which BCH term, exactly?
- [ ] One paragraph: why does the sign problem (QMC's killer) have no
      analogue for a quantum computer running the same instance?
