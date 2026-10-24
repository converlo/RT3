from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Callable, Mapping, Sequence

import numpy as np


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


Setter = Callable[[Any, str, Any], Any]
Simulator = Callable[[Any, np.random.Generator], Any]
Observer = Callable[[Any, Any], Any]


def set_path(system: Any, path: str, value: Any) -> Any:
    """
    Setter générique pour dataclasses imbriquées (copie, ne modifie pas `system`).

    set_path(system, "companion.m_C", 1.5)
    set_path(system, "planet.a", 3.0)
    """
    head, _, rest = path.partition(".")
    if not rest:
        return replace(system, **{head: value})
    return replace(system, **{head: set_path(getattr(system, head), rest, value)})


def sweep(
    system: Any,
    axis: SweepAxis,
    *,
    simulate: Simulator,
    observables: Mapping[str, Observer],
    setter: Setter = set_path,
    n_realizations: int = 1,
    seed: int | None = None,
    common_random_numbers: bool = True,
    on_error: str = "raise",
) -> SweepResult:
    """
    Balaye un paramètre sans connaître le modèle physique.

    setter(system, axis.name, value) -> configuration modifiée
    simulate(configuration, rng)     -> résultat intermédiaire
    observer(configuration, result)  -> scalaire, tableau ou objet

    Chaque observable est calculée à partir de la même simulation.

    common_random_numbers : si True, la réalisation j utilise le même flux
        aléatoire à chaque point de la grille (les différences entre points
        viennent alors du paramètre, pas du bruit d'échantillonnage).
    on_error : "raise" ou "none" (stocke None pour toutes les observables
        du couple (point, réalisation) qui a échoué).
    """
    if n_realizations < 1:
        raise ValueError("n_realizations doit être >= 1")
    if not observables:
        raise ValueError("Il faut fournir au moins une observable")
    if on_error not in ("raise", "none"):
        raise ValueError("on_error doit valoir 'raise' ou 'none'")

    seed_sequence = np.random.SeedSequence(seed)
    n_points = len(axis.values)

    if common_random_numbers:
        children = seed_sequence.spawn(n_realizations)
    else:
        children = seed_sequence.spawn(n_points * n_realizations)

    output = {name: [[] for _ in range(n_points)] for name in observables}

    for i, value in enumerate(axis.values):
        configuration = setter(system, axis.name, value)

        for j in range(n_realizations):
            child = children[j] if common_random_numbers else children[i * n_realizations + j]
            # Un SeedSequence réutilisé redonne exactement le même flux
            rng = np.random.default_rng(child)

            try:
                result = simulate(configuration, rng)
                values = {name: obs(configuration, result) for name, obs in observables.items()}
            except Exception:
                if on_error == "raise":
                    raise
                values = {name: None for name in observables}

            for name in observables:
                output[name][i].append(values[name])

    meta = {
        "axis": axis.name,
        "n_points": n_points,
        "n_realizations": n_realizations,
        "common_random_numbers": common_random_numbers,
        "numpy_version": np.__version__,
    }
    return SweepResult(
        axis=axis,
        observable_names=tuple(observables),
        data=output,
        entropy=seed_sequence.entropy,
        meta=meta,
    )