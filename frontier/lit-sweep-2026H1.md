# Literature Sweep: 2026 H1 (with late-2025 context)
**Compiled:** 2026-07-02
**Scope:** Ground A (DQI / optimization-as-decoding), Ground C (quantum Gibbs sampling / Lindbladian algorithms), plus general 2026 quantum-advantage and dequantization developments.
**Method:** arXiv API queries (multiple search terms), web search cross-checks. Every paper below was found via an actual search or fetch during this sweep; arXiv IDs are as reported by the arXiv API feed or the paper's abs page. Where I only saw a search-result snippet rather than the full abstract page, I say so. Items are dated by arXiv submission month.

---

## Ground A — Decoded Quantum Interferometry (DQI) and optimization-as-decoding

### A.0 Anchor (pre-cutoff context)
- **Optimization by Decoded Quantum Interferometry** — Jordan, Shutty, Wootters, Zalcman, Schmidhuber, King, Isakov, Khattar, Babbush. arXiv:2408.08292 (v5). The foundational paper; published in Nature (2025). Reduces max-LinSAT to decoding; superpolynomial speedup claim for OPI (Optimal Polynomial Intersection, dual code = Reed–Solomon) over known polynomial-time classical algorithms (best classical heuristic on average-case OPI remains Prange-type, satisfaction ratio 1/2 + mu + o(1)).

### A.1 2026 papers

1. **A nearly linear-time Decoded Quantum Interferometry algorithm for the Optimal Polynomial Intersection problem** — Ansis Rosmanis. arXiv:2601.15171 (Jan 2026).
   Improves the DQI-for-OPI pipeline by sidestepping the quadratic-time Dicke state preparation, achieving a nearly linear-time quantum algorithm for OPI (with random input access). Together with the Khattar et al. circuit optimizations (below), this pushes the quantum side of the OPI advantage claim close to its asymptotic floor: classical hardness O(2^N) vs. Õ(N) quantum gates. This is an improvement to the *quantum* runtime, not a new advantage regime.
   **Assessment: THREAT** (to the direction "optimize DQI's runtime/circuits" — largely mined out now) but strengthens OPI as the flagship candidate.

2. **Hamiltonian Decoded Quantum Interferometry for General Pauli Hamiltonians** — Kaifeng Bu, Weichen Gu, Xiang Li. arXiv:2601.18773 (Jan 2026).
   Extends HDQI (see A.2.3) from commuting/structured cases to general Pauli Hamiltonians, using decoding oracles to prepare spectral-filtered states, with robustness guarantees under imperfect decoding. Broadens the reduction "energy filtering → decoding" beyond the original code-Hamiltonian setting.
   **Assessment: OPPORTUNITY** — the general-Pauli filtered-state framework is young; concrete Hamiltonian families where the induced decoding problem is quantumly easy but classically hard remain unidentified.

3. **Tight inapproximability of max-LINSAT and implications for decoded quantum interferometry** — Maximilian J. Kramer, Carsten Schubert, Jens Eisert. arXiv:2603.04540 (Mar 2026).
   Proves tight inapproximability bounds for max-LINSAT: any algorithm surpassing the r/q satisfaction fraction must exploit instance structure. This delineates, complexity-theoretically, where DQI-style advantage can even live: only on structured instances, and it quantifies the ceiling.
   **Assessment: OPPORTUNITY** (a map of where advantage is allowed) and simultaneously a **THREAT** to hopes of generic/unstructured advantage — consistent with the OGP result (A.2.5).

4. **Benchmarking Techniques for Decoded Quantum Interferometry** — Leon Bollmann, Maximilian Hess. arXiv:2603.24441 (Mar 2026).
   Benchmarking schemes for DQI on the Binary Paint Shop Problem, with quantum circuit implementations of greedy decoders for the LDPC codes arising from max-2-XORSAT. Engineering/benchmarking, not new advantage.
   **Assessment: neutral/OPPORTUNITY** (tooling for empirical comparisons).

5. **A Factorization Identity for Twisted Multinomial Coefficients with Application to Pilot States in Hamiltonian DQI** — Pawel Wocjan. arXiv:2604.01022 (Apr 2026).
   Combinatorial identity yielding exact matrix-product-state forms for HDQI pilot states. Technical enabler for HDQI implementations.
   **Assessment: neutral** (useful lemma; also a hint that some pilot states are MPS-like, i.e., classically representable — worth watching for simulability implications).

6. **On Worst-Case Optimal Polynomial Intersection** — Yihang Sun, Mary Wootters. arXiv:2604.09533 (Apr 2026).
   Shows that on worst-case OPI instances, strictly better solutions *exist* than what DQI's semicircle law achieves — "DQI and the semicircle law are not optimal" — via a connection to leakage in secret-sharing schemes. Important nuance: this is an *existential* result about solution quality, not an efficient classical algorithm; it does not dequantize OPI. Note Wootters is a coauthor of the original DQI paper.
   **Assessment: OPPORTUNITY** — headroom above DQI's semicircle bound exists; a better (quantum or classical) algorithm reaching it is an open target. Also a mild warning: DQI's output quality is not a fundamental barrier.

