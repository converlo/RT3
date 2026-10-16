"""
Test file to simulate WDS 08403+1921 system using REBOUND. The WDS 08403+1921 system is a hierarchical triple star system with an inner binary star system named AB and third companion star C, the system has the following parameters:
m_A = 1.65 M⊙, m_B = 1.51 M⊙, m_C = 2.26 M⊙, a_AB = 0.384 au, a_C = 26.17 au, e_AB = 0.11, e_C = 0.169, P_AB ≈50 day, P_C ≈57.5 yr
"""

import rebound
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import random as rd
import os

#################################

parameters = {
    "binary": {
        "m_A": 1.65,
        "m_B": 1.51,
        "a_AB": 0.384,
        "e_AB": 0.11,
        "P_AB": 50 / 365.25
    },
    "companion": {
        "m_C": 2.26,
        "a_C": 26.17,
        "e_C": 0.169,
        "P_C": 57.5,
        "inc_C": 0.0
    }
}

phase = {
    "f_AB": rd.random() * 2 * np.pi,
    "omega_AB": rd.random() * 2 * np.pi,
    "f_C": rd.random() * 2 * np.pi,
    "omega_C": rd.random() * 2 * np.pi
}

simulation = {
    "n_C_orbits": 0.05,
    "time_resolution": 3000
}

#################################

sim = rebound.Simulation()
sim.units = ("AU", "msun", "year")
sim.integrator = "whfast"

sim.add(m=parameters["binary"]["m_A"])
sim.add(m=parameters["binary"]["m_B"], e=parameters["binary"]["e_AB"], a=parameters["binary"]["a_AB"], f=phase["f_AB"], omega=phase["omega_AB"], inc=rd.random() * np.pi)

cdmAB = sim.com(0, 2)

sim.add(m=parameters["companion"]["m_C"], e=parameters["companion"]["e_C"], a=parameters["companion"]["a_C"], f=phase["f_C"], omega=phase["omega_C"], inc=parameters["companion"]["inc_C"], primary=cdmAB)

sim.move_to_com()

sim.dt = parameters["binary"]["P_AB"] / 20

A = sim.particles[0]
B = sim.particles[1]
C = sim.particles[2]
m_A = parameters["binary"]["m_A"]
m_B = parameters["binary"]["m_B"]
P_C = parameters["companion"]["P_C"]

################################

time = np.linspace(0, simulation["n_C_orbits"]*P_C, simulation["time_resolution"])
position = np.zeros((simulation["time_resolution"], 3, 2))

for i, t in enumerate(time):
        sim.integrate(t)
        
        x_com_AB = (m_A * A.x + m_B * B.x) / (m_A + m_B)
        y_com_AB = (m_A * A.y + m_B * B.y) / (m_A + m_B)

        position[i, 0] = [A.x - x_com_AB, A.y - y_com_AB]
        position[i, 1] = [B.x - x_com_AB, B.y - y_com_AB]
        position[i, 2] = [C.x - x_com_AB, C.y - y_com_AB]

################################
a_AB = parameters["binary"]["a_AB"]
e_AB = parameters["binary"]["e_AB"]
a_C = parameters["companion"]["a_C"]
e_C = parameters["companion"]["e_C"]

fig, ax = plt.subplots(figsize=(8, 8))
lim = 1.1 * a_C * (1 + e_C)
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_xlabel("x [au]")
ax.set_ylabel("y [au]")
ax.set_title("WDS 08403+1921 : orbite de C autour de AB")
ax.plot([0], [0], marker="+", color="gray")

star_A, = ax.plot([], [], marker='*', color="#000000", markersize=8,  linestyle='None', label="A")
star_B, = ax.plot([], [], marker='*', color="#FF1919", markersize=8,  linestyle='None', label="B")
star_C, = ax.plot([], [], marker='*', color="#00FFB7", markersize=8,  linestyle='None', label="C")

trail_C, = ax.plot([], [], color="#00FFB7", alpha=0.5, lw=0.8)
ax.legend(loc="upper right")

time_text = ax.text(0.02, 0.96, "", transform=ax.transAxes)

step = 10
frame = np.arange(0, simulation["time_resolution"], step)

def update(k):
    i = frame[k]
    star_C.set_data([position[i, 2, 0]], [position[i, 2, 1]])
    trail_C.set_data(position[:i + 1:step, 2, 0], position[:i + 1:step, 2, 1])
    time_text.set_text(f"t = {time[i]:.2f} yr")


ani = anim.FuncAnimation(fig, update, frames=len(frame), interval=50)

os.makedirs("Figures/test", exist_ok=True)
filename = "wds_08403_1921.gif"
ani.save(f"Figures/test/{filename}", writer="pillow", fps=30)

plt.close(fig)