# Tableau de Bord Agricole Interactif

## Description du Projet
Ce projet consiste en la création d’un système complet et interactif pour l'analyse avancée des données agricoles. Il intègre des données temporelles et spatiales provenant de multiples sources pour offrir des visualisations, des analyses de tendances, et des prédictions des risques agricoles.

### Objectifs
L'objectif est de fournir un outil d'aide à la décision aux agriculteurs et aux gestionnaires agricoles pour :
- Suivre en temps réel les cultures à l'aide de métriques clés comme le NDVI, le stress hydrique, et la biomasse estimée.
- Identifier les tendances historiques des rendements agricoles.
- Prévoir les risques et les facteurs limitants grâce à des analyses avancées.
- Visualiser les données sous forme de graphiques et de cartes interactives.

---

## Fonctionnalités

### 1. Gestion des Données
- **Intégration Multi-Sources** : Données sur les cultures, les sols, les conditions météorologiques, et les rendements historiques.
- **Validation des Données** : Vérification de la cohérence temporelle et gestion des données manquantes.
- **Préparation des Caractéristiques** : Fusion des données pour une analyse enrichie.

### 2. Analyses Temporelles
- Identification des tendances historiques des rendements.
- Analyse des patterns temporels pour des parcelles spécifiques.
- Détection des facteurs influençant les rendements.

### 3. Visualisations Interactives
- **Cartes Interactives (Folium)** :
  - Visualisation des rendements historiques.
  - Cartes de chaleur pour les zones à risque.
  - Évolution du NDVI sur une carte.
- **Graphiques Interactifs (Bokeh)** :
  - Historique des rendements avec annotations.
  - Évolution temporelle du NDVI.
  - Matrice de stress combinant stress hydrique et météorologique.

### 4. Génération de Rapports
- Création de rapports détaillés par parcelle (historique, analyses actuelles, recommandations).
- Exportation au format PDF pour des présentations professionnelles.

### 5. Prédiction des Risques
- Identification des zones sensibles aux conditions météorologiques défavorables.
- Calcul d'indices de risque basés sur des seuils paramétrables.

---

## Structure du Projet
plaintext
projet_agricole/
│
├── data/
│   ├── monitoring_cultures.csv
│   ├── meteo_detaillee.csv
│   ├── sols.csv
│   └── historique_rendements.csv
│
├── src/
│   ├── data_manager.py
│   ├── dashboard.py
│   ├── map_visualization.py
│   └── report_generator.py
│
├── notebooks/
│   └── analyses_exploratoires.ipynb
│
└── reports/
    └── templates/

---

## Données Utilisées

### `monitoring_cultures.csv`
- Météo : NDVI, LAI, stress hydrique, biomasse estimée.
- Localisation des parcelles avec latitude et longitude.

### `meteo_detaillee.csv`
- Données horaires : température, humidité, précipitations, rayonnement solaire, direction et vitesse du vent.

### `sols.csv`
- Caractéristiques physico-chimiques des sols : type de sol, capacité de rétention d’eau, teneur en nutriments.

### `historique_rendements.csv`
- Rendements annuels par parcelle, performances des cultures passées.

---

## Installation

### 1. Prérequis
- **Python 3.8 ou supérieur**
- Liste des bibliothèques nécessaires :
  ```bash
  pip install folium pandas numpy bokeh scikit-learn plotly streamlit geopandas seaborn statsmodels
  ```

### 2. Configuration

- **Clonez le dépôt GitHub** :

    ```bash
    git clone https://github.com/votre-utilisateur/projet-agricole.git
    cd projet-agricole
    ```

- **Configurez un environnement virtuel** :

    ```bash
    python -m venv venv
    source venv/bin/activate       # Sur macOS/Linux
    venv\Scripts\activate         # Sur Windows
    ```

- **Installez les dépendances** :

    ```bash
    pip install -r requirements.txt
    ```

---

### 3. Lancer le Projet

- **Analyse Exploratoire** : Lancez le notebook Jupyter :

    ```bash
    jupyter notebook notebooks/analyses_exploratoires.ipynb
    ```

- **Tableau de Bord Streamlit** :

    ```bash
    streamlit run src/dashboard.py
    ```

---

## Instructions d'Utilisation

### Visualisations Interactives

- Lancer les cartes et graphiques via `dashboard.py`.
- Naviguer entre les couches interactives (rendements, NDVI, risques).

### Génération de Rapports

- Exécuter le module `report_generator.py` pour créer des rapports PDF.

---

## Exemple de Résultat

### Carte Folium avec les rendements historiques :

_(Capture d’écran à insérer)_

### Graphique Bokeh montrant les tendances des rendements :

_(Capture d’écran à insérer)_

---

## Contributions

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet, suivez ces étapes :

1. **Forkez le dépôt**.
2. **Créez une branche pour vos modifications** :

    ```bash
    git checkout -b feature/nom-de-votre-feature
    ```

3. **Soumettez une pull request** avec une description détaillée de vos changements.

---

## Ressources Supplémentaires

- [Documentation Folium](https://python-visualization.github.io/folium/)
- [Documentation Bokeh](https://docs.bokeh.org/en/latest/)
- [Documentation Pandas](https://pandas.pydata.org/)
- [Documentation Streamlit](https://docs.streamlit.io/)

---

## Auteurs

Ce projet a été développé par **Oussama El Ouazdi**, dans le cadre du programme **Master DSEF**.