7. **Hidden Quantum Advantage near the Decoding Threshold of Decoded Quantum Interferometry** — Maoxin Gao, Yan Chang. arXiv:2604.15025 (Apr 2026).
   Replaces the uniform decoding-failure penalty in the DQI analysis with an eigenvector-weighted average penalty, strictly improving the provable performance bounds near the decoding threshold — i.e., DQI is somewhat better than the original analysis showed in the near-threshold regime.
   **Assessment: OPPORTUNITY** — sharper analyses can enlarge the certified advantage region without changing the algorithm; more slack likely remains.

8. **Super-Constant Weight Dicke States in Constant Depth Without Fanout** — Lucas Gretta, Meghal Gupta, Malvika Raj Joshi. arXiv:2604.15298 (Apr 2026).
   First QAC^0-type construction of super-constant-weight Dicke states in constant depth without full fanout; explicitly motivated by DQI state preparation.
   **Assessment: OPPORTUNITY** (circuit-depth primitives for DQI-like algorithms; also relevant to low-depth advantage proposals).

9. **Optimization Using Locally-Quantum Decoders** — Noah Shutty, Avijit Mandal, Seyoon Ragavan, Quentin Buzet, André Chailloux, Nicholas C. Rubin, Abid Khan, Sami Boulebnane, Ruslan Shaydulin, John Azariah, Stephen P. Jordan. arXiv:2604.24633 (Apr 2026).
   The DQI-team attempt to get advantage on D-regular max-k-XORSAT via *quantum* decoding of LDPC codes under coherent superpositions of bit-flip errors. Their quantum decoder beats classical Belief Propagation on Gallager-ensemble instances, and for some parameters beats Prange and simulated annealing — but they then find an *enhancement of Prange's algorithm that matches the quantum decoder*, so no quantum advantage survives (mirroring Chailloux–Tillich 2024). This is the most authoritative statement to date that the LDPC/max-k-XORSAT route to DQI advantage is (currently) closed: the quantum-vs-classical race on unstructured-ish sparse codes keeps ending in a tie.
   **Assessment: THREAT** — strongly closes "better decoders for sparse random codes" as an advantage route; redirects all pressure onto algebraically structured codes (RS, AG, Gabidulin).

10. **Quantum Decoding Algorithms: Quantum Speedups in Optimization** — Jan Ljubas, Tim Byrnes. arXiv:2605.00312 (May 2026).
    Self-contained review of DQI (Galois fields, coding theory, algorithmics, OPI). Useful onboarding text; no new results.
    **Assessment: neutral** (field consolidation signal — the area now has reviews).

11. **Multivariate Decoded Quantum Interferometry for Weighted Optimization** — Kaifeng Bu, Weichen Gu, Xiang Li. arXiv:2605.10666 (May 2026).
    Extends DQI to weighted max-LINSAT over prime fields by grouping constraints by weight; derives asymptotic expectation values and concentration (a weighted analogue of the semicircle law). Claims potential advantage over best known classical algorithms for certain weighted max-LINSAT problems (per abstract; advantage vs. strong classical baselines not independently established).
    **Assessment: OPPORTUNITY** — weighted/nonuniform constraint families are a genuinely new axis; classical baselines there are less studied, cutting both ways.

12. **From Constraint to Code: DQI-Kit — A Software Framework for DQI** — Simon Thelen, Wolfgang Mauerer. arXiv:2605.16955 (May 2026).
    Software framework auto-encoding constrained optimization into max-LINSAT for DQI, for practical advantage assessment.
    **Assessment: neutral** (tooling).

13. **Decoded Quantum Interferometry Beyond Hamming: Rank-Metric and Translation Association Schemes** — Alexandre Krajenbrink, Colin Krawchuk, Ansis Rosmanis, Matthias Rosenkranz. arXiv:2606.04843 (Jun 2026).
    Generalizes the DQI machinery from Hamming space to translation association schemes; instantiates in the rank metric with Gabidulin codes, giving an efficient protocol for a "find matrix with smallest rank difference" optimization problem. This is exactly the "new problem families reduced to decoding" extension pattern: new metric, new dual-code structure, new candidate problems whose classical complexity is much less charted than max-XORSAT.
    **Assessment: OPPORTUNITY (high)** — rank-metric optimization is fresh territory; classical attack literature there (rank-syndrome decoding) is thinner, and nobody has yet run the "enhanced-Prange catches up" playbook against it.

