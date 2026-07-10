# The Problem-Shape Catalog

The distillation of the Predecessors curriculum: which shapes of problem
structure map to which quantum mechanisms, what kills each, and what stands.
**This is the hunting weapon.** Drafted by the AI 2026-07-06; your job is to
argue with it, annotate it, and rewrite entries in your own words as you
finish each autopsy — a catalog you haven't fought with is someone else's.

## Shapes that work

| # | Problem shape | Mechanism | Exemplar | Separation | What kills / caps it |
|---|---|---|---|---|---|
| 1 | Global/aggregate property of f under a promise | Interference computes a Fourier coefficient | Deutsch–Jozsa | exp. vs *exact deterministic only* | randomized classical baseline (O(1)) |
| 2 | Answer = location of Fourier mass (hidden linear structure) | Fourier sampling over $\mathbb{Z}_2^n$ | Bernstein–Vazirani | n vs 1, robust | information bound caps at factor n |
| 3 | Hidden coset/period structure, each query near-worthless classically | Fourier sampling + classical algebra | Simon | exponential + robust (oracle) | needs instantiation to matter |
| 4 | Shape 3 with an **efficiently computable f over an abelian group** | QFT + phase estimation + continued fractions | **Shor** | superpoly, Tier-2 hardness (50 yr of number theory) | none known in 30 years |
| 5 | Unstructured search / mean estimation | Amplitude amplification/estimation | Grover, AE | quadratic, provably optimal (BBBV) | overhead eats it on hardware; never compounds |
| 6 | Graph traversal where classical drift fails but spectral dispersion sails | Quantum walk (ballistic vs diffusive) | Glued trees | exponential (oracle, non-Fourier!) | no instantiation found in 20 yr |
| 7 | Reversible Markov chain with gap δ | Szegedy quantization: δ → √δ | MNRS search | quadratic | same as 5 |
| 8 | Dynamics of a quantum system (quantum-native input) | Trotter / LCU / qubitization | Ham. simulation | BQP-complete (worst case) | instance-wise classical methods (TN, QMC, Pauli paths) |
| 9 | Polynomial transform of a block-encoded matrix | QSVT | (compiler for 4,5,8,11) | = degree × encoding advantage | dequantized iff encoding ≈ sampleable data |
| 10 | Objective whose Fourier spectrum lives on a **decodable code** | DQI: optimization → syndrome decoding | OPI (standing, 2026) | superpoly vs best known (Prange) | classical decoders catching up; killed on sparse/random codes; **needs a P-polynomial translation scheme — rare (see hunt finding below)** |
| 11 | Gibbs state of non-commuting local H, intermediate β | Lindbladian samplers (Davies → CKG) | Rajakumar–Watson hardness; Bakshi–Tan template | conditional (PH-style assumptions) | expanding "provably easy" atlas; no gap theorems yet |
| 12 | Learning/estimation with quantum memory across copies | entangled measurements | shadow tomography separations, Huang–Chen–Preskill | exponential *sample* complexity, provable | needs quantum data access — which is also its shield |

## Anti-shapes (the graveyard — do not enter)

- **No structure at all** → quadratic ceiling, theorem (BBBV, Aaronson–Ambainis).
- **Nonabelian hidden structure** (Sₙ, dihedral) → representation theory
  smears frequency across matrix blocks; 30 years, no exit. (But the
  graveyard IS a hardness assumption viewed from the other side — lattice
  crypto rests on it. Usable.)
- **Low-rank classical data behind a state-preparation assumption** →
  Tang's mirror: grant the baseline ℓ²-sampling access and the advantage
  evaporates. *Access-model symmetry is a law of nature for us.*
- **Random/sparse instances of code problems** → 2026's lesson: OGP/AMP +
  enhanced Prange reclaim everything unstructured; only algebraic structure
  (RS, AG, rank-metric codes) has survived contact with classical algorithms.
- **Obfuscation as hardness** ("we couldn't simulate it") → peaked circuits
  died in one GPU-hour (Apr 2026). Hardness needs a mechanism, not a shrug.

## The meta-patterns (argue with these)

1. **Named algorithm = old primitive + new problem + instantiable oracle.**
   (Shor: Simon's primitive + Miller's reduction + a^x mod N. DQI: Fourier
   sampling + a 60-year-old decoding toolbox + OPI.)
2. **Advantage survives where the input is quantum-native or the structure
   is algebraic**; it dies where the input is classical data (access models)
   or the instance is random (statistical-physics obstructions).
3. **The quantum side buys one global transform per query** (Fourier
   coefficient, spectral sample, syndrome); classical simulation pays per
   *value*. Every real separation in this table cashes exactly that check.
