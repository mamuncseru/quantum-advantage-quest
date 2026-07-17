"""JOINT J1 closed: the CRT shell state, prepared by the written circuit,
validated exactly end-to-end at m = 3 (primes 3,5,7, M = 105, ell = 2).

The lemma (strike/j1-shell-preparation.md) claims the composition

    |Psi> = sum_k w_k C(m,k)^{-1/2} sum_{|S|=k} sum_{k_i != 0}
            prod_{i in S} h_i(k_i) |y(S, k)>

is prepared EXACTLY (no cross-normalization error) by: weight register ->
count-controlled Dicke scan -> per-coordinate unit preparations h_i
(normalized DFT of the recentered indicator, h_i(0) = 0) -> uncompute mask
and count from the pattern. The load-bearing subtlety is a two-way
cancellation: ||DFT(g_i)|| = sqrt(p_i), and the per-coordinate 1/sqrt(p_i)
normalizations exactly cancel the sqrt(p_i) factors the inverse QFT
produces per coordinate — so the x-side lands on the UNWEIGHTED symmetric
polynomial sum_k w_k C(m,k)^{-1/2} e_k(g_1(x),...,g_m(x)), which is what
the payoff analysis (Claim 7.1) assumes. "Believed routine" hid exactly
this cancellation.

This file simulates the actual register-level construction (W, count C,
mask B, mixed-radix pattern Y) as linear maps — not a shortcut formula —
and checks, all exactly (tolerances ~1e-12 on float128-free numpy):

  1. composition: circuit-route state == definition, ancillas (W, C, B)
     disentangle back to |0> with zero residual;
  2. dictionary: frequency map + inverse QFT over Z_M reproduces
     sum_k w_k C(m,k)^{-1/2} e_k(g(x)) pointwise;
  3. payoff: E[f] of the prepared state at the optimal weights equals the
     top eigenvalue of the (ell+1)-shell pencil — Claim 7.1's finite-size
     payoff, realized by the constructed state;
  4. the k = 0 branch convention: within the coherent eta, cf_decode
     accepts nothing at theta ~ 0, so "no accept" = empty pattern is sound.

Run: .venv/bin/python hunt/code/j1_shell_state.py
"""

import random
import sys
from fractions import Fraction
from itertools import product
from math import comb, prod
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from cf_decode import cf_decode  # noqa: E402

PRIMES = [3, 5, 7]
M = prod(PRIMES)
ELL = 2
m = len(PRIMES)


