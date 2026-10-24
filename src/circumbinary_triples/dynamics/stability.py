import numpy as np

def is_stable(system, trajectory):
    G = 4 * np.pi**2
    mu = G * (system.binary.m_A + system.binary.m_B + system.planet.m_p)
    a_C = system.companion.orbit.a

    rp = trajectory.pos[:, 2, :]
    vp = trajectory.v[:, 2, :]

    energy = 0.5 * np.sum(vp**2, axis=1) - mu / np.linalg.norm(rp, axis=1)

    if not np.all(np.isfinite(energy)) or np.any(energy >= 0):
        return 0 
    
    if np.any(-mu / (2 * energy) > a_C):
        return 0   

    return 1
