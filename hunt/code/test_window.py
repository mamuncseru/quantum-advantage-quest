import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from advantage_window import (dqi_fraction, dqi_opi_fraction, prange_fraction,
                              window)


def test_paper_benchmark_n_over_p_one_tenth():
    # arXiv 2408.08292v5: DQI = 1/2 + sqrt(19)/20 ~ 0.7179, Prange = 0.55
    assert np.isclose(dqi_opi_fraction(0.1, 0.5), 0.5 + np.sqrt(19) / 20)
    assert np.isclose(dqi_opi_fraction(0.1, 0.5), 0.7179, atol=1e-4)
    assert np.isclose(prange_fraction(0.1, 0.5), 0.55)


def test_paper_benchmark_n_over_p_one_half():
    # arXiv 2408.08292v5: DQI = 1/2 + sqrt(3)/4 ~ 0.9330, Prange = 0.75
    assert np.isclose(dqi_opi_fraction(0.5, 0.5), 0.5 + np.sqrt(3) / 4)
    assert np.isclose(dqi_opi_fraction(0.5, 0.5), 0.9330, atol=1e-4)
    assert np.isclose(prange_fraction(0.5, 0.5), 0.75)


def test_semicircle_shape_at_mu_half():
    # at mu = 1/2 Eq. 6 reduces to 1/2 + sqrt((l/m)(1 - l/m)) — a semicircle —
    # on the non-saturated branch l/m <= 1 - mu = 1/2
    lm = np.linspace(0, 0.5, 50)
    assert np.allclose(dqi_fraction(lm, 0.5),
                       0.5 + np.sqrt(lm * (1 - lm)))


def test_saturation_branch():
    assert dqi_fraction(0.6, 0.5) == 1.0          # mu > 1 - ell/m saturates


def test_window_positive_everywhere_at_mu_half():
    x = np.linspace(0.01, 0.99, 99)
    assert (window(x, 0.5) > 0).all()             # DQI beats Prange on OPI