14. **Approximability limits for bounded-degree max-LINSAT and implications for DQI** — Maximilian J. Kramer, Carsten Schubert, Jens Eisert. arXiv:2606.13570 (Jun 2026).
    Companion/extension to #3: hardness-of-approximation for *bounded-degree* max-LINSAT over finite fields; concludes quantum advantage on bounded-degree instances is confined to constant prefactors (no asymptotic-ratio advantage possible there), and that quantum decoding is essential for matching the complexity-theoretic scaling.
    **Assessment: THREAT** to bounded-degree/sparse-instance advantage hopes; sharpens the message that advantage must come from dense, structured instances (OPI-like).

### A.2 Late-2025 context (post-cutoff-adjacent, needed to read 2026 correctly)

1. **Verifiable Quantum Advantage via Optimized DQI Circuits** — Khattar, Shutty, Gidney, Zalcman, Yosri, Maslov, Babbush, Jordan. arXiv:2510.10967 (Oct 2025).
   Establishes DQI-for-OPI as the first candidate for *verifiable* quantum advantage with optimal asymptotic speedup (classical hardness O(2^N) vs Õ(N) quantum gates) and gives concrete resource estimates (~5.72M Toffolis for a hard instance). This is the paper that turned OPI into the field's flagship near-term-ish target.
   **Assessment: OPPORTUNITY/THREAT mix** — validates the ground; but the flagship is now heavily staffed by Google-adjacent teams.

2. **Hamiltonian Decoded Quantum Interferometry** — Schmidhuber, Lu, Shutty, Jordan, Poremba, Quek. arXiv:2510.07913 (Oct 2025).
   Introduces HDQI: coherent Bell measurements reduce Gibbs-state preparation / spectral filtering of code Hamiltonians to *decoding*. This is the bridge between Ground A and Ground C — Gibbs sampling as a decoding problem.
   **Assessment: OPPORTUNITY (high)** — the A↔C bridge is new and underexplored (which Hamiltonian families give decodable-but-classically-hard filters?).

3. **Algebraic Geometry Codes and DQI** — Andi Gu, Stephen P. Jordan. arXiv:2510.06603 (Oct 2025).
   Extends DQI beyond Reed–Solomon to Hermitian (AG) codes: block length q^3 over F_{q^2}; quantum advantage claim for "Hermitian OPI" in substantial parameter regimes. Enlarges the structured-code family where the OPI-style story works.
   **Assessment: OPPORTUNITY** — the AG-codes direction (towers, other curves) is barely opened.

4. **OPI x Soft Decoders** — André Chailloux. arXiv:2511.22691 (Nov 2025).
   Reconciles the DQI and Chailloux–Tillich (arXiv:2411.12553, Koetter–Vardy soft decoding) approaches to OPI; simplifies analysis under Bernoulli noise and yields improved algorithms. Soft/list decoding strictly enlarges the OPI advantage region relative to hard-decision Berlekamp–Massey.
   **Assessment: OPPORTUNITY** — better decoders provably enlarge the advantage regime; the decoder-improvement axis is still productive for structured codes (unlike LDPC, per A.1.9).

5. **Decoded Quantum Interferometry Requires Structure** — Eric R. Anschuetz, David Gamarnik, Jonathan Z. Lu. arXiv:2509.14509 (Sep 2025).
   Proves DQI hits the overlap gap property (OGP) obstruction on unstructured MAX-k-XORSAT; classical approximate message passing (conjectured OGP-optimal) outperforms DQI on the relevant random ensembles. No quantum advantage from DQI on unstructured instances.
   **Assessment: THREAT** — with A.1.9 and A.1.14, decisively closes random/unstructured instances.

6. **On the Complexity of DQI** — Kunal Marwaha, Bill Fefferman, Alexandru Gheorghiu, Vojtech Havlicek. arXiv:2509.14443 (Sep 2025).
   Structural complexity analysis: DQI can be simulated at a low level of the polynomial hierarchy, while still resisting naive classical simulation (high-probability output location arguments). Tempers hopes of basing DQI advantage on PH-collapse-style hardness.
   **Assessment: mild THREAT** (weakens the strongest hardness stories one could tell for DQI outputs).

7. **No Quantum Advantage in DQI for MaxCut** — Ojas Parekh. arXiv:2509.19966 (Sep 2025).
   The MaxCut instances where DQI would beat classical guarantees are solvable exactly in classical poly time.
   **Assessment: THREAT** (closes MaxCut-via-DQI).

8. **Efficient and optimal quantum state discrimination via quantum belief propagation** — Christophe Piveteau, Joseph M. Renes. arXiv:2509.19441 (Sep 2025).
   Efficient *quantum* decoders for structured codes (incl. turbo codes) via quantum BP, aimed at boosting DQI's decodable-radius. A decoder-side tool for enlarging advantage regimes.
   **Assessment: OPPORTUNITY** — quantum-BP-decodable code families as new DQI substrates.

