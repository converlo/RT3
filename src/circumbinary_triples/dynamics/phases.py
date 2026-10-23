import numpy as np
from dataclasses import replace

def make_rngs(n, master_seed=None):
    """
    Create n statistically independent Generators from a seed.
 
    Returns (rngs, entropy). Store `entropy` in the metadata of your outputs
    (figures, tables) and pass it back as `master_seed` to reproduce the run.
    """
    ss = np.random.SeedSequence(master_seed)
    return [np.random.default_rng(s) for s in ss.spawn(n)], ss.entropy

def random_phases(system, rng=None):
    """
    Return a copy of `system` with randomized orbital phases.
 
    `rng` can be a numpy Generator (preferred), an int seed, or None
    (fresh OS entropy, not reproducible).
 
    Only the mean anomaly M (uniform in time) and the argument of pericenter
    omega are drawn. Omega (longitude of the ascending node) is left
    untouched: it is degenerate for coplanar systems (i = 0).

    rngs, entropy = make_rngs(N, master_seed=12345)
    systems = [random_phases(system, rng) for rng in rngs]
    # log `entropy` alongside the results
    """
    rng = np.random.default_rng(rng)  # no-op if already a Generator
 
    def randomize(body):
        phases = replace(
            body.phases,
            omega=rng.uniform(0, 2 * np.pi),
            Omega=rng.uniform(0, 2 * np.pi),  # unchanged
            M=rng.uniform(0, 2 * np.pi),
        )
        return replace(body, phases=phases)
 
    return replace(
        system,
        binary=randomize(system.binary),
        companion=randomize(system.companion),
        planet=randomize(system.planet),
    )