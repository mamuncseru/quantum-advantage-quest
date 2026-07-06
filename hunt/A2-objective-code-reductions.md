# A2 — New objective→code reductions *(primary candidate)*

**Pre-registered 2026-07-06.**

!!! success "Status update, same day — kill criterion 3 cleared"

    Novelty check complete ([full report](notes/A2-novelty-check.md)): **no
    collision** across all ~27 DQI papers, the citation graph of 2408.08292,
    and a grep of the DQI v5 LaTeX source (zero occurrences of "Chinese").
    The name "optimal residue intersection" is unclaimed. Nearest occupied
    point: Regev-reduction for DLOG in finite abelian groups (2605.03972) —
    still RS codes over fields. The technical map is in
    [the derivation note](notes/A2-crt-opi-derivation.md): the transplant
    reduces to Q(A2.1) (closest CRT-sparse integer = sparse rational
    approximation, the Fourier dual of GRS decoding) and Q(A2.2) (max-min
    Diophantine modulus design — the CRT-dual of MDS code design).

    Two pressure points the check surfaced, now part of the brief:
    **(i)** Kothari–O'Donnell–Wu (2510.07515) *dequantized* CLZ's SIS∞
    speedup — the one prior "over ℤ without field structure" claim in this
    family fell classically; our window step lives in that neighborhood and
    must be treated accordingly. **(ii)** Useful ingredient: GSS 2000
    already built the CRT analogue of the Koetter–Vardy soft decoder —
    exactly the object a soft-decoded CRT-DQI would consume. Also pinned:
    large-list list-recovery of CRT codes (our regime, $|F_i| \approx
    p_i/2$) has **no classical literature at all** — the exact mirror of
    OPI's believed hardness.

## The question

DQI converts any max-LinSAT objective into syndrome decoding of
$C^\perp = \{\mathbf d : B^T \mathbf d = 0\}$; every code family with an
efficient decoder is therefore a potential optimization advantage — *if* the
corresponding objective is natural and classically hard. The DQI team framed
the easy direction ("harvest the coding literature"). Our question aims past
it:

> **Which *natural problems* — not yet phrased as optimization-over-codes —
> have constraint structure whose dual is an efficiently decodable algebraic
> code?**

## Flagship sub-candidate: CRT-OPI (residue intersection)

Transplant OPI from polynomials to residues. **Problem (draft):** given
coprime moduli $p_1 < \dots < p_m$, a bound $X$, and subsets
$F_i \subset \mathbb{Z}_{p_i}$, find an integer $x < X$ maximizing
$|\{i : x \bmod p_i \in F_i\}|$ — *optimal residue intersection*, the
Chinese-remainder twin of noisy polynomial reconstruction.

Why this specific transplant:

- **The decoder exists.** Chinese Remainder codes have efficient unique- and
  list-decoders (Mandelbaum; Goldreich–Ron–Sudan 1999; Guruswami–Sahai–Sudan)
  — the exact ingredient DQI consumes.
- **The hardness pedigree exists.** Noisy CRT / CRT with errors underlies
  cryptographic constructions and attacks; the analogy to OPI's
  noisy-polynomial-reconstruction pedigree is structural, not cosmetic:
  RS codes : $\mathbb{F}_p[y]$ :: CRT codes : $\mathbb{Z}$.
- **Same asymmetry as OPI**: mixed-radix QFT over
  $\mathbb{Z}_{p_1}\times\cdots\times\mathbb{Z}_{p_m}$ is abelian and
  efficient; classical Prange-analogues should cap near
  $\mu + (1-\mu)\cdot\frac{\log X}{\sum_i \log p_i}$ (to be derived properly).

**The technical unknowns that decide it (in order):**

1. Does the DQI state-preparation architecture survive *mixed moduli*?
   (The Dicke-state layer and the weight measure change; number-theoretic
   "weight" on $\prod \mathbb{Z}_{p_i}$ is non-uniform. This is the hard,
   interesting step.)
2. Does the semicircle analysis transfer, and with which $\ell/m$? (CRT
   unique decoding radius has the amplitude-weighting subtlety — the
   Goldreich–Ron–Sudan radius is weight-dependent.)
3. Is there headroom over the natural Prange analogue *after* points 1–2 fix
   the actual achievable $\ell$?

## Systematic search behind the flagship

Enumerate (code family with poly decoder) × (dual objective), asking for
*naturalness* and *hardness pedigree* — candidates to work through: BCH duals
(sparse-exponent polynomial fits), Reed–Muller duals (low-degree multivariate
fits — check literature first, likely explored), Goppa duals (the McEliece
connection — hardness pedigree!), group-algebra codes (character-sum
objectives), lattice analogues (Construction-A bridges to Regev/CLZ).

## Pre-registration

- **Advantage currency:** superpolynomial vs best-known classical (DQI-tier),
  with the hardness-pedigree honesty note attached, exactly as the DQI paper
  itself phrases it.
- **Hardness mechanism:** algebraic structure + cryptographic pedigree of
  noisy CRT interpolation; explicit non-claim of complexity-theoretic proof.
- **Named classical baseline:** Prange-analogue for CRT codes (we derive and
  implement it FIRST, before any quantum analysis), plus lattice/Coppersmith
  attacks on noisy CRT (they exist in crypto literature — inventory them).
- **Access model:** input is an explicit list of moduli and sets — no state
  preparation assumptions; Tang test trivially passes.
- **Kill criteria (any one kills the flagship):**
    1. Step 1 fails structurally — no poly-time coherent uncomputation for
       CRT syndromes (deadline: 3 weeks of focused effort).
    2. The honest $\ell$ from step 2 puts the semicircle payoff at or below
       the Prange-analogue everywhere in parameter space.
    3. Literature search finds this done (check: Regev-reduction papers,
       CLZ follow-ups, DQI citations — first task).
- **Kill deliverable:** a boundary note explaining *which* structural feature
  of $\mathbb{Z}$ vs $\mathbb{F}_p[y]$ broke the transplant — that is a
  publishable observation about where DQI's magic lives.

## First actions

1. Literature sweep specifically for CRT/Regev/DQI intersections (nothing in
   the 2026-H1 sweep matches, but search *before* working).
2. Human: proof-level pass through DQI §5 (OPI reduction) — the template to
   transplant.
3. Derive the Prange-analogue satisfied fraction for CRT instances (classical
   baseline first, per rules).
4. Write the mixed-radix DQI state-preparation attempt; find where it breaks.
