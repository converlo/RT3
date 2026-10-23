from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class SweepAxis:
    """Valeurs d'un paramètre balayé."""

    name: str
    values: Sequence[Any]

    @classmethod
    def linspace(
        cls,
        name: str,
        start: float,
        stop: float,
        count: int,
    ) -> "SweepAxis":
        if count < 1:
            raise ValueError("count doit être >= 1")
        return cls(name=name, values=np.linspace(start, stop, count))

    @classmethod
    def explicit(
        cls,
        name: str,
        values: Sequence[Any],
    ) -> "SweepAxis":
        if len(values) == 0:
            raise ValueError("values ne peut pas être vide")
        return cls(name=name, values=values)


@dataclass
class SweepResult:
    """Résultats indexés par point, réalisation et nom d'observable."""

    axis: SweepAxis
    observable_names: tuple[str, ...]
    values: dict[str, list[list[Any]]]
    # values[nom_observable][index_point][index_realisation]


Setter = Callable[[Any, Any], Any]
Simulator = Callable[[Any, np.random.Generator], Any]
Observer = Callable[[Any, Any], Any]


def sweep(
    system: Any,
    axis: SweepAxis,
    *,
    setter: Setter,
    simulate: Simulator,
    observables: Mapping[str, Observer],
    n_random: int = 1,
    seed: int | None = None,
) -> SweepResult:
    """
    Balaye une suite de valeurs sans connaître le modèle physique.

    setter(system, value) -> configuration modifiée
    simulate(configuration, rng) -> résultat intermédiaire
    observer(configuration, simulation_result) -> scalaire, tableau ou objet

    Chaque observable est calculée à partir du même résultat de simulation.
    Si des observables exigent des intégrations différentes, simulate peut
    les lancer toutes et les réunir dans son résultat.
    """
    if n_random < 1:
        raise ValueError("n_realizations doit être >= 1")
    if not observables:
        raise ValueError("Il faut fournir au moins une observable")

    seed_sequence = np.random.SeedSequence(seed)
    child_seeds = seed_sequence.spawn(len(axis.values) * n_random)

    output = {
        name: [[] for _ in axis.values]
        for name in observables
    }

    seed_index = 0
    for point_index, parameter_value in enumerate(axis.values):
        configuration = setter(system, parameter_value)

        for _ in range(n_random):
            rng = np.random.default_rng(child_seeds[seed_index])
            seed_index += 1

            simulation_result = simulate(configuration, rng)

            for name, observer in observables.items():
                output[name][point_index].append(
                    observer(configuration, simulation_result)
                )

    return SweepResult(
        axis=axis,
        observable_names=tuple(observables),
        values=output,
    )


