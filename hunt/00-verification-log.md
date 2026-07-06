# Verification log

Per quality gate 1: primary-source confirmation of every result the hunt
builds on. *Verified* = title/authors/abstract claims confirmed at arXiv;
*proof-level* = the human has re-derived the load-bearing statements.
Nothing ships in a paper of ours on less than proof-level.

| Paper | ID | Verified | Proof-level | Notes |
|---|---|---|---|---|
| Jordan, Shutty, Wootters, et al., *Optimization by DQI* | 2408.08292 **v5** (Oct 2025) | ✅ 2026-07-06, incl. pp. 1–8 read directly | ⬜ pending (human) | Semicircle law Eq. 6 extracted verbatim; validated against paper's own numbers in `code/advantage_window.py` tests |
| Rajakumar & Watson, *Gibbs sampling gives quantum advantage at constant T with O(1)-local H* | 2408.01516, Quantum 10, 1981 (2026) | ✅ 2026-07-06 | ⬜ pending | Claims exactly as the lit sweep stated |
| Bakshi & Tan, *Rapid mixing for high-T Gibbs states with arbitrary external fields* | 2604.08408 | ✅ 2026-07-06 | ⬜ pending | **Sweep framing corrected:** the paper proves (i) fields induce entanglement past $h \approx \beta^{-1}\log(1/\beta)$, (ii) a quasi-local Lindbladian mixes in $O(\log(n/\varepsilon))$ under arbitrary on-site fields, (iii) classical hardness for $\beta<1$ with sufficiently large fields. "Break the dequantizer" was a gloss — hardness is proven directly, and only for $\beta<1$. |
| Krajenbrink, Krawchuk, Rosmanis, Rosenkranz, *DQI beyond Hamming* | 2606.04843 | ✅ 2026-07-06 | ⬜ pending | **Sweep framing corrected:** the authors *explicitly disclaim* quantum advantage — a **covering-radius obstruction** means the semicircle bound gives no additive guarantee for the true optimum in rank metric. "Standing advantage" was wrong; this recasts candidate A1. |
| Schmidhuber, Lu, Shutty, Jordan, Poremba, Quek, *Hamiltonian DQI* | 2510.07913 | ✅ 2026-07-06 | ⬜ pending | Confirmed: Gibbs/optimization → decoding via coherent Bell measurements + symplectic Pauli representation; first non-abelian extension of Regev's reduction; efficient for commuting H (toric, Haah), conditional beyond |
| Shutty, Mandal, Ragavan, et al., *Optimization using locally-quantum decoders* | 2604.24633 | ✅ 2026-07-06 | ⬜ pending | Confirmed: quantum BP-style decoder beats classical BP on Gallager-ensemble max-k-XORSAT, but an **enhanced Prange recovers a precise tie** — no advantage. Defines the bar any A-ground claim must clear. |

## Facts extracted verbatim from 2408.08292v5 (pp. 1–8)

**The semicircle law (Eq. 6).** For max-LinSAT with $m$ constraints, per-constraint
random-satisfaction fraction $\mu = r/p$, and a poly-time decoder correcting
$\ell$ errors on $C^\perp = \{\mathbf d \in \mathbb F_p^m : B^T\mathbf d = 0\}$:

$$
\frac{\langle s\rangle}{m}
= \left( \sqrt{\frac{\ell}{m}\Big(1 - \frac{r}{p}\Big)}
       + \sqrt{\frac{r}{p}\Big(1 - \frac{\ell}{m}\Big)} \right)^{\!2}
\quad\text{if } \frac{r}{p} \le 1 - \frac{\ell}{m}, \qquad 1 \text{ otherwise.}
$$

**OPI (Def. 2.2).** $n < p-1$, $p$ prime, subsets $F_1,\dots,F_{p-1} \subset \mathbb F_p$:
find $Q \in \mathbb F_p[y]$, $\deg \le n-1$, maximizing $|\{y : Q(y) \in F_y\}|$.
$B$ = Vandermonde $\Rightarrow C^\perp$ = Reed–Solomon; Berlekamp–Massey decodes
to half distance $\Rightarrow$ substitute $\ell/m = n/2p$.

**Classical state of the art (their §11):** Prange achieves
$\tfrac12 + \tfrac{n}{2p}$ (at $r/p = 1/2$); only exponential methods beat it.
Benchmarks: at $n \simeq p/10$: Prange $0.55$ vs DQI $\tfrac12 + \sqrt{19}/20 \simeq 0.7179$.
At $n/p = 1/2$: Prange $0.75$ vs DQI $\tfrac12 + \sqrt3/4 \simeq 0.9330$
($\approx 10^8$ Toffoli, $9{\times}10^3$ logical qubits at $p = 521$).

**Honesty note in the paper itself:** no complexity-theoretic hardness result
matches the DQI parameter regime yet — the OPI advantage is
"superpolynomial over *known* classical algorithms." Also: on their tuned
max-XORSAT instance, a tailored classical heuristic (0.880) beats DQI+BP
(≥0.831). Both facts go into how we phrase everything.

## Corrections this log forced on our strategy

1. Candidate A1 is no longer "stress-test a standing advantage claim" — there
   is none. It is now "attack or circumvent the covering-radius obstruction."
2. Candidate C1's target regime must respect that Bakshi–Tan hardness lives at
   $\beta < 1$; the intermediate-$\beta$ seam is *ours to open*, not theirs.
