# Projet Final : Analyse Avancée de Données Agricoles et Tableau de Bord Interactif

## Description
Ce projet vise à créer un tableau de bord interactif pour l'analyse temporelle et spatiale des données agricoles. L'objectif est d'intégrer des données historiques avec des informations de monitoring en temps réel, pour fournir des analyses approfondies et des prédictions utiles à la gestion agricole.

### Données utilisées
Le projet s'appuie sur plusieurs sources de données :
- *monitoring_cultures.csv* : Données de suivi des cultures (NDVI, LAI, stress hydrique, etc.).
- *meteo_detaillee.csv* : Données météorologiques horaires (température, humidité, précipitations, etc.).
- *sols.csv* : Caractéristiques physico-chimiques des sols.
- *historique_rendements.csv* : Historique des rendements annuels par parcelle.

### Fonctionnalités principales
1. *Analyse des données agricoles multi-sources* : Intégration et gestion des données.
2. *Visualisations interactives* : Graphiques temporels et cartes spatiales via Bokeh et Folium.
3. *Indicateurs de performance* : Calcul des tendances, métriques de risque, et analyses avancées.
4. *Génération de rapports automatisés* : Export en PDF des résultats et recommandations.
5. *Prédiction des risques agricoles* : Modèles basés sur des méthodes statistiques et machine learning.

---

## Installation

### Prérequis
- Python 3.8 ou supérieur.
- Modules nécessaires (installables via pip):
  bash
  pip install folium pandas numpy bokeh pandoc python-docx scikit-learn plotly
  pip install streamlit geopandas seaborn statsmodels
  
- Outils externes :
  - *pandoc* et *xelatex* pour la génération de rapports PDF.
  - Minimum 8 Go de RAM pour les traitements.

### Structure du projet
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


Pour éviter les conflits de dépendances, créez un environnement virtuel avec :
bash
python -m venv venv
source venv/bin/activate   # ou "venv\Scripts\activate" sous Windows


---

## Utilisation

1. *Chargement des données* :
   Implémentez et utilisez les méthodes de data_manager.py pour intégrer les données.
2. *Visualisations* :
   - Utilisez dashboard.py pour des graphiques interactifs (via Bokeh).
   - Employez map_visualization.py pour créer des cartes (via Folium).
3. *Rapports* :
   Génération de rapports automatisés avec report_generator.py.

---

## Ressources
- [Documentation Folium](https://python-visualization.github.io/folium/)
- [Documentation Bokeh](https://docs.bokeh.org/en/latest/)
- [Documentation Pandoc](https://pandoc.org/MANUAL.html)
- [Tutoriel Streamlit](https://docs.streamlit.io/)