9. **Towards solving industrial integer linear programs with DQI** — Sabater et al. (BMW/BCG/Zapata-adjacent consortium). arXiv:2509.08328 (Sep 2025). Full DQI+BP pipeline on an automotive pricing ILP. **Assessment: neutral** (applications interest confirms commercial attention).

10. **Kernelized DQI** — Fumin Wang. arXiv:2511.20016 (Nov 2025). Adds spectral/kernel engineering to DQI circuits for noise robustness. Single-author, unreviewed; treat with caution. **Assessment: neutral.**

11. **DQI under noise** — Bu, Gu, Koh, Li. arXiv:2508.10725 (Aug 2025). Depolarizing noise degrades DQI solution quality exponentially in (inverse) sparsity; guidance on preserving advantage under noise. **Assessment: neutral/THREAT** for NISQ-ish DQI hopes; fault tolerance likely required.

### A.3 What has been reclaimed classically, and what stands (as of 2026-07-02)

- **Reclaimed / closed:** random and unstructured max-k-XORSAT (OGP + AMP, A.2.5); sparse/LDPC-code instances even with genuinely quantum decoders (enhanced Prange parity, A.1.9, following Chailloux–Tillich 2411.12553's earlier reclaiming of the original DQI max-XORSAT regime); MaxCut via DQI (A.2.7); any asymptotic-ratio advantage on bounded-degree max-LINSAT (A.1.14).
- **Still standing:** OPI / noisy polynomial reconstruction (Reed–Solomon duals) — my searches found **no 2026 classical algorithm or dequantization attacking the DQI-OPI regime**; the best classical remains Prange-type at 1/2 + mu + o(1), and per the Sun–Wootters paper the known Bleichenbacher–Nguyen-style lattice attacks on related noisy-interpolation problems do not appear effective against OPI. Hermitian/AG-code OPI (A.2.3) and rank-metric/Gabidulin problems (A.1.13) also stand, but are younger and less attacked. I searched explicitly for tensor-network or lattice attacks on OPI and found nothing — a genuine gap in the literature, not just in my search.

---

## Ground C — Quantum Gibbs sampling, Lindbladian/dissipative algorithms

### C.0 Anchors (pre-cutoff context)
- **Quantum Thermal State Preparation** — Chen, Kastoryano, Brandão, Gilyén. arXiv:2303.18224; and **An efficient and exact noncommutative quantum Gibbs sampler** — Chen, Kastoryano, Gilyén. arXiv:2311.09207. The CKG lineage: exactly-detailed-balanced, efficiently implementable Lindbladians for arbitrary noncommuting Hamiltonians. Now published as "Efficient quantum thermal simulation," **Nature 646, 561 (2025)** — a legitimization milestone for the whole program.
- **Slow Mixing of Quantum Gibbs Samplers** — Gamarnik, Kiani, Zlokapa. arXiv:2411.04300 (Nov 2024): bottleneck-lemma lower bounds; exponential mixing times for random K-SAT / spin glasses (limits on Gibbs-sampling-as-optimizer).
- **Optimal quantum algorithm for Gibbs state preparation** — Rouzé, Stilck França, Alhambra. arXiv:2411.04885, now published **PRL 136, 060601 (2026)**: high-temperature dissipative evolution mixes in O(log n).
- **Gibbs sampling gives quantum advantage at constant temperatures with O(1)-local Hamiltonians** — Joel Rajakumar, James D. Watson. arXiv:2408.01516 (v4, Jan 2026), published **Quantum 10, 1981 (22 Jan 2026)**. Proves (under standard hardness-of-sampling assumptions, e.g., non-collapse of PH) that sampling from Gibbs states of O(1)-local Hamiltonians — down to 5-local on a 3D lattice — at constant temperature is classically hard, while quantum Gibbs samplers prepare them efficiently; robust to imperfect measurements. This is currently the cleanest provable-advantage statement in Ground C.

### C.1 2026 papers

1. **Polynomial-time thermalization and Gibbs sampling from system-bath couplings** — Samuel Slezak, Matteo Scandi, Álvaro M. Alhambra, Daniel Stilck França, Cambyse Rouzé. arXiv:2601.16154 (Jan 2026).
   Proves poly-time convergence for *physically natural* thermalization models (repeated interactions, open-system Lindbladians) — high-temperature lattices, weakly interacting fermions, 1D spin chains. Narrows the gap between "algorithmic" CKG-style samplers and nature's own thermalization.
   **Assessment: OPPORTUNITY** — supports "nature thermalizes fast ⇒ quantum computers can too" arguments in regimes where classical simulation is not known to work; but also shows these easy regimes are *provably easy*, pushing advantage-hunting to intermediate temperatures.

2. **Efficient Shadow Tomography of Thermal States** — Chi-Fang Chen, András Gilyén. arXiv:2603.16845 (Mar 2026).
   O(log(M)/ε²) copies of a Gibbs state suffice to estimate M observables, by reinterpreting quantum Gibbs samplers as detailed-balance measurement channels. Extends the CKG toolkit from preparation to *measurement/learning*.
   **Assessment: OPPORTUNITY** — detailed-balance channels as a primitive for thermal-state learning tasks is a fresh interface; possible advantage statements in sample complexity rather than time.

3. **Thermal expectation estimation via single-trajectory Gibbs sampling with non-destructive measurements** — Hongrui Chen, Jiaqing Jiang, Bowen Li, Lexing Ying. arXiv:2603.21595 (Mar 2026).
   Extends single-trajectory (no re-mixing between samples) Gibbs sampling to arbitrary non-commuting observables via non-destructive measurements. Practical cost reduction for thermal averages.
   **Assessment: neutral/OPPORTUNITY** (efficiency, not new separations).

4. **Quantum Gibbs sampling through the detectability lemma** — Di Fang, Jianfeng Lu, Yu Tong, Chu Zhao. arXiv:2604.07214 (Apr 2026).
   Gibbs-state preparation avoiding full Lindbladian-simulation overhead, cutting cost by a factor O(M) (number of jump operators), and achieving quadratic improvement in spectral-gap dependence for local commuting Hamiltonians.
   **Assessment: OPPORTUNITY** — the "beyond-Lindbladian-simulation" implementation layer is actively improving; gap-dependence quadratics matter for end-to-end advantage claims.

5. **Rapid mixing for high-temperature Gibbs states with arbitrary external fields** — Ainesh Bakshi, Xinyu Tan. arXiv:2604.08408 (Apr 2026).
   Quasi-local detailed-balance Lindbladian mixing in O(log(n/ε)) for high-temperature Hamiltonians with *arbitrary* on-site fields. Crucially, also **proves** (under standard complexity assumptions) that for any β<1 there are local Hamiltonians with large fields whose computational-basis Gibbs sampling is classically hard — while the quantum sampler stays efficient, and the states are provably entangled above a field threshold h ≈ β⁻¹ log(1/β). This evades the Bakshi–Liu–Moitra–Tang (arXiv:2403.16850) dequantization, whose counting-to-sampling approach breaks once separability is lost.
   **Assessment: OPPORTUNITY (high)** — the sharpest new "efficient quantumly + provably hard classically + physically natural" package of 2026 H1 in this ground; the field-driven mechanism suggests a family of similar separations.

6. **Quantum Gibbs Sampling in Infinite Dimensions** — Simon Becker, Cambyse Rouzé, Robert Salzmann. arXiv:2604.01192 (Apr 2026); and **Computing the free energy of quantum Coulomb gases and molecules via quantum Gibbs sampling** — same authors, arXiv:2604.15263 (Apr 2026).
   Rigorous Gibbs-sampling framework for infinite-dimensional (bosonic/continuum) systems via Dirichlet forms, with quantitative trace-distance convergence; then first convergence proofs for Coulomb-interacting molecular systems and free-energy estimation.
   **Assessment: OPPORTUNITY** — continuum/chemistry Gibbs sampling with proofs is brand-new; classical baselines (and hardness) there are unmapped.

7. **Accelerating quantum Gibbs sampling without quantum walks** — Jiaqi Leng, Jiaqing Jiang, Lin Lin. arXiv:2604.22996 (Apr 2026).
   Walk-free algorithm achieving the quadratic improvement in spectral-gap dependence (previously the domain of quantum-walk/Szegedy constructions) via singular-value filtering and QSVT.
   **Assessment: OPPORTUNITY** — removes a major implementation obstruction to gap-quadratic speedups; relevant to any "quantum MCMC beats classical MCMC quadratically in the gap" claim.

8. **Localised Davies generators for unbounded operators** — Jeffrey Galkowski, Maciej Zworski. arXiv:2604.00306 (Mar 2026).
   Extends localized Davies-generator constructions to unbounded (pseudodifferential) operators. Mathematical infrastructure for continuum dissipative preparation.
   **Assessment: neutral** (enabling mathematics).

9. **Fast mixing of all-to-all quantum systems at high temperatures** — Thiago Bergamaschi. arXiv:2606.26090 (Jun 2026).
   Arbitrary k-local Hamiltonians with bounded-strength interactions (no geometric locality — includes all-to-all/mean-field models) admit quantum Gibbs samplers with system-size-independent spectral gap at high temperature.
   **Assessment: double-edged** — extends efficient quantum preparation to SYK-like/mean-field territory (OPPORTUNITY for applications), but high-temperature regimes are also where classical methods keep catching up; any advantage claim must sit *below* these provably-easy temperatures.

10. **Experimental Realization of the Markov Chain Monte Carlo Algorithm on a Quantum Computer** — arXiv:2603.08395 (Mar 2026; seen via search snippet only — authors not captured).
    Quantum-enhanced MCMC demonstrated on Quantinuum H2 and Helios hardware. Experimental milestone for "quantum MCMC," though the Layden-style quantum-enhanced MCMC speedup remains empirically bounded and not provably superquadratic (cf. arXiv:2403.03087).
    **Assessment: neutral** (hardware traction; no new provable separation).

11. **Dissipative Quantum Multiplicative Weights with Sampling Feedback** — Agung Trisetyarso, Lenny Putri Yulianti, Kridanto Surendro. arXiv:2606.26162 (Jun 2026).
    Claims an online-learning primitive using Davies-type dissipators preparing constant-temperature Gibbs states, with sublinear quantum regret vs. constant classical regret, hardness argued via PH non-collapse (leaning on Gibbs-sampling hardness results à la Rajakumar–Watson); IBM Heron r2 demo. Ambitious claims from a group outside the usual lineage; relies on a "realizability assumption." Not yet independently validated — flagging with caution.
    **Assessment: watch-list** — if sound, "dissipative samplers inside learning loops" is a novel advantage template; verify before building on it.

### C.2 Late-2025 context

1. **Fast Mixing of Quantum Spin Chains at All Temperatures** — Thiago Bergamaschi, Chi-Fang Chen. arXiv:2510.08533 (Oct 2025).
   Every 1D short-range Hamiltonian admits a Gibbs sampler with system-size-independent gap at *all* finite temperatures. Definitively makes 1D thermal states quantum-easy (and, combined with classical 1D methods, likely advantage-free).
   **Assessment: THREAT** to any 1D-based advantage hope; OPPORTUNITY as proof technique (localization of Lindbladians).

2. **Code Swendsen–Wang Dynamics** — Dominik Hangleiter, Nathan Ju, Umesh Vazirani. arXiv:2510.08446 (Oct 2025).
   Global-update Markov chain preparing Gibbs states of arbitrary code Hamiltonians; resolves the previously open 4D toric code case. Note: classical-style cluster dynamics adapted to codes — relevant both as quantum algorithm and as potential dequantizer of code-Hamiltonian Gibbs sampling (interacts with HDQI, A.2.2!).
   **Assessment: double-edged** — anyone reducing Gibbs sampling to decoding (HDQI) must now check whether code-Swendsen–Wang classically preempts their instances.

3. **Rapid Mixing of Quantum Gibbs Samplers for Weakly-Interacting Quantum Systems** — Štěpán Šmíd, Richard Meister, Mario Berta, Roberto Bondesan. arXiv:2510.04954 (Oct 2025).
   Rapid (polylog) mixing at *any* temperature for weakly interacting qudit, fermionic, and bosonic systems; exponentially faster than prior spectral-gap bounds for fermions, with explicit interaction-strength constants. First efficient bounds for non-commuting qudit and bosonic models at arbitrary temperature. (Companion to their Fermi–Hubbard result, arXiv:2501.01412, published Nature Communications 2025.)
   **Assessment: OPPORTUNITY for applications, THREAT for separations** — another provably-easy island (weak coupling, any T); advantage must live at intermediate coupling.

4. **Efficient quantum Gibbs sampling of stabilizer codes using hybrid computation** — Ivan H. C. Shum, Angela Capel. arXiv:2511.10839 (Nov 2025). Hybrid preparation of surface/toric-code Gibbs states in ~L/2 depth. **Assessment: neutral.**

5. **Rapid mixing for Gibbs states within a logical sector** — Bergamaschi, Gheissari, Liu. arXiv:2507.10976 (Jul 2025). Rapid mixing *within a logical sector* for self-correcting memories (4D toric code, polylog depth). **Assessment: OPPORTUNITY** (dynamical view of self-correction; ties Gibbs sampling to memory).

6. Also seen in searches, snippet-level only: **Lloyd & Abanin, "Quantum thermal state preparation for near-term quantum processors"** (arXiv:2506.21318, Jun 2025); **Hahn, Sweke, Deshpande, Shtanko, "Efficient Quantum Gibbs Sampling with Local Circuits"** (arXiv:2506.04321, Jun 2025 — provably efficient with dense local circuits, no block encodings); **"End-to-End Efficient Quantum Thermal and Ground State Preparation Made Simple"** (arXiv:2508.05703). All are implementation-layer simplifications of the CKG lineage.

### C.3 State of "provable quantum mixing-time advantage"

No unconditional quantum-vs-classical *mixing-time* separation was found in 2026 H1. What exists: (i) conditional sampling-hardness separations — Rajakumar–Watson (constant T, O(1)-local, published Jan 2026) and Bakshi–Tan (high T + strong fields, Apr 2026) — where the quantum sampler is provably fast and classical sampling is hard unless PH collapses; (ii) an expanding atlas of provably-fast quantum regimes (1D all T; weak coupling any T; high T with fields; all-to-all high T; random sparse Hamiltonians); (iii) slow-mixing lower bounds for Gibbs-sampling-as-optimizer on spin glasses (Gamarnik–Kiani–Zlokapa). The Layden-style quantum-enhanced MCMC line still lacks a provable superquadratic speedup, and arXiv:2403.03087 bounds it empirically. Searches for "provable quantum mixing time advantage 2026" style results came up thin beyond the above — stated explicitly per integrity rules.

---

## General 2026 developments

1. **Efficient Classical Simulation of Heuristic Peaked Quantum Circuits** — David Kremer, Nicolas Dupuis. arXiv:2604.21908 (Apr 2026).
   **Dequantization event.** The peaked-circuit quantum advantage demonstration of Gharibyan et al. (BlueQubit-style, following Aaronson's peaked-circuits proposal) is classically simulated near-exactly — MPO contraction exploiting the mirrored circuit structure with an "unswapping" trick — in ~1 hour on a single GPU, about half the quantum hardware runtime. Kills that specific claim and badly damages heuristically-obfuscated peaked circuits as a verifiable-advantage route.
   **Assessment: THREAT** to obfuscation-based verifiable advantage; strengthens the case for *structured* verifiable advantage (DQI-OPI style) instead.

2. **Google "Quantum Echoes" OTOC advantage (Willow)** — Nature, Oct 2025 (hardware result; found via press/blog coverage, not arXiv).
   First claimed *verifiable* hardware quantum advantage: second-order OTOCs on 65+ qubits, ~13,000× faster than best classical estimate (2.1 h quantum vs ~3.2 years/circuit on Frontier). Verifiable in the sense of a repeatable observable, not an interactive proof. Status as of mid-2026: **standing**. Supporting theory: **Tensor Networks with Belief Propagation Cannot Feasibly Simulate Google's Quantum Echoes Experiment** — Pablo Bermejo, Benjamin Villalonga, Brayden Ware, Guifre Vidal, Aaron Szasz. arXiv:2604.15427 (Apr 2026): the circuits are largely incompressible for TNBP and likely other Schrödinger-picture TN methods. No successful classical simulation found in my searches.
   **Assessment: context** — raises the bar for what "verifiable advantage" means experimentally; OTOC-observable estimation is a possible new ground (proof side open: no complexity-theoretic hardness known for these OTOCs).

3. **D-Wave vs. Flatiron tensor networks** (May 2026, press/company statements; no single arXiv ID captured).
   New Flatiron tensor-network work challenged D-Wave's 2025 "beyond-classical" quantum-simulation claim; D-Wave publicly disputes that the result is overturned. Unresolved as of this sweep.
   **Assessment: context** — analog/annealing advantage claims remain in the usual claim–rebut cycle.

4. **Quantum Advantage via Solving Multivariate Polynomials** — Pierre Briaud, Itai Dinur, Riddhi Ghosal, Aayush Jain, Paul Lou, Amit Sahai. arXiv:2509.07276 (Sep 2025).
   Extends the Yamakawa–Zhandry framework (not DQI) to *unrelativized* average-case NP search: poly-time quantum algorithm for underdetermined constant-degree (d≥3) multivariate systems over F_2, with classical hardness *conjectured* from cryptanalysis review. A second family, parallel to DQI-OPI, of "structured average-case search with quantum Fourier-side algorithms."
   **Assessment: OPPORTUNITY** — the YZ-style design space (choose distribution so quantum Fourier/decoding works; argue classical hardness from cryptanalysis) is where DQI-like discoveries are being made; cross-pollination with DQI machinery looks unexplored.

5. **Quantum speedups for MCMC with application to optimization** — arXiv:2504.03626 (Apr 2025, snippet-level); **A Quantum Algorithm for Random Number Generation** — arXiv:2606.13034 (Jun 2026, snippet-level): provable quadratic speedup over classical mixing for a card-shuffle-based generation task via Diaconis–Shahshahani analysis. Modest but *provable* quadratic-type separations in the MCMC orbit.
   **Assessment: neutral/OPPORTUNITY** — quadratic-in-mixing-time results continue to be provable where structure (group theory) is explicit.

6. **Shor's algorithm with as few as 10,000 reconfigurable atomic qubits** — arXiv:2603.28627 (Mar 2026, snippet-level). Resource-estimate compression for factoring on neutral atoms; continues the 2025 trend (Gidney's ~1M→sub-M qubit estimates) of collapsing fault-tolerant resource counts.
   **Assessment: context** — timeline compression for cryptanalytic advantage.

7. **Not found:** despite targeted searches, I found **no 2026 dequantization of DQI-OPI, no classical algorithm undermining the Rajakumar–Watson or Bakshi–Tan Gibbs-sampling hardness results, and no refutation of the CKG Gibbs-sampler lineage**. The major "kill" of 2026 H1 was peaked circuits (item 1). Searches for a headline-scale new exponential speedup in 2026 H1 outside grounds A/C came back thin: mostly consolidation, implementation, and the hardware claims above.

---

## Strategic implications (as of 2026-07-02)

**Ground A.** The map has clarified dramatically in nine months, mostly by elimination. Three independent lines — OGP obstructions (Anschuetz–Gamarnik–Lu), inapproximability ceilings (Kramer–Schubert–Eisert ×2), and the DQI team's own locally-quantum-decoders negative result — converge on one message: *no DQI advantage without algebraic structure*. Sparse, random, bounded-degree, LDPC-decodable: all closed, with classical Prange-enhancements repeatedly catching quantum decoders. What stands, unchallenged classically, is the structured-code family: OPI (Reed–Solomon), Hermitian/AG-code OPI, and now rank-metric/Gabidulin problems. For a small team, the flagship OPI-circuit-optimization race is effectively over (Google-adjacent teams + Rosmanis have driven it to near-linear time), but three adjacent seams look genuinely open: (i) *new structured metrics/schemes* — the rank-metric paper shows the DQI machinery transplants to any translation association scheme with a good decoder, and nobody has yet stress-tested the classical side there (running the "enhanced-Prange playbook" against Gabidulin-DQI is an obvious, publishable move in either direction); (ii) *the HDQI bridge* — which code Hamiltonians have spectral filters that are decodable quantumly but resist both classical decoding and code-Swendsen–Wang dynamics is a wide-open, well-posed question; (iii) *classical-side headroom* — Sun–Wootters proved better OPI solutions exist than DQI finds; whoever finds an efficient algorithm (quantum or classical) reaching them either extends or kills the flagship. Also note the parallel Yamakawa–Zhandry-style multivariate-polynomial family (Briaud et al.): the "pick a distribution where the quantum Fourier side is easy, argue classical hardness from cryptanalysis" recipe is the common generator of both families, and hybridizing it with DQI's decoding lens is untried.

**Ground C.** The CKG lineage has won institutionally (Nature publication, PRL, Quantum) and the 2026 activity is now a race to (a) simplify implementations (detectability-lemma, walk-free QSVT, local-circuit variants) and (b) chart the provably-easy atlas: 1D at all temperatures, weak coupling at all temperatures, high temperature with and without fields, all-to-all at high temperature, random sparse models. The strategic consequence is that *advantage lives in the shrinking middle*: intermediate temperature, intermediate coupling, geometrically frustrated or field-driven models. The best current template is Bakshi–Tan: find a physically natural knob (there, strong on-site fields at high temperature) that destroys separability — breaking the Bakshi–Liu–Moitra–Tang classical counting-to-sampling method — while leaving the quasi-local Lindbladian rapidly mixing, then prove conditional classical hardness. That mechanism ("break the dequantizer, keep the mixer") is repeatable and, per this sweep, has been executed exactly once. Candidate knobs no one has published on: quasi-periodic fields, weak non-commuting perturbations of classically-hard commuting models, and the logical-sector setting of Bergamaschi–Gheissari–Liu. Separately, Chen–Gilyén's thermal shadow tomography hints at *sample-complexity* separations for thermal-state learning — a different currency of advantage than mixing time, with far less competition.

**Cross-cutting.** The two grounds now physically touch at HDQI (Gibbs sampling reduced to decoding) and at code-Hamiltonian dynamics (Hangleiter–Ju–Vazirani), and this intersection is the least crowded high-value region found in this sweep: on one side a quantum reduction from thermal states to decoders, on the other a new classical cluster dynamics for exactly those Hamiltonians — nobody has yet delineated which side wins where. Meanwhile the general lesson of 2026 H1 is that obfuscation-based advantage (peaked circuits) died in an afternoon of MPO contraction, while structure-based claims (OPI, quantum echoes, constant-temperature Gibbs hardness) survived and hardened. For a small team hunting *provable* advantage, that argues for staking claims where the hardness story is a named, cryptanalyzed problem (rank-metric decoding, noisy polynomial reconstruction variants, PH-non-collapse sampling hardness) rather than where it is "we couldn't simulate it." The window that looks widest right now, weighting openness against required firepower: (1) classical cryptanalysis or extension of rank-metric/AG-code DQI, (2) a second instance of the Bakshi–Tan break-the-dequantizer mechanism, (3) the HDQI vs. code-Swendsen–Wang boundary.

---
*Search coverage notes: arXiv API full-text queries for "decoded quantum interferometry" (50 results), "optimal polynomial intersection" (30), "quantum Gibbs sampling/sampler" (40); web searches on classical attacks on DQI/OPI, Gibbs mixing times, quantum Metropolis/Davies 2026, dequantization 2026, quantum MCMC, and Google/D-Wave advantage claims. Thin spots flagged inline: items marked "snippet-level" were not verified against their abs pages; the D-Wave/Flatiron dispute and Google Nature paper were found via press coverage rather than arXiv. No relevant results were fabricated; absence claims (no OPI dequantization, no mixing-time separation) reflect explicit searches that returned nothing on point.*
