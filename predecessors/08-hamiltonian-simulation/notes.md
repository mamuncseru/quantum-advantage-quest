# Autopsy 09 — Hamiltonian simulation: Trotter → LCU → qubitization

## 1. The problem

Given a local Hamiltonian H and time t, apply e^{-iHt}. **Feynman's original
1982 problem — the reason quantum computing exists.** The customer base is
real and enormous: chemistry, materials, nuclear/lattice physics.

## 2. The classical wall

Exact statevector: 2ⁿ. The serious walls are the structured classical
methods — and each has a *mechanism-based* failure mode:
- Tensor networks: cost ~ exp(entanglement); fail when entanglement grows
  linearly under quench dynamics (2D, long times).
- Quantum Monte Carlo: sign problem for fermions/frustration.
- Pauli-path/sparse methods: fail at low noise and high circuit "magic."

This is hardness with a mechanism, not "we couldn't simulate it" — the only
bucket of empirical advantage claims that survived 2024–2026 (per our
frontier sweep) lives here.

## 3. The primitive(s) — three generations

1. **Trotter (Lloyd 1996):** slice time; error from commutators.
   `trotter.py` measures the slopes: order 1 ~ n⁻¹, order 2 ~ n⁻². Simple,
   often best in practice; cost scales poorly in target error (poly(1/ε)).
2. **LCU (Berry–Childs–Cleve–Kothari–Somma):** write the evolution as a
   Linear Combination of Unitaries, implement with ancilla + amplitude
   amplification. First exponential improvement in 1/ε dependence.
3. **Qubitization (Low–Chuang):** block-encode H/α in a unitary; the walk
   operator W rotates each eigenspace by arccos(λ) — see the QSVT autopsy;
   optimal query complexity O(αt + log(1/ε)). The α (block-encoding
   normalization = how much of the unitary's "budget" H occupies) is now the
   whole game in applied work.

## 4. The hardness evidence

BQP-complete (simulating local H dynamics to 1/poly precision) — so generic
dequantization would collapse BQP to BPP: **the strongest hardness footing
any application area has.** The honest fine print: BQP-completeness is
worst-case; the instances chemists care about may still be classically easy
(and tensor-network people keep proving some are). The advantage frontier in
simulation is *instance-wise*, which is why baseline discipline (our rule 1)
decides everything there.

## 5. The lesson — YOUR TURN

*(Own words. Prompts: "quantum-native input" — the problem is ABOUT a
quantum object, so no classical access-model trick (à la Tang) can even be
formulated. Which of our hunting grounds inherits this immunity? What does
the α-normalization story say about where asymptotic optimality can still
lose to Trotter in practice?)*

## Exercises

- [ ] Run `trotter.py`; then prove the first-order error bound
      ||e^{-i(A+B)t} − (e^{-iAt/n}e^{-iBt/n})ⁿ|| ≤ t²||[A,B]||/2n (BCH truncation
      + telescoping; sketch in solutions).
- [ ] Second-order (Strang) symmetrization kills which BCH term, exactly?
- [ ] One paragraph: why does the sign problem (QMC) have no analogue for a
      quantum computer running the same instance?
