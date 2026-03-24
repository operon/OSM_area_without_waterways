# OSM Scripts

Partant du principe que dans une zone à l’échelle d'un pays ou d'une région, il y a des waterways de tout type uniformément réparti par les pluies.
Ce script python  permet de créer une page HTML comprenant un quadrillage de carreaux dans lesquels aucun waterway n'est présent.
Cette carte permet d'ouvrir dans JOSM les petites zones sans waterway afin de pouvoir les tracer à l'aide des photos satellite.

Afin d'avoir une idée des zones "pauvres" en waterway, il existe le site https://waterwaymap.org qui permet de visualiser les cours d'eau.
Lorsque l'on distingue une zone, il n'est pas facile de l'identifier et de l'éditer, d'où l'idée de mon script.

Quatre paramétres et principalement l'ID de la relation OSM de la zone à éditer et un fichier HTML cliquable permet d'éditer sous JOSM les zones "Pauvre" en waterways. 

Attention : Script optimisé et seulement testé sous Windows IDLE Python 3.13

## Installation

```bash

```

## Utilisation

```bash
python scripts/area_without_waterways/area_without_waterways.py
```

## Description

Ce script permet de :
    • extraire des données OSM
    • les traiter par algorithme
    • Créer une page HTML permettant d’ouvrir sous JOM des carreaux de taille paramétrable dans lesquels aucun waterway n'est présent.

## Exemple

area_without_waterways.py permet de créer une page HTML comprenant un quadrillage de zone dans lesquelles aucun waterway n'est présent.
Partant du principe que dans une zone à l’échelle d'un pays ou d'une région) il y a des waterways uniformément réparti.
Cette carte permet d'ouvrir dans JOSM les petites zones sans waterway afin de pouvoir les tracer à l'aide des photos satellite.

Afin d'avoir une idée des zones "pauvres" en waterway, il existe le site https://waterwaymap.org qui permet devisualiser les coursd'eau.


## Auteur

operon

