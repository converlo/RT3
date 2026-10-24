import numpy as np
from dataclasses import replace

def random_phases(system, rng=None):
    """
    Return a copy of `system` with randomized orbital phases.
 
    `rng` can be a numpy Generator (preferred), an int seed, or None
    (fresh OS entropy, not reproducible).

    rngs, entropy = make_rngs(N, master_seed=12345)
    systems = [random_phases(system, rng) for rng in rngs]
    # log `entropy` alongside the results
    """
    rng = np.random.default_rng(rng)  # no-op if already a Generator
 
    def randomize(body):
        phases = replace(
            body.phases,
            omega=rng.uniform(0, 2 * np.pi),
            Omega=rng.uniform(0, 2 * np.pi),
            M=rng.uniform(0, 2 * np.pi),
        )
        return replace(body, phases=phases)
 
    return replace(
        system,
        binary=randomize(system.binary),
        companion=randomize(system.companion),
        planet=randomize(system.planet),
    )