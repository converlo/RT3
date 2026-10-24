from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Mapping, Sequence

from circumbinary_triples.config import (SweepAxis, SweepResult)

import numpy as np


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