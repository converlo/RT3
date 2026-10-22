import rebound


def build_system():

    sim = rebound.Simulation()
    sim.units = ("AU", "msun", "year")

    sim.add(m=m_A)
    sim.add(m=m_B, a=a_B, e=e_B, inc=inc_B, omega=w_B, Omega=Omega_B, M=M_B)

    sim.move_to_com()

    sim.add(m=m_p, a=a_p, e=e_p, inc=inc_p, omega=w_p, Omega=Omega_p, M=M_p)

    sim.move_to_com()

    sim.add(m=m_C, a=a_C, e=e_C, inc=inc_C, omega=w_C, Omega=Omega_C, M=M_C)

    


def positions():



