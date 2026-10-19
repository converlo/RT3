# circumbinary-triples

Stabilité dynamique et habitabilité de planètes circumbinaires dans les systèmes
stellaires triples hiérarchiques.

Projet de recherche mené à l'IPAG (Grenoble), équipe Odyssey, projet Stellar-MADE,
sous la direction de Mario Sucerquia, Romain Grane et Nicolás Cuello.

## Objectif

Dans un triple hiérarchique, une planète tourne autour d'un binaire interne (A, B)
tout en étant perturbée par une troisième étoile C sur une orbite plus large.
Le projet cherche les régions orbitales qui satisfont simultanément :

    stable ∩ MER ∩ HZ ∩ faible variation d'obliquité

- stable : la planète survit dynamiquement (simulations N corps avec REBOUND) ;
- MER : région de variation minimale de l'excentricité (Gianuzzi et al. 2026) ;
- HZ : zone habitable radiative circumbinaire, flux des trois étoiles ;
- obliquité : l'axe de rotation de la planète reste stable en présence de C.

Questions posées :

1. Pour quelles architectures stellaires la MER recoupe-t-elle la zone habitable ?
2. Les orbites dynamiquement calmes ont-elles aussi une irradiation plus régulière ?
3. L'étoile C préserve-t-elle ou détruit-elle la stabilité de l'obliquité ?

## Installation
Prérequis : Python 3.10 ou plus récent, et git.

    git clone https://github.com/converlo/RT3.git
    cd RT3

    python -m venv .venv
    source .venv/bin/activate        # Windows : .venv\Scripts\activate

    pip install --upgrade pip
    pip install -e ".[dev]"

Cette dernière commande installe le package en mode éditable (les modifications du
code sont prises en compte immédiatement), ses dépendances (numpy, scipy, rebound,
matplotlib, pandas) et les outils de test (pytest).

Pour les sessions suivantes, il suffit de réactiver l'environnement :

    source .venv/bin/activate

## Organisation du dépôt

    src/circumbinary_triples/   la librairie (toute la physique est ici)
    tests/                      tests, dont régression contre les valeurs publiées
    scripts/                    un script par figure ou tableau du papier
    data/                       sorties de simulations (non versionnées)
    docs/                       architecture et notes
    legacy/                     code du stage précédent, conservé pour référence

Voir `docs/architecture.md` pour le détail des modules et des conventions.

## Règles de travail

1. Aucune physique dans `scripts/` : ils appellent seulement la librairie.
2. Toute fonction analytique est testée contre une valeur publiée.
3. Chaque résultat se régénère depuis un script, avec une graine aléatoire fixée.
4. On travaille sur des branches, jamais directement sur `main`.

## Références principales

- Gianuzzi, Sucerquia, Cuello & Giuppone (2026), Circumbinary planets in coplanar
  triple-star systems. I. Minimum eccentricity variation region, arXiv:2609.04450.
- Holman & Wiegert (1999), AJ 117, 621.
- Kopparapu et al. (2013, 2014) ; Haghighipour & Kaltenegger (2013) ; Kane & Hinkel (2013).
- Rein & Liu (2012) ; Rein & Tamayo (2015) : REBOUND et WHFast.

## Licence

GPL-3.0, voir `LICENSE`.