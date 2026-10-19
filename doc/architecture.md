# Architecture

## Modules de la librairie (src/circumbinary_triples/)

| Module | Rôle |
|---|---|
| constants.py | Constantes physiques et unités, définies une seule fois |
| config.py | Description d'un système (masses, orbites, planète) |
| analytic/ | Prédictions théoriques : a_ME, a_LK, critère de Holman & Wiegert |
| dynamics/ | Construction du système REBOUND, intégration, critères de stabilité |
| radiation/ | Luminosités, flux des trois étoiles, température d'équilibre,  Habitable Zone (HZ) definition |

## Conventions

**Unités.** Dynamique : UA, masse solaire, année. Rayonnement : SI. Les conversions
passent par `constants.py`.

**Notation.** Binaire interne A et B, compagnon externe C, planète p. Les paramètres
de l'orbite interne sont notés a_AB, e_AB, ceux de l'orbite externe a_C, e_C.

**Critères d'instabilité.** 

**Reproductibilité.** Graine aléatoire fixée pour les phases initiales, paramètres
d'un run enregistrés avec ses résultats, une figure = un script.

## Choix de conception

- Layout `src/` : les tests s'exécutent sur le package réellement installé.
- La physique est dans la librairie, jamais dans `scripts/`.
- Les valeurs publiées servent de tests de régression.
