"""
Configuration objects for circumbinary planets in hierarchical triple-star systems.

All objects are frozen dataclasses: they cannot be modified in place, so a
parameter sweep is done by building copies with ``dataclasses.replace``.

Units: masses in solar masses, distances in AU, angles in radians.

Example
-------
>>> from dataclasses import replace
>>> base = SystemConfig(
...     binary=BinaryConfig(
...         m_A=2.0, m_B=1.0, R_A=2.0, R_B=1.0,
...         orbit=OrbitConfig(a=0.1),
...     ),
...     companion=CompanionConfig(
...         m_C=1.0, R_C=1.0,
...         orbit=OrbitConfig(a=15.0),
...     ),
...     planet=PlanetConfig(
...         m_p=0.001, R_p=0.1,
...         albedo=0.30, greenhouse_factor=1.13,
...         orbit=OrbitConfig(a=2.0),
...     ),
... )
>>> variant = replace(
...     base,
...     companion=replace(
...         base.companion,
...         orbit=replace(base.companion.orbit, e=0.4),
...     ),
... )
"""

from __future__ import annotations
from dataclasses import dataclass, field, replace
import numpy as np
from typing import Any, Callable, Mapping, Sequence


@dataclass(frozen=True)
class OrbitConfig:
    a: float
    e: float = 0.0
    i: float = 0.0

def __post_init__(self):
    if self.a <= 0:
        raise ValueError("Semi-major axis must be strictly positive.")
    if not 0 <= self.e < 1:
        raise ValueError("Eccentricity must satisfy 0 <= e < 1.")
    if not 0 <= self.i <= np.pi:
        raise ValueError("Inclination must satisfy 0 <= i <= pi.")

@dataclass(frozen=True)
class PhaseConfig:
    omega: float = 0.0
    Omega: float = 0.0
    M: float = 0.0


@dataclass(frozen=True)
class SpinConfig:
    period: float
    obliquity: float = 0.0
    azimuth: float = 0.0

def __post_init__(self):
    if self.period <= 0:
        raise ValueError("Spin period must be strictly positive.")
    if not 0 <= self.obliquity <= np.pi:
        raise ValueError("Obliquity must satisfy 0 <= obliquity <= pi.")
    if not 0 <= self.azimuth < 2 * np.pi:
        raise ValueError("Azimuth must satisfy 0 <= azimuth < 2*pi.")



@dataclass(frozen=True)
class BinaryConfig:
    m_A: float
    m_B: float
    R_A: float
    R_B: float
    orbit: OrbitConfig
    phases: PhaseConfig = PhaseConfig()

def __post_init__(self):
    if self.m_A <= 0 or self.m_B <= 0:
        raise ValueError("Stellar masses must be positive.")
    if self.R_A <= 0 or self.R_B <= 0:
        raise ValueError("Stellar radii must be positive.")

    @property
    def mAB(self) -> float:
        return self.m_A + self.m_B

    @property
    def muA(self) -> float:
        return self.m_A / self.mAB

    @property
    def muB(self) -> float:
        return self.m_B / self.mAB

@dataclass(frozen=True)
class CompanionConfig:
    m_C: float
    R_C: float
    orbit: OrbitConfig
    phases: PhaseConfig = PhaseConfig()

def __post_init__(self):
    if self.m_C <= 0:
        raise ValueError("Companion mass must be positive.")
    if self.R_C <= 0:
        raise ValueError("Companion radius must be positive.")

@dataclass(frozen=True)
class PlanetConfig:
    m_p: float
    R_p: float
    albedo: float
    greenhouse_factor: float
    orbit: OrbitConfig
    phases: PhaseConfig = PhaseConfig()
    spin: SpinConfig | None = None

def __post_init__(self):
    if self.m_p <= 0:
        raise ValueError("Planetary mass must be positive.")
    if self.R_p <= 0:
        raise ValueError("Planetary radius must be positive.")
    if not 0 <= self.albedo < 1:
        raise ValueError("albedo must satisfy 0 <= A < 1.")
    if self.greenhouse_factor <= 0:
        raise ValueError("greenhouse_factor must be positive.")


@dataclass(frozen=True)
class SystemConfig:
    binary: BinaryConfig
    planet: PlanetConfig
    companion: CompanionConfig

@dataclass(frozen=True)
class Trajectory:
    t: np.ndarray      # (n_times,) temps réels atteints, en années
    pos: np.ndarray
    v: np.ndarray


@dataclass(frozen=True)
class SweepAxis:
    """Valeurs d'un paramètre balayé. `name` peut être un chemin pointé ("companion.m_C")."""

    name: str
    values: Sequence[Any]

    @classmethod
    def lin(cls, name: str, start: float, stop: float, count: int) -> "SweepAxis":
        if count < 1:
            raise ValueError("count doit être >= 1")
        return cls(name=name, values=np.linspace(start, stop, count))

    @classmethod
    def log(cls, name: str, start: float, stop: float, count: int) -> "SweepAxis":
        if count < 1:
            raise ValueError("count doit être >= 1")
        if start <= 0 or stop <= 0:
            raise ValueError("start et stop doivent être > 0 pour une grille log")
        return cls(name=name, values=np.geomspace(start, stop, count))

    @classmethod
    def explicit(cls, name: str, values: Sequence[Any]) -> "SweepAxis":
        if len(values) == 0:
            raise ValueError("values ne peut pas être vide")
        return cls(name=name, values=values)


@dataclass
class SweepResult:
    """Résultats : data[nom_observable][index_point][index_realisation]."""

    axis: SweepAxis
    observable_names: tuple[str, ...]
    data: dict[str, list[list[Any]]]
    entropy: int
    meta: dict = field(default_factory=dict)

    def array(self, name: str) -> np.ndarray:
        """Observable scalaire -> tableau (n_points, n_realisations). None -> NaN."""
        return np.array(self.data[name], dtype=float)

    def mean(self, name: str) -> np.ndarray:
        return np.nanmean(self.array(name), axis=1)

    def std(self, name: str) -> np.ndarray:
        return np.nanstd(self.array(name), axis=1)