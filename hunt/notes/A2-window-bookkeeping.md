# A2 — Gate 1 closed: the Gaussian window costs nothing (exact numerics + lemma)

!!! success "2026-07-11 — the amplitude bookkeeping holds, and adds NO new constraint"

    The flagged-since-day-one risk (§4 of the [derivation note](A2-crt-opi-derivation.md),
    "the April-2024 LWE bug lived exactly here") is resolved: at the design
    point, the windowed and unwindowed DQI payoffs agree to
    **machine precision** ($3.3\times10^{-16}$) with **zero** decoder
    failure mass — computed exactly, no sampling, no simulator
    ([`code/windowed_payoff.py`](../code/windowed_payoff.py), 5 tests).
    Both stress tests break the agreement *exactly at the predicted
    thresholds*, so the validation has falsification power. Gate 2 (the
    classical inventory) is discharged below by a structural argument:
    the known noisy-CRT attacks are list *decoding*; CRT-OPI is large-list
    list *recovery*.

## What had to be shown

The windowed state $|\psi_W\rangle \propto \sum_x W(x)\,P(f(x))\,|x\rangle$
(Gaussian taper $W$, width $\sigma_x$) is prepared through Fourier-side
Gaussian bumps of width $\sigma_f = M/(2\pi\sigma_x)$ centered on the
CRT-sparse frequencies, erased by the CF decoder. Three worries:

1. the decoder must be correct on the Gaussian support (else the erase
   step leaves entangled garbage);
2. bumps at distinct sparse frequencies must not overlap (norm and
   coherence);
3. conditioning on the window must not spoil the payoff — $\mathbb{E}[f]$
   under $|W \cdot P(f)|^2$ must match the unwindowed semicircle value.

## The lemma (one $d_{\min}$ condition, three duties)

By Poisson summation, every window-induced correction is a Fourier
coefficient of $W^2$ at a *nonzero sparse frequency difference*:

- **norm/coherence** terms sit at $|t - t'|$ with $w(t), w(t') \le \ell$,
  so at $|t-t'| \ge d_{\min}(2\ell)$;
- **payoff cross-terms** ($f$ has weight-1 frequencies) sit at
  $|t - t' + \tau| \ge d_{\min}(2\ell+1)$;
- **decoder collisions** need another sparse $t''$ within the tail cut,
  excluded below $d_{\min}(2\ell)/2$.

A Gaussian of frequency width $\sigma_f$ suppresses all of these by
$\exp\!\big(-\Omega\big((d_{\min}(2\ell{+}1)/\sigma_f)^2\big)\big)$. So:

> **Lemma (windowed payoff).** If $C\,\sigma_f \sqrt{\log(m/\varepsilon)}
> \le d_{\min}(2\ell+1)$ and the Gaussian is truncated there, then the
> prepared state is $\varepsilon$-close to the ideal windowed state, and
> $\big|\mathbb{E}[f]_W - \mathbb{E}[f]\big| \le m\,\varepsilon'$ with
> $\varepsilon'$ superpolynomially small.

**And the κ-consistency check — the part that had to come out right:**
the smallest window the lemma supports has
$X \approx \sigma_x\,\mathrm{polylog} = \frac{M\,\mathrm{polylog}}{2\pi\sigma_f}
\gtrsim \frac{M}{d_{\min}(2\ell+1)} = P_{\max}(2\ell+1)$, i.e.
$\kappa \gtrsim (2\ell+1)/m \approx 2\ell/m$ — **precisely the
$\ell/m \lesssim \kappa/2$ boundary already imposed by unique decoding.**
The bookkeeping introduces no new constraint; the advantage window
$(\kappa^2/4,\, \kappa/2)$ stands as stated.

## Exact numerics (m = 7, primes 3…19, M = 4 849 845, ℓ = 1)

At $\ell = 1$ the state is $W(x)(w_0 + w_1 S(x))$ with $S$ the
standardized constraint sum — a function of the 7-bit constraint pattern —
so every expectation reduces to exact 128-bin histograms. Design point:
$\sigma_f = 17$, $\sigma_x \approx 45{,}405$, $\kappa_{\text{eff}} = 0.81$,
$\ell/m = 0.143 < \kappa/2$.

