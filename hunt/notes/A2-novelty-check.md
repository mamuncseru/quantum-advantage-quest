# A2 Novelty Check: CRT-OPI (DQI over Chinese Remainder codes)

**Date:** 2026-07-06. **Method:** WebSearch + arXiv API + Semantic Scholar citation graph of 2408.08292 + grep of the DQI v5 LaTeX source (downloaded from arXiv e-print) + pdftotext of the Guruswami–Sahai–Sudan paper. All arXiv IDs below were seen directly in search/API results; nothing is cited from memory unless marked **[background knowledge, unverified today]**. Statements marked **[our analysis]** are inferences made during this check, not literature findings.

---

## 1. Direct collisions — anyone did CRT-DQI?

**No. No direct collision found.** Evidence, in decreasing order of strength:

1. **Full-text arXiv sweep of "decoded quantum interferometry"** (~27 papers, Aug 2024 – Jun 2026). The generalization axes covered so far: extension/folded fields (2408.08292 itself), soft decoders / Koetter–Vardy for OPI and ISIS∞ (2411.12553; 2511.22691), algebraic-geometry / Hermitian codes ("HOPI", 2510.06603), rank-metric and translation association schemes (2606.04843), multivariate polynomials (2605.10666), quadratic constraints (2510.08061, author-flagged error), Hamiltonian/Pauli DQI (2510.07913, 2601.18773), kernelized DQI (2511.20016), circuits/benchmarks/software (2504.18334, 2510.10967, 2603.24441, 2605.16955), near-linear-time OPI (2601.15171). The fetch explicitly reported: **none** involve Chinese remainder, CRT codes, residue number systems, codes over the integers, or number fields.
2. **Citation graph of 2408.08292** (Semantic Scholar, 47 citing papers returned; may be incomplete — API capped/lagged). Only one paper flagged on keywords {Chinese remainder, CRT, residue, congruence, integers, Regev, lattice}: *Regev's reduction as a candidate quantum algorithm for the discrete logarithm problem in finite abelian groups* (2605.03972). Checked its abstract: it uses **Reed–Solomon codes over finite fields** (Cheng–Wan reduction); no Z_M / composite moduli / CRT-code structure. A second candidate, *Affine Filtering Measurements* (2606.07852), also checked: pure-state channel decoding of linear codes, no CRT.
3. **The DQI paper itself never targets CRT.** We downloaded the v5 LaTeX source and grepped: zero occurrences of "Chinese" in the body. The only CRT-adjacent artifact is bibliography entry BN00 (Bleichenbacher–Nguyen, "Noisy polynomial interpolation and noisy Chinese remaindering", EUROCRYPT 2000), cited purely as a **classical lattice attack** on the Naor–Pinkas noisy-polynomial-interpolation problem. Jordan et al. run BKZ experiments (their Fig. on `bleichenbacher_nguyen_success_rate_vs_p_same_sum1.pdf`) showing the BN attack works at p≈2^80, per-position list size r≤16, rate ≥0.88, but **fails in the OPI regime** (r≈p/2, rate ≈1/10, many optimal solutions → many spurious short vectors). CRT codes appear nowhere as a quantum target, and no "future work over Z" is suggested.
4. **Term check:** searches for "optimal residue intersection" returned zero hits — the name is unclaimed.
5. **arXiv API, "chinese remainder" + "quantum algorithm"** (50 most recent): CRT appears only as a *tool* — distributed exact HSP (2512.22959), QoPrime amplitude estimation (2012.03348, 2109.09685), residue arithmetic for quantum computers (quant-ph/9911050). No quantum algorithm *for* noisy Chinese remaindering / CRT-code decoding exists on arXiv as far as these searches reach.
6. **"Regev reduction" + "CRT code" / "Chinese remainder code":** empty of collisions. CRT surfaces in ring-LWE reductions (Lyubashevsky–Peikert–Regev, "clearing the ideal") as a classical bookkeeping tool, and as "modulus-splitting/CRT bookkeeping" in Yifan Zhang's coset-sampling note (2509.12341) on the Chen factoring-style lattice algorithm (eprint 2024/555, which contains a known unfixable bug **[background knowledge, unverified today]**). Never as the code being decoded.

**Empty searches are findings:** "optimal residue intersection" (0 hits); quantum + {"simultaneous congruences", "residue codes", "Chinese remainder codes"} decoding (0 quantum-algorithmic hits); NP-hardness of CRT-code decoding (0 hits); DQI + {CRT, residue, number field} (0 hits).

---

## 2. Adjacent work (CLZ lineage; Regev reductions over Z)

