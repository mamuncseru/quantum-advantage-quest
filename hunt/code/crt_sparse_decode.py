"""Q(A2.1), constant-sparsity fragment: enumeration decoder, verified.

Result (ii) of hunt/notes/A2-crt-opi-derivation.md in executable form:
CRT-sparse integers with support S are exactly the multiples of M/P_S, so
for |S| <= ell = O(1), decoding under size-noise is nearest-multiple
rounding enumerated over supports — poly(m^ell). Unique when the noise is
below half the progression spacing.

This validates the constant-ell geometry numerically. The open frontier
(linear ell, designed moduli) is section 7(iv) of the note.
"""

from itertools import combinations
from math import prod

import sympy


def crt_sparse(moduli, support, ks):
    """t = sum_{i in support} (M/p_i) k_i mod M."""
    M = prod(moduli)
    return sum((M // moduli[i]) * k for i, k in zip(support, ks)) % M


def crt_weight_pattern(t, moduli):
    """Support and residue pattern of t: k_i = t (M/p_i)^{-1} mod p_i."""
    M = prod(moduli)
    pattern = {}
    for i, p in enumerate(moduli):
        k = (t % p) * pow(M // p % p, -1, p) % p
        if k:
            pattern[i] = k
    return pattern


def mod_dist(a, b, M):
    d = (a - b) % M
    return min(d, M - d)


def decode(t_prime, moduli, ell, delta):
    """Enumerate supports; nearest-multiple round; return all candidates
    within delta. O(m^ell) supports, poly arithmetic each."""
    M = prod(moduli)
    hits = set()
    for size in range(ell + 1):
        for S in combinations(range(len(moduli)), size):
            g = M // prod(moduli[i] for i in S) if S else M
            t_hat = round(t_prime / g) * g % M
            if mod_dist(t_hat, t_prime, M) <= delta:
                if len(crt_weight_pattern(t_hat, moduli)) <= ell:
                    hits.add(t_hat)
    return hits


def planted_instance(m, ell, seed, noise_frac=0.25):
    """Random planted (t, t') with noise below the uniqueness bound.

    Uses stdlib random: M is astronomically large, far beyond int64.
    """
    import random
    rng = random.Random(seed)
    moduli = [int(p) for p in sympy.primerange(3, 10 ** 6)][:m]
    M = prod(moduli)
    support = sorted(rng.sample(range(m), ell))
    ks = [rng.randrange(1, moduli[i]) for i in support]
    t = crt_sparse(moduli, support, ks)
    # Uniqueness radius = d_min(2*ell)/2 with the exact minimum-distance law
    #     d_min(w) = M / P_max(w),  P_max(w) = product of the w largest moduli
    # (two weight-<=ell integers differ by a weight-<=2*ell integer, and by
    # CRT the residue-1 combination always achieves M/P_S on any support S —
    # theorem verified numerically 2026-07-07, note section 7).
    finest = prod(sorted(moduli)[-2 * ell:])
    delta_max = M // (2 * finest) - 1
    delta = int(noise_frac * delta_max)
    noise = rng.randint(-delta, delta) if delta > 0 else 0
    return moduli, t, (t + noise) % M, delta_max


if __name__ == "__main__":
    for seed in range(5):
        moduli, t, t_prime, delta = planted_instance(m=24, ell=3, seed=seed)
        hits = decode(t_prime, moduli, ell=3, delta=delta)
        pat = crt_weight_pattern(t, moduli)
        print(f"seed {seed}: planted w(t) = {len(pat)}, "
              f"candidates found = {len(hits)}, recovered = {t in hits}")