| quantity | value |
|---|---|
| $\mathbb{E}[f]/m$ unwindowed (exact) | 0.560047 |
| $\mathbb{E}[f]/m$ windowed (exact) | 0.560047 |
| difference | $3.3\times10^{-16}$ |
| random baseline $\bar\mu$ | 0.4318 |
| decoder failure mass (exact grid) | 0 |

**Stress, state side** ($\sigma_x$ shrunk; theory: breaks when
$3\sigma_f \sim d_{\min}(3) = 1155$, i.e. $\sigma_x \sim 2000$):

| $\sigma_x$ | $3\sigma_f$ | $\mathbb{E}_W - \mathbb{E}$ |
|---|---|---|
| 45 405 | 51 | $3\times10^{-16}$ |
| 2 000 | 1 158 ≈ $d_{\min}(3)$ | $8\times10^{-5}$ — first deviation, on cue |
| 200 | 11 580 | $-1\times10^{-2}$ |

**Stress, decoder side** (cut pushed toward $d_{\min}(2)/2 = 7507$):
failure mass $0$ at $6\sigma_f = 6000$, $4.8\times10^{-4}$ at $12\,000$,
$2.2\times10^{-2}$ at $18\,000$ — the wall is where the theorem says.

The thresholds were **measured, not fitted** — the deviation onset lands on
$d_{\min}(3)$ to three digits. That is the strongest kind of numerical
validation this program knows how to produce.

## Gate 2 — the classical inventory (discharged, with the reason)

The standing worry: the CF structure that unlocks the quantum decoder
might also unlock a classical attack on CRT-OPI. Inventory:

- [Bleichenbacher–Nguyen 2000](https://link.springer.com/chapter/10.1007/3-540-45539-6_4)
  (noisy CRT via lattices/SVP),
  [Shparlinski–Steinfeld](https://www.semanticscholar.org/paper/Noisy-Chinese-remaindering-in-the-Lee-norm-Shparlinski-Steinfeld/c6749be0c3695ff93258df7984b58dc9db97326d)
  (Lee-norm noisy CRT), and Boneh's CRT list decoding all solve: *given
  one received residue per modulus, find $x < X$ agreeing on enough
  moduli* — list **decoding**, input list size 1 per position.
- CRT-OPI at $\mu \approx 1/2$ asks for $x < X$ with
  $x \bmod p_i \in F_i$, $|F_i| \approx p_i/2$: list **recovery** with
  input lists of size $\sim p_i/2$. Guruswami–Sudan-type list recovery
  degrades with input list size and is vacuous at $\ell_{\text{in}} =
  \Theta(p)$; the [novelty check](A2-novelty-check.md) already found that
  large-list list recovery of CRT codes has **no classical literature at
  all** — the exact mirror of RS-OPI's believed hardness (which survives
  GS for the same reason).
- The CF decoder itself gives a classical algorithm only for the *Fourier
  side* problem (recover a sparse pattern near a **given** $\theta$);
  classically there is no known way to find high-payoff $\theta$'s
  without the quantum interference that concentrates amplitude on them.

**Conclusion:** best-known classical remains CRT-Prange
($\kappa + \mu(1-\kappa)$). Epistemic status = RS-OPI's, verbatim: no
complexity-theoretic hardness in the regime; pedigree by analogy and by
the absence of any attack surface in 25 years of noisy-CRT literature.
DQI's honesty note transfers word for word.

## Where A2 stands (the chain, end to end)

| link | status |
|---|---|
| window nonempty: $(\kappa^2/4, \kappa/2) \ne \emptyset$ | ✅ theorem (§7, $d_{\min}$) |
| efficient decoder on the whole window | ✅ CF (§10), exact tests |
| amplitude bookkeeping | ✅ this note: lemma + exact numerics, thresholds confirmed |
| classical baseline inventory | ✅ this note: list-recovery gap, Prange stands |
| state prep at general $\ell$ (Dicke-type over supports) | standard DQI machinery, same as Hamming — needs the write-up pass |
| hardness pedigree | inherited from OPI, honesty note verbatim |
| human proof-level verification | **deferred batch** (per directive) — §2–4, §10, this lemma |

**A2 is now an end-to-end algorithm candidate surviving its own
self-attacks** — the first in this program to clear a full chain. Next:
the ℓ>1 exact-numerics replication (mechanism is ℓ-generic; cheap on a
compute node), then the Phase-3 question: write the construction as a
theorem statement with all constants, and hand the classical-attack
surface to a fresh adversarial pass.
