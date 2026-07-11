import sys
from math import pi
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from windowed_payoff import (M, PRIMES, decoder_failure_mass, make_instance,
                             optimal_w, pattern_histograms, payoff)

F = make_instance(seed=1)
MUS = [len(F[i]) / p for i, p in enumerate(PRIMES)]
SIGMA_F = 17.0
SIGMA_X = M / (2 * pi * SIGMA_F)


def test_histogram_totals():
    hist_u, hist_w = pattern_histograms(F, center=M // 2, sigma_x=200.0)
    assert int(hist_u.sum()) == M          # every x counted exactly once
    assert hist_w.sum() > 0


def test_window_preserves_payoff_at_design_point():
    hist_u, hist_w = pattern_histograms(F, center=M // 2, sigma_x=SIGMA_X)
    w = optimal_w(hist_u, MUS)
    e_u = payoff(hist_u, MUS, *w)
    e_w = payoff(hist_w, MUS, *w)
    assert abs(e_u - e_w) < 1e-10          # machine-precision agreement
    assert e_u > sum(MUS) / len(PRIMES) + 0.05   # and DQI boost is real


def test_conditioning_breaks_when_sigma_x_hits_dmin3_scale():
    # 3 sigma_f ~ d_min(3) = 1155 at sigma_x = 2000; far below it at 200
    hist_u, _ = pattern_histograms(F, center=M // 2, sigma_x=SIGMA_X)
    w = optimal_w(hist_u, MUS)
    e_u = payoff(hist_u, MUS, *w)
    _, hw = pattern_histograms(F, center=M // 2, sigma_x=200.0)
    assert abs(payoff(hw, MUS, *w) - e_u) > 1e-3


def test_decoder_perfect_inside_dmin2():
    assert decoder_failure_mass(SIGMA_F) == 0.0


def test_decoder_fails_beyond_dmin2():
    # 6 sigma_f = 18000 > d_min(2)/2 = 7507: collisions must appear
    assert decoder_failure_mass(3000.0) > 1e-3
