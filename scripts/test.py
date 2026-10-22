import circumbinary_triples as ct
import numpy as np
import rebound as rb
import matplotlib.pyplot as plt

WDS08403 = ct.SystemConfig(
    binary=ct.BinaryConfig(
        m_A=1.65, m_B=1.51, R_A=2.0, R_B=1.0,
        orbit=ct.OrbitConfig(a=0.384, e=0.11, i=0.0),
    ),
    planet=ct.PlanetConfig(
            m_p=0.001, R_p=0.1,
            albedo=0.30, greenhouse_factor=1.13,
            orbit=ct.OrbitConfig(a=5.0, e=0.0, i=0.0),
    ),
    companion=ct.CompanionConfig(
        m_C=2.26, R_C=1.0,
        orbit=ct.OrbitConfig(a=26.17, e=0.169, i=0.0),
    )
    
)

sim = ct.sim_parameters(ct.build_system(WDS08403), integrator="whfast")

pos = ct.positions(sim, n_orbits=100000, res_orbits=10000)

plt.figure(figsize=(6, 6))

bodies = [
    (0, "Star A", "orange", 8),
    (1, "Star B", "red", 4),
    (2, "Planet p", "blue", 2),
    (3, "Companion star C", "grey", 4),
]

for i, name, color, size in bodies:
    plt.plot(pos[:, i, 0], pos[:, i, 1], color=color, label=name)

plt.xlabel("x [AU]")
plt.ylabel("y [AU]")
plt.axis("equal")
plt.xlim(-35, 35)
plt.ylim(-35, 35)
plt.legend()
plt.show()