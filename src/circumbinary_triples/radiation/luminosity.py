"""Main-sequence mass-luminosity relation."""
import numpy as np
from circumbinary_triples.constants import SIGMA, AU, L_SUN


def luminosity(m):
    """Main-sequence stellar luminosity, in solar luminosities.

    Four-branch mass-luminosity relation (Salaris & Cassisi 2005):

        L/Lsun = 0.23 * m**2.3     for m < 0.43
        L/Lsun = m**4              for 0.43 <= m < 2
        L/Lsun = 1.4 * m**3.5      for 2 <= m < 55
        L/Lsun = 32000 * m         for m >= 55

    This is a piecewise fit: the branches match only to within a few percent
    at the junctions. It provides neither the effective temperature nor the
    stellar radius.

    Parameters
    ----------
    m : float or array_like
        Stellar mass, in solar masses. Must be strictly positive.

    Returns
    -------
    float or ndarray
        Luminosity, in solar luminosities.

    Raises
    ------
    ValueError
        If any mass is less than or equal to zero.
    """
    m = np.asarray(m, dtype=float)
    if np.any(m <= 0):
        raise ValueError("Mass must be strictly positive.")

    L = np.select(
        [m < 0.43, m < 2, m < 55],
        [0.23 * m**2.3, m**4, 1.4 * m**3.5],
        default=32000 * m,
    )
    return float(L) if L.ndim == 0 else L


