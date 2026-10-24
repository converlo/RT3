import rebound
import numpy as np


def build_system(system):
    sim = rebound.Simulation()
    sim.units = ("AU", "msun", "year")

    sim.add(m=system.binary.m_A)
    sim.add(
        m=system.binary.m_B,
        a=system.binary.orbit.a,
        e=system.binary.orbit.e,
        inc=system.binary.orbit.i,
        omega=system.binary.phases.omega,
        Omega=system.binary.phases.Omega,
        M=system.binary.phases.M,
    )
    sim.add(
        m=system.planet.m_p,
        a=system.planet.orbit.a,
        e=system.planet.orbit.e,
        inc=system.planet.orbit.i,
        omega=system.planet.phases.omega,
        Omega=system.planet.phases.Omega,
        M=system.planet.phases.M,
    )
    sim.add(
        m=system.companion.m_C,
        a=system.companion.orbit.a,
        e=system.companion.orbit.e,
        inc=system.companion.orbit.i,
        omega=system.companion.phases.omega,
        Omega=system.companion.phases.Omega,
        M=system.companion.phases.M,
    )

    sim.move_to_com()
    return sim


def sim_parameters(sim, integrator="whfast"):
    B = sim.particles[1]
    sim.integrator = integrator
    sim.dt = B.P/20
    return sim


def positions(sim, n_orbits=10, res_orbits=100):
    p = sim.particles[2]
    A = sim.particles[0]
    B = sim.particles[1]

    times = np.linspace(sim.t, sim.t + n_orbits*p.P, res_orbits)
    pos = np.zeros((len(times), sim.N, 3))

    for k, t in enumerate(times):
        sim.integrate(t, exact_finish_time=0)
        com_AB = (A.m * np.array([A.x, A.y, A.z])+ B.m * np.array([B.x, B.y, B.z])) / (A.m + B.m)
        pos[k] = np.array([[body.x, body.y, body.z] for body in sim.particles]) - com_AB

    return pos





