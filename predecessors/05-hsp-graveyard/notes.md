# Autopsy 05 — The Hidden Subgroup Problem, and where structure ends

## 1. The problem

Unify DJ, BV, Simon, Shor: given a group G and f: G → S constant exactly on
cosets of a hidden subgroup H ≤ G, find H. This is the **Hidden Subgroup
Problem (HSP)**. BV: G = Z₂ⁿ, H = {0, s}... rank-(n−1) variants; Simon:
G = Z₂ⁿ, H = {0, s}; Shor: G = Z (or Z_N), H = rZ; discrete log: G = Z_r × Z_r.

## 2. What's solved

**Every finitely generated abelian G**: Fourier sampling over G solves HSP
with polynomially many queries and efficient post-processing. The abelian
Fourier transform is efficiently implementable (Kitaev's phase estimation /
QFT circuits), characters are one-dimensional, and measurement statistics
identify H exactly as in Simon. This closed an entire continent in the
mid-1990s. Consequences: factoring, discrete log (all groups used in
classical crypto), Pell's equation (Hallgren), unit groups of number fields.

## 3. The graveyard

Two nonabelian targets carried enormous prizes, and neither has fallen in
thirty years:

- **Symmetric group Sₙ** — would solve graph isomorphism. Status: the quantum
  coset-state approach provably requires entangled measurements across
  Ω(n log n) coset states (Hallgren–Moore–Rötteler–Russell–Sen); no efficient
  such measurement is known. Effectively dead as an approach — and meanwhile
  Babai's classical quasipolynomial algorithm (2016) ate most of the prize.
- **Dihedral group D_N** — Regev showed dihedral HSP (with efficient coset
  sampling) would break lattice problems (unique-SVP), i.e. post-quantum
  cryptography. Best known: **Kuperberg's sieve**, subexponential
  2^O(√log N) — neither poly (which would be a revolution) nor stuck at
  exponential. Twenty years of effort has moved constants.

Cautionary tale, pinned: in April 2024 a well-known researcher posted a
claimed quantum poly-time algorithm for LWE (lattice crypto). It survived
**ten days** before a subtle bug in one step (a modular domain-extension of
a Gaussian-windowed QFT) was found. Even at proof level, self-attack before
belief — the whole field ran that protocol, and it worked as intended.

## 4. Why the wall is where it is

The abelian magic: characters are 1-dimensional, so Fourier sampling turns
coset structure into *phases*, and phases into measurable deltas. Nonabelian
representations are matrices: the "frequency" information is smeared across
representation *spaces*, single-copy measurements provably lose it, and the
required entangled measurements have no known efficient circuits. The
primitive didn't weaken — the problem's structure stopped matching it.
**Speedup ends where the group stops being abelian enough.** (Kuperberg's
subexponential sieve is exactly the price of "slightly nonabelian.")

## 5. The lesson — YOUR TURN

*(Own words. Prompts: what does this graveyard predict about "generalize the
primitive" research programs? Note that 30 years of dihedral-HSP failure is
also load-bearing EVIDENCE — the entire post-quantum lattice ecosystem rests
on it the way RSA rests on factoring. A graveyard is a hardness assumption
seen from the other side. Could OUR hunt use one that way?)*

## Exercises

- [ ] State precisely why Simon's post-processing (linear algebra over GF(2))
      is the abelian-character statement in disguise.
- [ ] No code for this autopsy. Instead: 30 minutes with Kuperberg's sieve
      (arXiv quant-ph/0302112, §2–3) — understand only the *shape*: combine
      coset states pairwise to cancel phase bits, a time/quantity trade.
      Where does the 2^O(√log N) come from, one sentence.
