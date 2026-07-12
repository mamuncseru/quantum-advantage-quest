# USTC Jiuzhang — the boson-sampling line

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

The photonic arm of Jian-Wei Pan's USTC program (Chao-Yang Lu leading) —
sibling to the [Zuchongzhi](zuchongzhi.md) superconducting line, and named
for the ancient Chinese mathematical text *Jiuzhang Suanshu*. This is not a
computer program in the engineering sense: it is a **sampling-advantage
program**, iterating one experiment to ever-larger scales.

| Version | Year | Scale | Claim vs classical |
|---|---|---|---|
| Jiuzhang | 2020 | 76 photons | 10¹⁴× |
| Jiuzhang 2.0 | 2021 | 113 photons | 10²⁴× |
| Jiuzhang 3.0 | 2023 | 255 photons | 10⁴⁴× (Frontier-scaled) |
| Jiuzhang 4.0 | 2026 | 1,024 sources, 3,050 clicks | 10⁴²+ years for El Capitan |

## 2–3 · The machine

**Gaussian boson sampling** hardware at maximal scale
([pipeline figure on the Xanadu page](xanadu.md#3--how-gates-happen)):
squeezed-light sources into a huge interferometer, photon-number detection
at the far end. Jiuzhang 4.0: **1,024 squeezed inputs, an 8,176-mode hybrid
spatial–temporal interferometer, 92% source efficiency, 51% end-to-end
system efficiency**, task time 25 µs (Nature, May 2026). No qubits, no
gates, no programs — the interferometer *is* the computation
([analog caveat](metrics.md#1-qubit-count--the-vanity-metric)).

## 5 · The numbers

The efficiency figures are the scientifically serious core: loss is the
classical simulator's best friend, and 4.0's 51% system efficiency is a
direct, engineered rebuttal to the loss-exploiting attacks that hurt
versions 1–3. The photon-click record (3,050) is more than 10× version 3.0.

## 6 · Error correction status

Not applicable — and that is the deepest critique: a GBS machine has no
path to *becoming* anything else. It is a purpose-built classical-hardness
demonstration, not a step toward a programmable computer (contrast
[PsiQuantum](psiquantum.md), which is nothing *but* the path).

!!! danger "⚔ The skeptic's box"

    - **Every prior Jiuzhang margin was cut down.** Loss-exploiting tensor
      and matrix-product samplers (Bulmer et al., Oh et al., Pan-group
      classical work itself) repeatedly closed tens of orders of magnitude
      on versions 1–3. The 4.0 claim is precisely calibrated *against known
      attacks* — the unknown ones are what history recommends waiting for.
    - **Verification is impossible in principle at this size.** Nobody can
      check 3,050-photon samples; validation rests on spoof-discrimination
      tests against the attacks the authors thought of. This is the
      weakest epistemic position an advantage claim can occupy
      ([the special rules](metrics.md#7-advantage-claims--the-special-rules)) —
      which is exactly why this repository's own program demands
      classical-hardness *reductions* instead.
    - **"Faster than El Capitan by 10⁴² years" compares against brute
      force**, not against the smartest known approximate sampler run at
      matched fidelity — the comparison that actually matters and the one
      that shrank every predecessor's number.

## 7 · Roadmap & sources

Watch for: independent spoofing attempts against 4.0 (the next 18 months
will tell), and whether the program pivots toward programmability or
declares sampling victory and stops.

- [Jiuzhang 4.0 (CAS, May 2026)](https://english.cas.cn/newsroom/headlines/202605/t20260514_1159331.shtml)
- [Coverage](https://phys.org/news/2026-05-prototype-optical-quantum-technology.html)
- [GBS spoofing lineage (Oh et al.)](https://arxiv.org/abs/2306.03709)
