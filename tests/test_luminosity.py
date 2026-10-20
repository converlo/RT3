"""Tests for the main-sequence mass-luminosity relation."""
import numpy as np
import pytest

from circumbinary_triples.radiation.luminosity import luminosity

# Mass boundaries between the four branches (solar masses)
JUNCTIONS = [0.43, 2.0, 55.0]


def test_sun_has_one_solar_luminosity():
    assert luminosity(1.0) == 1.0


@pytest.mark.parametrize(
    "mass, expected",
    [
        (0.1, 0.23 * 0.1**2.3),   # low-mass branch
        (1.0, 1.0),               # solar branch
        (1.5, 1.5**4),            # m**4 branch
        (10.0, 1.4 * 10.0**3.5),  # massive branch
        (100.0, 32000 * 100.0),   # very massive branch
    ],
)
def test_each_branch_formula(mass, expected):
    assert luminosity(mass) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize(
    "lo, hi",
    [(0.1, 0.42), (0.44, 1.99), (2.01, 54.0), (56.0, 500.0)],
)
def test_increasing_within_each_branch(lo, hi):
    m = np.linspace(lo, hi, 200)
    assert np.all(np.diff(luminosity(m)) > 0)


@pytest.mark.parametrize("m_junction", JUNCTIONS)
def test_branches_match_at_junctions_within_five_percent(m_junction):
    below = luminosity(m_junction * (1 - 1e-9))
    above = luminosity(m_junction)
    assert above == pytest.approx(below, rel=0.05)


def test_known_dip_at_two_solar_masses_is_small():
    # The fit is not continuous: L drops slightly when crossing m = 2.
    below = luminosity(2.0 * (1 - 1e-9))
    above = luminosity(2.0)
    assert above < below
    assert (below - above) / below < 0.02


def test_array_input_returns_array_of_same_shape():
    m = np.array([0.1, 1.0, 5.0, 100.0])
    L = luminosity(m)
    assert isinstance(L, np.ndarray)
    assert L.shape == m.shape


def test_scalar_input_returns_python_float():
    assert isinstance(luminosity(1.0), float)


@pytest.mark.parametrize("bad_mass", [0.0, -1.0, [1.0, 0.0], [-0.5, 2.0]])
def test_non_positive_mass_raises(bad_mass):
    with pytest.raises(ValueError):
        luminosity(bad_mass)