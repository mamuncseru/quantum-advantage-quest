---
title: Home
hide:
  - navigation
---

# Quantum Advantage Quest

An open research notebook with one goal: a quantum algorithm whose advantage
holds up the way Shor's does, meaning a rigorous algorithm plus classical
hardness that rests on a well-studied assumption. The work is published as it
happens, and that includes the candidates that died.

<p class="qq-meta">Started 2026-07-02 · six-month plan, see the
<a href="ROADMAP/">roadmap</a> · last update 2026-08-07 ·
<a href="https://github.com/mamuncseru/quantum-advantage-quest">source on GitHub</a>, MIT licence</p>

## Where things stand

| Phase | Status |
|---|---|
| **1 · Study** the named algorithms | Written: 13 autopsies from Deutsch–Jozsa to quantum Gibbs sampling, plus two deep dives, each with tested code |
| **2 · Hunt** for candidates | 23 candidates opened on four grounds; 9 closed, killed or merged so far, each with its reason in the [ledger](hunt/ledger.md) |
| **3 · Strike** on the best candidate | Running since 2026-07-11, on CRT-DQI (below) |
| **4 · Write** the result | Not started |

### The lead candidate: CRT-DQI

[Decoded Quantum Interferometry](predecessors/11-dqi/notes.md) turns an
optimization problem into a decoding problem. Its one regime that classical
algorithms have not reclaimed, Optimal Polynomial Intersection, lives on
Reed–Solomon codes over a finite field. CRT-DQI moves that problem to the
integers: find $x < X$ that lands in as many target residue sets
$F_i \bmod p_i$ as possible. The decoder DQI needs then turns out to be the
continued-fraction algorithm.

- **Done:** the construction written as a theorem with explicit constants;
  every step checked numerically; one adversarial pass, which found a false
  proof step and repaired it without weakening the result.
- **Not done:** verification of the proofs by a human, which is the largest
  open item. There is also no complexity-theoretic hardness result.
  "Advantage" here means beating the best classical algorithm we and the
  literature could find, not a proof that none exists.

[The theorem](strike/crt-dqi-theorem.md) ·
[the attack on it](strike/adversarial-pass-1.md) ·
[the remaining lemma](strike/j1-shell-preparation.md)

### What has been ruled out

Negative results are treated as deliverables. The sharpest so far:

- **DQI beyond Hamming.** Among coordinate-decomposable metrics, Hamming is
  the only place a DQI advantage can live. The Lee metric and the Doob
  schemes both fail ([A3](hunt/A3-p-polynomial-schemes.md)).
- **Variational circuits.** Five unrelated trainability mechanisms each came
  with their own classical surrogate, and the sixth collapsed into the
  simulation oracle it relied on
  ([ground T](hunt/README.md#ground-t--trainable-circuits)).
- **Folklore, recomputed.** With matched outputs, HHL loses to conjugate
  gradients by $10^8$ to $10^{10}$ and there is no crossover
  ([autopsy 11](predecessors/10-hhl-tang/notes.md)). Grover on AES-128 needs
  11.5 million years even at one logical operation per iteration
  ([autopsy 06](predecessors/06-grover/notes.md)). On a plain Ising chain,
  qubitization beats Trotter at every chemically relevant precision
  ([autopsy 09](predecessors/08-hamiltonian-simulation/notes.md)).

## Where to start

| If you want to… | Read |
|---|---|
| learn how the known quantum algorithms were found | [The curriculum](curriculum/00-curriculum.md), then [autopsy 01](predecessors/01-deutsch-jozsa/notes.md) |
| brush up on Fourier analysis first | [Deep dive 00 · Fourier from scratch](study-deep-dive/00-fourier-primer/notes.md) |
| see which problem structures give quantum speedups | [The problem-shape catalog](frontier/problem-shapes.md) |
| follow the current research | [The CRT-DQI theorem](strike/crt-dqi-theorem.md), then the [candidate board](hunt/README.md#the-candidate-board) |
| judge a hardware claim | [Machines](machines/index.md), starting with [the gap](machines/gap.md) |

## How the work is done

Five rules, applied to our own results before anyone else's:

1. **Classical baselines get equal effort.** They are built and tuned as
   seriously as the quantum side.
2. **Hardness needs a mechanism**: algebraic, spectral or coding-theoretic
   evidence, never "we couldn't simulate it".
3. **Kill criteria are written down before the work starts.**
4. **Negative results are published** with the same care as positive ones.
5. **Every proof is attacked before it is believed.**

Every algorithm in the curriculum gets the same five-question autopsy: the
problem, the classical wall, the quantum primitive, the hardness evidence
(including what happened when classical algorithms fought back), and the
shape of problem the mechanism wants.

The numerics run on a small [hand-built statevector simulator](https://github.com/mamuncseru/quantum-advantage-quest/tree/main/qsim),
and every figure on the site is generated from the repository's code. Tests
pin the numbers quoted in the text, so a number cannot drift away from the
code that produced it.

<figure markdown="span">
  ![Order-finding interference spectrum](predecessors/04-shor/fig-spectrum.svg#only-light)
  ![Order-finding interference spectrum](predecessors/04-shor/fig-spectrum-dark.svg#only-dark)
  <figcaption>Shor's algorithm factoring 15 on the simulator: the order
  r = 4 appears as four interference peaks in a 9-qubit counting register
  (<a href="predecessors/04-shor/notes/">autopsy 04</a>).</figcaption>
</figure>

Sibling project: [HilbertBench](https://github.com/mamuncseru/hilbertbench),
diagnostics for quantum machine-learning experiments.
