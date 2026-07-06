"""Classical Metropolis on the 1D Ising chain — the workhorse we must beat.

Baseline discipline: before admiring quantum Gibbs samplers, hold the thing
they compete with. Exact Gibbs averages by enumeration (n small), Metropolis
estimates by sampling; mixing is what makes the estimate honest.
"""

import numpy as np


def ising_energy(spins, J=1.0):
    """Open 1D chain: E = -J sum s_i s_{i+1}, spins in {-1, +1}."""
    return -J * (spins[:-1] * spins[1:]).sum()


def exact_mean_energy(n, beta, J=1.0):
    configs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1
    E = -J * (configs[:, :-1] * configs[:, 1:]).sum(axis=1)
    w = np.exp(-beta * (E - E.min()))
    return (E * w).sum() / w.sum()


def metropolis_mean_energy(n, beta, sweeps, J=1.0, seed=0, burn_frac=0.2):
    rng = np.random.default_rng(seed)
    s = rng.choice([-1, 1], size=n)
    E = ising_energy(s, J)
    samples = []
    for sweep in range(sweeps):
        for _ in range(n):
            i = rng.integers(n)
            dE = 2 * J * s[i] * ((s[i - 1] if i > 0 else 0)
                                 + (s[i + 1] if i < n - 1 else 0))
            if dE <= 0 or rng.random() < np.exp(-beta * dE):
                s[i] = -s[i]
                E += dE
        if sweep >= burn_frac * sweeps:
            samples.append(E)
    return np.mean(samples)


if __name__ == "__main__":
    n, beta = 10, 0.7
    exact = exact_mean_energy(n, beta)
    print(f"1D Ising, n = {n}, beta = {beta}: exact <E> = {exact:.4f}")
    for sweeps in (10, 100, 1000, 10000):
        est = metropolis_mean_energy(n, beta, sweeps)
        print(f"  Metropolis {sweeps:>6d} sweeps: <E> = {est:8.4f}"
              f"  (err {abs(est-exact):.4f})")