4. **The classical toolbox is a quantum resource**: decoders (DQI), lattice
   reduction?, list decoding?, belief propagation? — "which other classical
   algorithms can be run coherently on superpositions to quantum profit"
   is an underexplored generator of candidates. (This is meta-pattern 1
   read as a search directive.)

## The hunt-phase search directives (grounds A & C, from the 2026 sweep)

- A1: transplant DQI to a new structured metric/scheme (Gabidulin/rank
  metric done once, June 2026, classically un-stress-tested — run the
  enhanced-Prange playbook against it; publishable either way).
- A2: new objective→code reductions (which optimization problems have
  constraint-Fourier spectra landing on decodable algebraic codes?).
- C1: second instance of "break the dequantizer, keep the mixer"
  (Bakshi–Tan recipe; candidate knobs: quasi-periodic fields, weak
  non-commuting perturbations of hard commuting models).
- C2: mixing-time separation for a specific family (even conditional).
- A∩C: the HDQI boundary — which code Hamiltonians are decodable-hence-
  quantum-preparable but resist classical cluster dynamics. Least crowded.

## Hunt findings that sharpen this catalog (dated)

- **2026-07-07 — the DQI decoder must beat lattice geometry, not just exist.**
  Sparse recovery under *archimedean* (size) noise does not reduce to LLL:
  the modular kernel supplies short ℓ²-vectors that are ℓ⁰-dense
  non-solutions. RS escapes via Berlekamp–Massey (algebra), not lattices.
  ⇒ shape #10 needs an *algebraic* decoder; "it's a lattice problem" is not
  enough. (hunt/notes/A2-crt-opi-derivation.md §8)
- **2026-07-08 — DQI-beyond-Hamming is gated on a P-POLYNOMIAL TRANSLATION
  SCHEME, and these are rare.** Hamming ✅, rank ✅ (bilinear forms), Lee ❌
  for q≥5 (not even an association scheme — computed). The scheme axiom, not
  the decoder, is the *first* gate; the eigenvalues $2\cos(2\pi t/q)$ must
  form an arithmetic progression, true only for q≤4. ⇒ the "new metric ⇒ new
  advantage" program is far narrower than it looks; the live question is the
  classification of distance-regular Cayley graphs carrying hard objectives.
  (hunt/notes/AC-lee-metric-KILLED.md)
- **2026-07-08 (2) — the coordinate-decomposable classification is DONE:
  Hamming and Doob, nothing else.** Cartesian products of connected graphs
  are distance-regular iff Hamming $H(N,q)$ or Doob $D(m,n)$ (rederived,
  then found known: Song 1986 + Egawa 1981). The AP-eigenvalue test is
  necessary but NOT sufficient — the Clebsch graph passes it (eigenvalues
  5,1,−3, common difference 4) yet Clebsch□Clebsch fails $a_2=2a_1$. The
  binding gate is the intersection axiom. Consequence for shape #10: the
  only non-Hamming coordinate-decomposable DQI home is the Doob scheme —
  counting objective over pair predicates, decoder open.
  (hunt/notes/A3-product-theorem.md)
- **2026-07-08 (3) — the coordinate-decomposable branch is CLOSED: Hamming
  is the unique advantage home.** Doob-DQI resolved: new geometry, no new
  advantage. The semicircle (Eq 6) is *alphabet-independent*, and Doob's
  reachable density menu is a subset of $H(N,16)$'s ⇒ Doob's payoff is a
  subset of the Hamming family's; meanwhile its pair-predicate objective
  leaks conditional bias ($3/4$) that strengthens the classical baseline
  ($10/32 > 9/32$, exact). So Doob's advantage window $\le$ Hamming's. With
  Lee ($q\ge5$, not a scheme) and the product theorem, this closes shape
  #10's coordinate-decomposable branch entirely — a publishable negative
  boundary. (hunt/notes/A3-doob-resolved.md)
- **2026-07-09 — the "algebraic decoder" demand of the 07-07 finding is
  MET for CRT: the decoder is Euclid.** Sparse CRT patterns are smooth
  denominators of reduced fractions; continued fractions (= rational number
  reconstruction, the $\mathbb{Z}$-twin of Berlekamp–Massey's
  $\mathbb{F}_q[x]$ Euclid) decode them at the exact $d_{\min}$ radius, poly
  time, linear sparsity. Lesson for shape #10: when a decoding problem
  resists lattices, ask whether the structure is *multiplicative* — the
  $\ell^0\ne\ell^2$ obstruction dissolves in the right representation.
  (hunt/notes/A2-crt-opi-derivation.md §10)
