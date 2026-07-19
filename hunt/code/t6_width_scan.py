"""T6-2D width scan: does chi* grow with the cut? Plus the random-theta
baseline that separates dynamics-intrinsic from training-steered
hardness.

The 4x4 verdict left two owed measurements:
  (a) BASELINE: chi=128 errors at random controls on 4x4 — if they
      match the trained trajectory's, the 2D hardness is intrinsic to
      the dynamics (consistent with the BQP pedigree), and T6's
      contribution is the trainable landscape on top.
  (b) WIDTH: the same protocol on 4x5 (n = 20). PRE-REGISTERED:
      width-hardening fires if the chi ladder {64, 128, 256} fails at
      the heated endpoint (tol 0.0125 n = 0.25) — i.e. chi* strictly
      grows with the cut; the window closes back if chi <= 128 passes
      at 4x5 (no growth).

New machinery (n = 20 cannot materialize the (chi x 2^n) intermediate):
exact-MPS form of psi0 by sequential SVD, and <MPS|MPO|MPS> boundary
contraction. Gated at 2x3 (machine precision vs dense) and cross-armed
at 4x4 against the dense mpo_apply route.

Run: .venv/bin/python hunt/code/t6_width_scan.py   (hours; background)
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from t6_2d_scan import (SV, build2d, mpo_conjugate_2d,  # noqa: E402
                        mpo_loss_2d, pauli_surrogate)


# ----------------------------------------------------- MPS machinery ----

def mps_from_dense(psi, n, chi=None, tol=1e-12):
    """Exact (or chi-capped) MPS by sequential SVD; returns tensors
    (chi_l, 2, chi_r) and the truncation fidelity loss."""
    tensors = []
    R = psi.reshape(1, -1)
    discarded = 0.0
    for i in range(n - 1):
        a = R.shape[0]
        M = R.reshape(a * 2, -1)
        U, S, Vh = np.linalg.svd(M, full_matrices=False)
        k = int((S > tol).sum()) or 1
        if chi:
            k = min(k, chi)
        discarded += float((S[k:] ** 2).sum())
        tensors.append(U[:, :k].reshape(a, 2, k))
        R = (S[:k, None] * Vh[:k])
    tensors.append(R.reshape(R.shape[0], 2, 1))
    return tensors, discarded


def mpo_mps_expect(Ws, A):
    """<A| O |A> for MPO Ws and MPS A (boundary contraction)."""
    env = np.ones((1, 1, 1), dtype=complex)          # (a_mpo, k_ket, b_bra)
    for W, T in zip(Ws, A):
        # env(a, k, b) ; W(a, s, t, c) ; T(k, t, k') ; conj T(b, s, b')
        env = np.einsum('akb,astc,ktl,bsm->clm', env, W, T, T.conj())
    return complex(env[0, 0, 0])


# ------------------------------------------------------------- main ----

if __name__ == "__main__":
    # gate 1: 2x3 machine-precision check of the MPS route
    P6 = build2d(2, 3, K=2, M=2)
    sv6 = SV(P6)
    rng = np.random.default_rng(3)
    th6 = rng.uniform(-0.8, 0.8, 2)
    A6, disc = mps_from_dense(sv6.psi0, 6)
    Ws6 = mpo_conjugate_2d(P6, th6, 64)
    v_mps = float(np.real(mpo_mps_expect(Ws6, A6)))
    v_ex = sv6.loss(th6)
    print(f"gate 1 (2x3): MPS-route vs exact {abs(v_mps - v_ex):.2e}, "
          f"psi0 truncation loss {disc:.1e}", flush=True)
    assert abs(v_mps - v_ex) < 1e-8

    # gate 2: 4x4 cross-arm (MPS route vs dense mpo_apply route)
    P4 = build2d(4, 4)
    sv4 = SV(P4)
    th4 = 0.1 * np.random.default_rng(20260718).normal(size=P4["K"])
    A4, disc4 = mps_from_dense(sv4.psi0, 16)
    W4 = mpo_conjugate_2d(P4, th4, 32)
    v_a = float(np.real(mpo_mps_expect(W4, A4)))
    v_b = mpo_loss_2d(sv4, th4, 32)
    print(f"gate 2 (4x4): MPS route vs dense route {abs(v_a - v_b):.2e}, "
          f"psi0 exact-MPS bonds max {max(t.shape[2] for t in A4)}",
          flush=True)
    assert abs(v_a - v_b) < 1e-6

    # (a) 4x4 random-theta baseline at chi = 128
    print("\n(a) 4x4 random-control baseline, chi = 128:", flush=True)
    rng_b = np.random.default_rng(77)
    for k in range(3):
        thr = rng_b.uniform(-1.0, 1.0, P4["K"])
        ex = sv4.loss(thr)
        Wr = mpo_conjugate_2d(P4, thr, 128)
        err = abs(float(np.real(mpo_mps_expect(Wr, A4))) - ex)
        print(f"    draw {k}: <H> = {ex:>8.4f}, chi=128 err = {err:.4f}",
              flush=True)

    # (b) 4x5 width scan
    P5 = build2d(4, 5)
    sv5 = SV(P5)
    tol5 = 0.0125 * P5["n"]
    print(f"\n(b) 4x5: n = {P5['n']}, E_min = {sv5.emin:.4f}, "
          f"E_max = {sv5.emax:.4f}, tol = {tol5}", flush=True)
    A5, disc5 = mps_from_dense(sv5.psi0, 20)
    print(f"    psi0 exact-MPS bonds max {max(t.shape[2] for t in A5)}, "
          f"trunc {disc5:.1e}", flush=True)
    th = 0.1 * np.random.default_rng(20260718).normal(size=P5["K"])
    marks = {}
    for t in range(31):
        if t in (0, 30):
            marks[t] = th.copy()
        if t < 30:
            th = th + 0.2 * sv5.grad(th)
    for t, thc in sorted(marks.items()):
        ex = sv5.loss(thc)
        gn = float(np.linalg.norm(sv5.grad(thc)))
        frac = (ex - sv5.emin) / (sv5.emax - sv5.emin)
        print(f"    t={t:>2} <H>={ex:>9.4f} (frac {frac:.2f}) "
              f"|grad|={gn:.3f}", flush=True)
        for Nb in (2048, 8192):
            e = abs(pauli_surrogate(sv5, thc, Nb) - ex)
            print(f"        pauli N={Nb}: err = {e:.4f}", flush=True)
        for chi in (64, 128, 256):
            Wc = mpo_conjugate_2d(P5, thc, chi)
            err = abs(float(np.real(mpo_mps_expect(Wc, A5))) - ex)
            print(f"        chi={chi:>4}: MPO err = {err:.4f}", flush=True)
    print("\nPre-registered: width-hardening fires if the whole chi ladder"
          "\n{64,128,256} fails at 4x5 t=30 (tol 0.25); closes back if"
          "\nchi <= 128 passes.")
