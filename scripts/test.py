import warnings
import numpy as np
import circumbinary_triples as ct
import matplotlib.pyplot as plt
 
system = ct.SystemConfig(
    binary=ct.BinaryConfig(
        m_A=1, m_B=1.51, R_A=2.0, R_B=1.0,
        orbit=ct.OrbitConfig(a=0.384, e=0.11, i=0.0),
    ),
    planet=ct.PlanetConfig(
        m_p=0.001, R_p=0.1,
        albedo=0.30, greenhouse_factor=1.13,
        orbit=ct.OrbitConfig(a=1.5, e=0.0, i=0.0),
    ),
    companion=ct.CompanionConfig(
        m_C=2.26, R_C=1.0,
        orbit=ct.OrbitConfig(a=26.17, e=0.169, i=0.0),
    ),
)
 
# --- Réglages du balayage ---------------------------------------------------
A_MIN, A_MAX, N_POINTS = 0.5, 20.0, 24     # a_p (AU)
N_ORBITS = 1000                              # périodes planétaires intégrées
RES_ORBITS = 10000                           # instantanés par intégration
N_REAL = 20                                 # réalisations de phases par a_p
Q = 0.9                                     # seuil de la zone stable
# -----------------------------------------------------------------------------
 
 
def simulate(system, rng):
    system = ct.random_phases(system, rng)
    sim = ct.sim_parameters(ct.build_system(system))
    return ct.trajectory(sim, n_orbits=N_ORBITS, res_orbits=RES_ORBITS)
 
 
observables = {
    "t": lambda system, traj: traj.t,
    "T": lambda system, traj: ct.temperature(system, traj),
    "T_mean": lambda system, traj: ct.mean_temperature(system, traj),
    "T_std": lambda system, traj: ct.std_temperature(system, traj),
    "Stability": lambda system, traj: ct.is_stable(system, traj),
}
 
axis = ct.SweepAxis.lin("planet.orbit.a", A_MIN, A_MAX, N_POINTS)
 
results = ct.sweep(system, axis, simulate=simulate, observables=observables,
                   n_realizations=N_REAL, seed=12345)
 
a_p = np.array(axis.values)
stab = results.array("Stability")           # (n_points, n_real) de 0/1
f_stable = stab.mean(axis=1)                # fraction stable par a_p
 
t = results.array("t")[:, 0, :]             # réalisation 0, (n_points, n_times)
T = results.array("T")[:, 0, :]
 
# --- 1. Fraction stable -------------------------------------------------------
fig_s, ax_s = plt.subplots(figsize=(8, 4))
ax_s.bar(a_p, f_stable, width=0.8 * (a_p[1] - a_p[0]),
         color="steelblue", edgecolor="black")
ax_s.axhline(Q, color="red", ls="--", label=f"q = {Q}")
ax_s.set_xlabel("a_p (AU)")
ax_s.set_ylabel("Stable fraction")
ax_s.set_ylim(0, 1)
ax_s.legend()
 
# --- 2. T(t) pour les orbites stables (réalisation 0) --------------------------
stable_idx = [k for k in range(len(a_p)) if stab[k, 0] == 1]
 
fig_T, ax_T = plt.subplots(figsize=(8, 4))
cmap = plt.cm.viridis(np.linspace(0, 1, len(a_p)))
 
if stable_idx:
    for k in stable_idx:
        ax_T.plot(t[k], T[k] - 273.15, color=cmap[k], lw=0.8,
                  label=f"a_p = {a_p[k]:.2f} AU")
    ax_T.axhspan(0, 100, color="deepskyblue", alpha=0.2, label="HZ (0-100 °C)")
    ax_T.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
else:
    print("Aucune orbite stable pour la réalisation 0")
 
ax_T.set_xlabel("Time (yr)")
ax_T.set_ylabel("Temperature (°C)")
fig_T.tight_layout()
 
# --- 3. et 4. T_mean et T_std, uniquement sur les réalisations stables ---------
T_mean = np.where(stab == 1, results.array("T_mean"), np.nan)
T_std = np.where(stab == 1, results.array("T_std"), np.nan)
 
with warnings.catch_warnings():
    warnings.simplefilter("ignore", RuntimeWarning)   # points sans aucune réalisation stable
    T_mean_a = np.nanmean(T_mean, axis=1) - 273.15
    T_std_a = np.nanmean(T_std, axis=1)
 
fig_meanT, ax_meanT = plt.subplots(figsize=(6, 4))
ax_meanT.plot(a_p, T_mean_a, lw=1, color="blue", marker="+", markersize=5)
ax_meanT.axhspan(0, 100, color="deepskyblue", alpha=0.2)
ax_meanT.set_xlabel("a_p (AU)")
ax_meanT.set_ylabel("Mean Temperature (°C)")
 
fig_stdT, ax_stdT = plt.subplots(figsize=(6, 4))
ax_stdT.plot(a_p, T_std_a, lw=1, color="red", marker="+", markersize=5)
ax_stdT.set_xlabel("a_p (AU)")
ax_stdT.set_ylabel("Temperature standard deviation (K)")
 
plt.show()