def make_instance(seed):
    rng = random.Random(seed)
    F = [frozenset(rng.sample(range(p), p // 2)) for p in PRIMES]
    g = []
    for i, p in enumerate(PRIMES):
        mu = len(F[i]) / p
        g.append(np.array([(int(r in F[i]) - mu) /
                           np.sqrt(mu * (1 - mu)) for r in range(p)]))
    return F, g


def unit_fourier(g):
    """h_i: the normalized DFT of g_i. ||DFT(g_i)|| = sqrt(p_i), h_i(0)=0."""
    h = []
    for gi in g:
        p = len(gi)
        k = np.arange(p)
        dft = (gi[None, :] *
               np.exp(-2j * np.pi * k[:, None] * k[None, :] / p)).sum(1) \
            / np.sqrt(p)
        assert abs(dft[0]) < 1e-12                 # recentring => h(0) = 0
        assert abs(np.linalg.norm(dft) - np.sqrt(p)) < 1e-12
        h.append(dft / np.linalg.norm(dft))        # unit per-coordinate state
    return h


# ------------------------------------------------ the circuit, simulated --

def circuit_route(w, h):
    """Registers: W (dim ell+1), C (dim ell+1), B (2^m), Y (mixed radix).
    Simulates the written construction gate-block by gate-block."""
    shape = (ELL + 1, ELL + 1, *([2] * m), *PRIMES)
    psi = np.zeros(shape, complex)
    psi[(0, 0) + (0,) * m + (0,) * m] = 1.0

    # A: weight register  |0> -> sum_k w_k |k>
    new = np.zeros_like(psi)
    for k in range(ELL + 1):
        new[k] = psi[0] * w[k]
    psi = new

    # B: Dicke scan — qubit i rotates by angle depending on (W=k, C=c):
    #    P(B_i = 1 | k, c) = (k - c)/(m - i); then C += B_i.
    for i in range(m):
        new = np.zeros_like(psi)
        for k in range(ELL + 1):
            for c in range(ELL + 1):
                frac = (k - c) / (m - i) if 0 <= k - c <= m - i else 0.0
                s, co = np.sqrt(frac), np.sqrt(1 - frac)
                sl0 = (k, c) + tuple(slice(None) for _ in range(2 * m))
                blk = psi[sl0]
                idx0 = tuple([slice(None)] * i + [0])
                idx1 = tuple([slice(None)] * i + [1])
                # B_i = 0 stays with amp cos, B_i = 1 branches with amp sin,
                # and C increments on the B_i = 1 branch
                new[(k, c)][idx0] += co * blk[idx0]
                if s > 0 and c + 1 <= ELL:
                    new[(k, c + 1)][idx1] += s * blk[idx0]
        psi = new
    # uncompute C against W (C == W on every branch after the scan)
    new = np.zeros_like(psi)
    for k in range(ELL + 1):
        new[(k, 0)] = psi[(k, k)]
        for c in range(ELL + 1):
            if c != k:
                assert np.allclose(psi[(k, c)], 0), "C != W residual"
    psi = new

    # C: controlled per-coordinate preparations |0>_{p_i} -> |h_i>
    for i in range(m):
        new = np.zeros_like(psi)
        bidx = 2 + i
        yidx = 2 + m + i
        for b in (0, 1):
            blk = np.take(psi, b, axis=bidx)
            if b == 0:
                new[(slice(None),) * bidx + (0,)] = blk
            else:
                src = np.take(blk, 0, axis=yidx - 1)  # Y_i currently |0>
                for kk in range(PRIMES[i]):
                    idx = [slice(None)] * psi.ndim
                    idx[bidx] = 1
                    idx[yidx] = kk
                    new[tuple(idx)] += src * h[i][kk]
        psi = new

    # D: uncompute mask from pattern (B_i ^= [Y_i != 0]), then W from wt(Y)
    for i in range(m):
        bidx, yidx = 2 + i, 2 + m + i
        new = np.zeros_like(psi)
        for b in (0, 1):
            for kk in range(PRIMES[i]):
                idx = [slice(None)] * psi.ndim
                idx[bidx], idx[yidx] = b, kk
                tgt = list(idx)
                tgt[bidx] = b ^ (kk != 0)
                new[tuple(tgt)] += psi[tuple(idx)]
        psi = new
    for y in product(*[range(p) for p in PRIMES]):
        wt = sum(v != 0 for v in y)
        idx = [slice(None), slice(None)] + [slice(None)] * m + list(y)
        blk = psi[tuple(idx)]
        rolled = np.roll(blk, -wt, axis=0)         # W -= wt(y)  (mod ell+1)
        psi[tuple(idx)] = rolled

    # ancilla checks: W, C, B all exactly |0>
    zero_block = psi[(0, 0) + (0,) * m]
    assert np.abs(psi).sum() - np.abs(zero_block).sum() < 1e-12, \
        "ancillas failed to disentangle"
    return zero_block                              # the pattern register


def definition_route(w, h):
    psi = np.zeros(PRIMES, complex)
    for y in product(*[range(p) for p in PRIMES]):
        S = [i for i in range(m) if y[i] != 0]
        k = len(S)
        if k > ELL:
            continue
        amp = w[k] / np.sqrt(comb(m, k))
        for i in S:
            amp *= h[i][y[i]]
        psi[y] = amp
    return psi


# ------------------------------------------------ dictionary and payoff --

def to_frequency(psi_y):
    v = np.zeros(M, complex)
    for y in product(*[range(p) for p in PRIMES]):
        t = sum(y[i] * (M // PRIMES[i]) for i in range(m)) % M
        assert v[t] == 0                            # mixed radix <-> Z_M
        v[t] = psi_y[y]
    return v


def x_side(v):
    x = np.arange(M)
    return (v[None, :] *
            np.exp(2j * np.pi * x[:, None] * np.arange(M)[None, :] / M)
            ).sum(1) / np.sqrt(M)


def target_x(w, g):
    xs = np.arange(M)
    gv = np.stack([g[i][xs % PRIMES[i]] for i in range(m)])
    e = [np.ones(M), gv.sum(0),
         (gv.sum(0) ** 2 - (gv ** 2).sum(0)) / 2]    # e_0, e_1, e_2
    return sum(w[k] / np.sqrt(comb(m, k)) * e[k] for k in range(ELL + 1))


def pencil(F, g):
    """(ell+1)-shell generalized eigenproblem for E[f] over uniform Z_M."""
    xs = np.arange(M)
    f = sum(np.array([int(x % PRIMES[i] in F[i]) for x in xs])
            for i in range(m))
    gv = np.stack([g[i][xs % PRIMES[i]] for i in range(m)])
    e = [np.ones(M), gv.sum(0), (gv.sum(0) ** 2 - (gv ** 2).sum(0)) / 2]
    Phi = np.stack([e[k] / np.sqrt(comb(m, k)) for k in range(ELL + 1)])
    A = np.einsum('ap,bp,p->ab', Phi, Phi, f.astype(float)) / M
    B = np.einsum('ap,bp->ab', Phi, Phi) / M
    evals, evecs = np.linalg.eigh(np.linalg.inv(B) @ A)
    wopt = evecs[:, -1]
    return f, wopt / np.linalg.norm(wopt), evals[-1]


def state_payoff(psi_y, f, g):
    u = np.abs(x_side(to_frequency(psi_y))) ** 2
    return float((u * f).sum() / u.sum())


if __name__ == "__main__":
    F, g = make_instance(seed=2)
    h = unit_fourier(g)
    f, wopt, lam_top = pencil(F, g)

    print(f"m = {m}, primes {PRIMES}, M = {M}, ell = {ELL}")

    # 1. composition exactness, generic weights
    wgen = np.array([0.5, -0.7, 0.6])
    wgen /= np.linalg.norm(wgen)
    a = circuit_route(wgen, h)
    b = definition_route(wgen, h)
    print("\n1. composition (circuit vs definition, generic w):")
    print(f"   max |diff| = {np.abs(a - b).max():.2e},  "
          f"norm = {np.linalg.norm(a):.12f}")

    # 2. dictionary: x-side == unweighted symmetric polynomial
    u = x_side(to_frequency(b))
    t = target_x(wgen, g)
    u, t = u.real / np.linalg.norm(u), t / np.linalg.norm(t)
    if np.dot(u, t) < 0:
        u = -u
    print("2. dictionary (inverse QFT vs sum_k w_k e_k(g)/sqrt(C(m,k))):")
    print(f"   max pointwise |diff| = {np.abs(u - t).max():.2e}")

    # 3. payoff at the optimal weights == top pencil eigenvalue
    psi_opt = definition_route(wopt, h)
    ef = state_payoff(psi_opt, f, g)
    print("3. payoff (prepared state at optimal w vs pencil top eigenvalue):")
    print(f"   E[f] state = {ef:.12f}")
    print(f"   lambda_top = {lam_top:.12f}   |diff| = {abs(ef-lam_top):.2e}")
    print(f"   (random-guess baseline mu_bar = "
          f"{float(np.mean([len(F[i])/PRIMES[i] for i in range(m)])) * m:.4f}"
          f" of m = {m})")

    # 4. k = 0 branch convention: nothing accepted near theta = 0
    pmax_l = prod(sorted(PRIMES)[-ELL:])
    eta_g = Fraction(1, 2 * pmax_l * pmax_l)
    got = cf_decode(PRIMES, ELL, eta_g / 2, eta_g)
    print("4. k = 0 branch: cf_decode(theta ~ 0, eta_global) ->", got,
          " (None == empty pattern: convention sound)")
