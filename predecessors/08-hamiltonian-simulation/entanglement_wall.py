"""Why the classical methods fail — with the mechanism measured, not named.

The autopsy claims tensor networks die because entanglement grows under
quench dynamics. That is a statement with a number in it, so here is the
number.

Evolve a product state under a transverse-field Ising Hamiltonian and watch
the entanglement entropy across the middle cut. It grows **linearly in
time** — and a matrix-product state needs bond dimension chi ~ exp(S) to
hold that state, so the classical memory cost grows **exponentially in
time**. That is the wall, and it is a property of the dynamics rather than
of anyone's cleverness.

The same code also shows the other half of the story, which the honest
version of this page has to include: ground states of the same Hamiltonian
obey an *area law*, entropy stays flat as the system grows, and tensor
networks handle them easily. The classical wall is a wall for **dynamics**,
not for everything — which is precisely why the advantage frontier here is
instance-wise.

Run:  .venv/bin/python predecessors/08-hamiltonian-simulation/entanglement_wall.py
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

SX = sp.csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
SZ = sp.csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))
ID = sp.identity(2, format="csr", dtype=complex)


def _op_at(op, i, n):
    out = sp.identity(1, format="csr", dtype=complex)
    for j in range(n):
        out = sp.kron(out, op if j == i else ID, format="csr")
    return out


def tfim_sparse(n, g=1.0, J=1.0):
    """H = -J sum Z_i Z_{i+1} - g sum X_i, as a sparse matrix.

    g = 1 is the critical point of this model, which is where entanglement
    grows fastest — the hardest case for a classical tensor network and so
    the fair one to measure.
    """
    H = sp.csr_matrix((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        H = H - J * (_op_at(SZ, i, n) @ _op_at(SZ, i + 1, n))
    for i in range(n):
        H = H - g * _op_at(SX, i, n)
    return H


def product_state(n, up=True):
    """|000...> — a product state, entanglement entropy exactly zero."""
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0 if up else (2 ** n - 1)] = 1.0
    return psi


def entanglement_entropy(psi, n, cut=None):
    """Von Neumann entropy across a bipartition, from the Schmidt values.

    Reshape the state into a matrix across the cut and take its singular
    values: S = -sum s^2 log2 s^2. No approximation anywhere.
    """
    cut = n // 2 if cut is None else cut
    m = psi.reshape(2 ** cut, 2 ** (n - cut))
    s = np.linalg.svd(m, compute_uv=False)
    p = s ** 2
    p = p[p > 1e-16]
    return float(-np.sum(p * np.log2(p)))


def bond_dimension_needed(psi, n, cut=None, keep=0.99):
    """Schmidt rank required to retain `keep` of the state's weight.

    This is what an MPS actually has to store. It is the operational
    version of the entropy, and it is the number that decides whether a
    classical simulation fits in memory.
    """
    cut = n // 2 if cut is None else cut
    m = psi.reshape(2 ** cut, 2 ** (n - cut))
    s = np.linalg.svd(m, compute_uv=False)
    w = np.cumsum(s ** 2) / np.sum(s ** 2)
    return int(np.searchsorted(w, keep) + 1)


def quench(n, times, g=1.0):
    """Evolve a product state and record entropy and bond dimension."""
    H = tfim_sparse(n, g=g)
    psi0 = product_state(n)
    out = []
    for t in times:
        psi = spla.expm_multiply(-1j * H * t, psi0)
        psi = psi / np.linalg.norm(psi)
        out.append((float(t), entanglement_entropy(psi, n),
                    bond_dimension_needed(psi, n)))
    return out


def growth_rate(n, times, g=1.0):
    """Fitted slope of S(t) — linear growth is the whole claim."""
    rows = quench(n, times, g=g)
    ts = np.array([r[0] for r in rows])
    ss = np.array([r[1] for r in rows])
    m = ts > 0
    return float(np.polyfit(ts[m], ss[m], 1)[0])


def ground_state_entropy(n, g=1.0):
    """Entropy of the ground state across the middle cut.

    Three regimes, and the distinction decides who wins:

    * **gapped** (g away from 1): the entropy *saturates* — an area law, since
      the "area" of a cut in one dimension is a single point. Constant in n,
      so bond dimension is constant, so DMRG eats it. This has been true
      since 1992.
    * **critical** (g = 1): logarithmic, S ~ (c/6) log2 n for an open chain
      with central charge c = 1/2 here. Still only polynomial bond
      dimension — harder, not hard.
    * **quenched dynamics** (`quench` above): linear in *time*, hence
      exponential cost. That is the only one of the three that is a wall.

    Printing all three is the honest version of "classical methods fail",
    because two thirds of the time they do not.
    """
    H = tfim_sparse(n, g=g)
    vals, vecs = spla.eigsh(H, k=1, which="SA")
    return entanglement_entropy(vecs[:, 0], n)


def ground_state_scaling(g, ns=(6, 8, 10, 12, 14, 16)):
    """Fitted slope of ground-state entropy against log2(n).

    ~0 for a gapped chain (area law), ~c/6 = 1/12 at the critical point for
    the Ising universality class. Measured, then compared with the conformal
    field theory prediction in the tests.
    """
    ns = np.array(ns, dtype=float)
    ss = np.array([ground_state_entropy(int(n), g=g) for n in ns])
    return float(np.polyfit(np.log2(ns), ss, 1)[0])


def classical_memory_bytes(chi, n, bytes_per_complex=16):
    """Memory for an MPS of bond dimension chi: ~ n * chi^2 * d complex numbers."""
    return n * chi * chi * 2 * bytes_per_complex


def _demo():
    print("1 · ENTANGLEMENT UNDER A QUENCH — THE MECHANISM OF FAILURE\n")
    n = 14
    times = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    rows = quench(n, times)
    print(f"   transverse-field Ising chain, n = {n}, critical (g = 1)\n")
    print(f"   {'t':>6} {'entropy S (bits)':>18} {'bond dim for 99%':>19} "
          f"{'MPS memory':>14}")
    for t, s, chi in rows:
        mem = classical_memory_bytes(chi, n)
        pretty = (f"{mem / 1e6:.1f} MB" if mem < 1e9
                  else f"{mem / 1e9:.1f} GB")
        print(f"   {t:>6.1f} {s:>18.3f} {chi:>19d} {pretty:>14}")
    print(f"\n   fitted growth rate: S ≈ {growth_rate(n, times):.2f} bits per "
          f"unit time — LINEAR.")
    print("   Bond dimension is 2^S, so the classical cost is exponential in")
    print("   *time*, not in system size. Doubling the simulated time squares")
    print("   the memory. That is the tensor-network wall, and no amount of")
    print("   engineering moves it.")

    print("\n2 · EXTRAPOLATING THE COST\n")
    rate = growth_rate(n, times)
    print(f"   {'simulated time t':>18} {'S (bits)':>10} {'bond dim χ':>14} "
          f"{'MPS memory':>16}")
    for t in (4, 8, 16, 32, 64):
        s = rate * t
        chi = 2 ** s
        mem = classical_memory_bytes(chi, 50)
        print(f"   {t:>18d} {s:>10.1f} {chi:>14.2e} {mem:>13.2e} B")
    print("\n   (extrapolating the measured rate; the point is the shape)")

    print("\n3 · AND THE TWO THIRDS THAT ARE NOT A WALL\n")
    print("   ground-state entropy across the middle cut:\n")
    print(f"   {'n':>4}" + "".join(f"{'g = ' + str(g):>14}"
                                   for g in (0.5, 1.0, 2.0)))
    for n2 in (6, 8, 10, 12, 14, 16):
        print(f"   {n2:>4}" + "".join(
            f"{ground_state_entropy(n2, g=g):>14.4f}" for g in (0.5, 1.0, 2.0)))
    print(f"\n   {'regime':>28}   {'slope vs log₂ n':>16}")
    for g, label in ((0.5, "gapped (ferromagnetic)"), (1.0, "critical"),
                     (2.0, "gapped (paramagnetic)")):
        print(f"   {label:>28}   {ground_state_scaling(g):>16.4f}")
    print(f"\n   gapped: flat — the AREA LAW, and DMRG has eaten these since 1992.")
    print(f"   critical: {ground_state_scaling(1.0):.3f} against the Ising CFT's")
    print(f"   c/6 = {1 / 12:.3f} — logarithmic, so still only polynomial cost.")
    print("\n   Only the quench is exponential. The quantum advantage in")
    print("   simulation lives in DYNAMICS and strong correlation — not in")
    print("   'chemistry' as a whole, and any claim that does not say which")
    print("   of these three regimes it is in has not started arguing yet.")


if __name__ == "__main__":
    _demo()