The "codes over Z / mixed coprime moduli" middle ground between DQI (F_p-linear codes) and CLZ (Z_q lattices) appears **unoccupied**. What exists around it:

- **CLZ (2108.11015)**, quantum filtering for S|LWE⟩ with known amplitudes. Follow-ups found: *LWE with Quantum Amplitudes* (2310.00644, Gaussian amplitudes, hardness + oblivious sampling); *The Quantum Decoding Problem* (2310.20651, TQC 2024); *Quantum Oblivious LWE Sampling* (Debris-Alazard–Fallahpour–Stehlé, STOC 2024); a quasi-polynomial algorithm for the **Extrapolated Dihedral Coset Problem over power-of-two moduli** (Springer proceedings chapter 978-3-032-01878-6_14, 2025/26) — moduli *structure* is exploited, but prime-power towers, not coprime CRT products.
- **Critical cautionary result:** *No exponential quantum speedup for SIS∞ anymore* (2510.07515, Kothari–O'Donnell–Wu): efficient **classical** algorithms for all SIS∞ / Constrained Integer Solution variants from CLZ. The one CLZ application that lived "over the integers without structure" has been dequantized.
- **DQI→Z contact point:** *Quantum advantage from soft decoders* (2411.12553) extended the Regev-reduction/DQI pipeline to **ISIS∞** — the closest anyone has come to "DQI over Z", and it is precisely the part hit by 2510.07515.
- **Regev reduction beyond fields:** 2605.03972 pushes Regev's reduction to DLOG in arbitrary finite abelian groups — the group is general, but the code is still Reed–Solomon over a field. Nobody has swapped in the CRT code, whose natural ambient group Z_N ≅ ∏ Z_{p_i} *is* a generic finite abelian group. **[our analysis]** This is the nearest occupied point in idea-space; a CRT-OPI paper would sit one step away from it.
- Related dequantization pressure on DQI generally: MaxCut instances (2509.19966), short-path (2604.12131), OGP obstruction for unstructured MAX-XOR-SAT (2509.14509), simulability at low PH levels (2509.14443), worst-case OPI beaten classically at high rate n/m ≥ 0.6225 (2604.09533), max-LINSAT inapproximability boundaries (2603.04540, 2606.13570).

---

## 3. Classical baseline inventory for noisy CRT

Setup (GSS notation): coprime p_1 < … < p_n, message space M = {0, …, ∏_{i≤k} p_i − 1}, encode m ↦ (m mod p_1, …, m mod p_n). "Agreement" t = #{i : r_i = m mod p_i}.

| Algorithm | Regime handled efficiently (poly time) | Source |
|---|---|---|
| Mandelbaum | unique decoding ~(n−k)/2 errors; degrades badly when primes vary in size | cited in GSS |
| Goldreich–Ron–Sudan (STOC'99; eprint 1999/002) | list decoding for t ≥ sqrt(2kn·log p_n/log p_1) | GSS, verified |
| Boneh (JCSS 64(4):768–784, 2002; "Finding smooth integers… CRT decoding") | t ≥ sqrt(kn·log p_n/log p_1) | GSS, verified |
| Guruswami–Sahai–Sudan (c. 2000) | **soft-decision/weighted** decoding; uniform list decoding for t ≥ sqrt(k(n+ε)), any ε>0 — the Johnson-style frontier, log p_n/log p_1 factor removed; also GMD unique decoding at agreement ≥ (n+k+1)/2 | pdftotext of paper, verified |
| Bleichenbacher–Nguyen (EUROCRYPT 2000) | lattice (SVP/CVP) attacks on noisy CRT with **small per-position lists** and high rate; DQI-paper experiments: fails for balanced lists r≈p/2, rate ≈1/10 | BN00 + DQI §9 experiments |
| Shparlinski–Steinfeld (J. Complexity 20 (2004) 423–437) | additive noise **small in Lee norm** (i.e., residues near-correct as integers) → poly-time lattice recovery; companion: multiplicative noise (ToCS, DOI 10.1007/s00224-005-1272-9) | verified |
| Recent classical activity | interleaved CRT codes via LLL (probabilistic analyses); *Simultaneous Rational Number Codes* beyond half min distance (2504.08472); rational function analogue (2508.05284) | search results |

**Where the classical frontier leaves a gap [our analysis]:** all of the above solve *decoding* (one received residue word, possibly weighted). CRT-OPI as posed is **list recovery with huge input lists** |F_i| ≈ p_i/2 — the exact CRT analogue of OPI's r≈p/2 regime. We found **no classical literature at all** on list recovery of CRT codes with large lists (the closest, 2512.08017, is list recovery of subspace-design codes over fields). The efficient regimes to respect as baselines: (a) agreement above sqrt(k·n) → GSS decodes; (b) F_i = intervals or any Lee-ball structure → Shparlinski–Steinfeld lattices win; (c) small |F_i| + high rate → BN lattices win. A quantum-advantage window must sit below the Johnson-type bound with balanced unstructured F_i and low rate — the mirror image of where Jordan et al. parked OPI.

---

## 4. Hardness pedigree of noisy CRT

Thinner than noisy polynomial interpolation, and reduction-free, but real:

- **Algorithmic stuckness:** the GRS → Boneh → GSS agreement bound has been parked at ~sqrt(kn) since 2000 — the same 25-year stuckness grade that OPI's hardness argument rests on for RS list recovery.
- **BN dictum:** Bleichenbacher–Nguyen note most noisy CRT problems convert to noisy polynomial / lattice problems; their attacks define the easy regimes (small lists, structured noise), not a general break.
- **Crypto constructions assuming CRT-with-noise hardness:** batch FHE over the integers via the **CCK-ACD / CRT-ACD** assumption (Cheon et al.); attacked in some parameter regimes by orthogonal-lattice + simultaneous-Diophantine methods (Cheon–Cho–Hhan–Kang–Kim–Lee, eprint 2019/195, J. Math. Cryptol. 14(1) 2020) — hard for proper parameters, broken given the CLT-style auxiliary input. **CLT13 multilinear maps** (Coron–Lepoint–Tibouchi 2013) are CRT+noise based and were broken by Cheon–Han–Lee–Ryu–Stehlé zeroizing (eprint 2014/906; J. Cryptology 2018) — but the break exploits zero-testing leakage, **not** a generic noisy-CRT algorithm. Minor: collusion-secure fingerprinting codes via Chinese remaindering.
- **No worst-case anchor:** no NP-hardness or worst-case reduction for CRT-code decoding was found (searches empty). Contrast: RS bounded-distance decoding was recently proven NP-hard even at zero rate (2605.03972), and max-LINSAT inapproximability is now mapped (2603.04540, 2606.13570) — over fields. A CRT analogue of either would itself be a publishable byproduct. **[our analysis]**

---

## 5. Verdict

**CRT-OPI appears novel.** No CRT-DQI paper, no quantum noisy-CRT decoder, no "codes over Z" Regev reduction exists in anything we could find as of 2026-07-06; the DQI community has generalized along essentially every axis *except* the integers, and the problem name is unclaimed. The idea sits one step from two occupied points (2605.03972: Regev reduction over general abelian groups but with RS codes; 2411.12553/2510.07515: DQI-pipeline over Z_q but unstructured), which is where good problems live — and where races start.

**Strongest reason FOR:** the classical toolbox for CRT codes is a structural mirror of the RS toolbox (GRS↔Berlekamp–Welch/Sudan, GSS↔Koetter–Vardy soft decoding — GSS even builds the shared "ideal-theoretic" framework explicitly covering both), it stalls at the same sqrt(kn) Johnson-type frontier, and the large-list list-recovery regime that makes OPI classically untouched has **zero** classical literature on the CRT side. The soft-decision decoder DQI's pipeline needs (per 2411.12553) already exists for CRT codes — GSS built it in 2000.

**Strongest reason AGAINST:** CRT codes are **not linear** — the codeword set {(x mod p_i)_i : x < X} is the image of an *interval*, not a subgroup of Z_N ≅ ∏Z_{p_i} — so DQI's core mechanism (dual code via QFT over F_p^m, syndrome decoding, uniform-alphabet Dicke states, semicircle law) does not transplant as-is; mixed alphabet sizes additionally break the symmetric-subspace machinery. **[our analysis]** The natural fallback — QFT over Z_N with interval/indicator states and filtering — lands squarely in CLZ territory, whose flagship over-Z speedup (SIS∞) was just dequantized (2510.07515), and current dequantization pressure on DQI-adjacent claims (2509.19966, 2604.12131, 2604.09533) guarantees any CRT-OPI advantage claim gets stress-tested immediately. The first gate for this project should therefore be the linearity obstruction: either find the correct "dual object" for the CRT code under QFT_{Z_N}, or show the interval constraint can be absorbed CLZ-style — before any advantage claims.

**Caveats:** Semantic Scholar returned 47 citing papers, likely an undercount for a Nature-published result; Google Scholar was not directly enumerable. Non-English and very recent (last ~2 weeks) preprints may be missed. The GSS venue/year is cited from the conference PDF (c. 2000) without independent venue verification.
