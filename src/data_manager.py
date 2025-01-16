import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


class AgriculturalDataManager:
    def __init__(self):
        """Initialise le gestionnaire de données agricoles."""
        self.monitoring_data = None
        self.weather_data = None
        self.soil_data = None
        self.yield_history = None
        self.scaler = StandardScaler()

    def load_data(self):
        """
        Charge l'ensemble des données nécessaires au système.
        Effectue les conversions de types, les indexations temporelles et
        l'agrégation des données météo par jour.
        """
        # Charger les données de suivi des cultures
        self.monitoring_data = pd.read_csv(
            '../data/monitoring_cultures.csv', parse_dates=['date']
        )

        # Charger les données météo
        self.weather_data = pd.read_csv(
            '../data/meteo_detaillee.csv', parse_dates=['date']
        )

        # Charger les données des sols
        self.soil_data = pd.read_csv('../data/sols.csv')

        # Charger l’historique des rendements
        self.yield_history = pd.read_csv(
            '../data/historique_rendements.csv', parse_dates=['date']
        )

        self.yield_history["rendement_final"] = self.yield_history["rendement_final"].fillna(0)

        result_list = []

        # Loop through the DataFrame in chunks of 24 rows
        chunk_size = 24
        for i in range(0, len(self.weather_data), chunk_size):
            chunk_mean = self.weather_data.iloc[i:i + chunk_size, :].mean()
            chunk_mean["date"] = pd.to_datetime(chunk_mean["date"], format="%Y-%m-%d")
            result_list.append(chunk_mean)

        # Convert the list of medians to a DataFrame
        self.weather_data = pd.DataFrame(result_list)


    def _setup_temporal_indices(self):
        """
        Configure les index temporels pour les différentes séries
        de données et vérifie leur cohérence.
        """
        self.monitoring_data.set_index('date', inplace=True)
        self.weather_data.set_index('date', inplace=True)
        self.yield_history.set_index('date', inplace=True)

    def _verify_temporal_consistency(self):
        """
        Vérifie la cohérence des périodes temporelles entre
        les différents jeux de données, avec gestion de la tolérance et des dates manquantes.
        """
        monitoring_range = (self.monitoring_data.index.min(), self.monitoring_data.index.max())
        weather_range = (self.weather_data.index.min(), self.weather_data.index.max())
        yield_range = (self.yield_history.index.min(), self.yield_history.index.max())

        tolerance = pd.Timedelta(days=1)

        # Check consistency between monitoring and weather data
        monitoring_weather_consistent = abs((monitoring_range[0] - weather_range[0]).days) <= tolerance.days and \
                                        abs((monitoring_range[1] - weather_range[1]).days) <= tolerance.days

        # Check consistency between yield history and monitoring data
        yield_consistent = yield_range[0] >= monitoring_range[0] and yield_range[1] <= monitoring_range[1]

        # Check for missing dates in monitoring data
        expected_dates = pd.date_range(start=monitoring_range[0], end=monitoring_range[1])
        missing_dates = not self.monitoring_data.index.equals(expected_dates)

        # Generate the output report
        report = [
            "===== Vérification de la cohérence temporelle =====",
            f"Période de monitoring : {monitoring_range}",
            f"Période météo         : {weather_range}",
            f"Période des rendements: {yield_range}",
            "",
            "1. Cohérence entre monitoring et météo:",
            "   → OK" if monitoring_weather_consistent else "   → Incohérence détectée",
            "",
            "2. Cohérence entre rendements et monitoring:",
            "   → OK" if yield_consistent else "   → Incohérence détectée : La période des rendements dépasse celle du monitoring",
            "",
            "3. Vérification des dates manquantes dans le monitoring:",
            "   → OK" if not missing_dates else "   → Des dates manquent dans le jeu de données de monitoring",
            "",
            "===== Fin de la vérification ====="
        ]

        # Print the report
        print("\n".join(report))


    def _enrich_with_yield_history(self, data):
        """
        Enrichit les données actuelles avec les informations
        historiques des rendements.
        """

        # Merge the features data with the filtered yield history on 'parcelle_id' and 'year'/'annee'
        enriched_data = pd.merge(data.drop(columns=['culture']), self.yield_history, 
                                on=['date', 'parcelle_id'],
                                how='left').set_index(data.index)

        return enriched_data
    
    def prepare_features(self):
        self._setup_temporal_indices()
        self._verify_temporal_consistency()
        """
        Prépare les caractéristiques pour l'analyse en fusionnant
        les différentes sources de données.
        """
        
        # Fusionner les données météo avec le monitoring
        combined_1 = pd.merge_asof(
            self.monitoring_data.sort_index(),
            self.weather_data.sort_index(),
            left_index=True,
            right_index=True
        )

        # Ajouter les données des sols
        combined_2 = combined_1.merge(self.soil_data, how='left', on=['parcelle_id', 'latitude', 'longitude'])

        combined_2.set_index(combined_1.index, inplace=True)

        features=self._enrich_with_yield_history(combined_2)

        columns_to_fill = ['temperature', 'humidite', 'precipitation', 'rayonnement_solaire',
                        'vitesse_vent', 'direction_vent']
        
        # Loop through each unique parcelle_id
        for parcelle in features['parcelle_id'].unique():
            # Get a subset of the data for the current parcelle_id
            parcelle_data = features[features['parcelle_id'] == parcelle]
            
            # Fill NaN values using backward and forward fill
            filled_data = parcelle_data[columns_to_fill].fillna(method='bfill').fillna(method='ffill')
            
            # Update the original DataFrame
            features.loc[features['parcelle_id'] == parcelle, columns_to_fill] = filled_data

        # Columns to apply linear interpolation
        columns_to_interpolate = ['rendement_estime', 'progression']

        # Loop through each unique parcelle_id
        for parcelle in features['parcelle_id'].unique():
            # Get a subset of the data for the current parcelle_id
            parcelle_data = features[features['parcelle_id'] == parcelle]
            
            # Perform linear interpolation on the specified columns
            interpolated_data = parcelle_data[columns_to_interpolate].interpolate(method='linear', limit_direction='both')
            
            # Update the original DataFrame
            features.loc[features['parcelle_id'] == parcelle, columns_to_interpolate] = interpolated_data

        features["rendement_final"] = features["rendement_final"].fillna(0)

        return features


    def get_temporal_patterns(self, features, parcelle_id):
        """
        Analyse les patterns temporels pour une parcelle donnée, basée sur les données enrichies.

        Args:
            features (DataFrame): Les données enrichies issues de prepare_features.
            parcelle_id (str): L'identifiant de la parcelle.

        Returns:
            DataFrame: Moyennes mensuelles des colonnes numériques.
        """
        # Filtrer les données pour la parcelle spécifiée
        parcelle_data = features[features['parcelle_id'] == parcelle_id]
        if parcelle_data.empty:
            raise ValueError(f"Aucune donnée pour la parcelle spécifiée : {parcelle_id}.")

        # Vérifier que la colonne 'date' est bien au format datetime
        parcelle_data.index = pd.to_datetime(parcelle_data.index)

        # Sélectionner uniquement les colonnes numériques
        numeric_columns = parcelle_data.select_dtypes(include=[np.number]).columns

        # Définir les colonnes à exclure (provenant des datasets 'sols' et 'historique_rendements')
        cols_to_exclude = list(self.soil_data.columns) + list(self.yield_history.columns)

        # Filtrer pour exclure les colonnes de "sols" et "historique_rendements"
        numeric_columns = [col for col in numeric_columns if col not in cols_to_exclude]

        # Filtrer les données pour ne garder que les colonnes pertinentes
        parcelle_data = parcelle_data[numeric_columns]

        # Effectuer le resampling mensuel et calculer les moyennes
        monthly_stats = parcelle_data.resample('M').agg(['mean', 'std', 'min', 'max', 'median'])

        return monthly_stats


    def calculate_risk_metrics(self, data):
        """
        Calcule les métriques de risque en combinant plusieurs facteurs :
        - Moyenne et variance du stress hydrique
        - Température moyenne
        - Capacité de rétention d'eau du sol

        Validation incluse pour détecter les valeurs manquantes.
        """
        # Vérification des données manquantes
        if data[['stress_hydrique', 'temperature']].isnull().sum().sum() > 0:
            raise ValueError("Des valeurs manquantes sont présentes dans les colonnes 'stress_hydrique' ou 'temperature'.")

        if self.soil_data[['parcelle_id', 'capacite_retention_eau']].isnull().sum().sum() > 0:
            raise ValueError("Des valeurs manquantes sont présentes dans les données des sols.")

        # Calcul de la moyenne et de la variance du stress hydrique par parcelle
        stress_metrics = data.groupby('parcelle_id')['stress_hydrique'].agg(['mean', 'std'])
        stress_metrics.rename(columns={'mean': 'mean_stress', 'std': 'stress_variability'}, inplace=True)

        # Ajout de la température moyenne par parcelle
        temperature_metrics = data.groupby('parcelle_id')['temperature'].mean()
        stress_metrics['mean_temperature'] = temperature_metrics

        # Ajout de la capacité de rétention d'eau du sol
        soil_retention = self.soil_data.set_index('parcelle_id')['capacite_retention_eau']
        stress_metrics = stress_metrics.join(soil_retention, on='parcelle_id', how='left')

        # Vérification si certaines parcelles n'ont pas de données sur la capacité de rétention d'eau
        if stress_metrics['capacite_retention_eau'].isnull().any():
            raise ValueError("Certaines parcelles manquent d'informations sur la capacité de rétention d'eau.")

        # Pondérations pour le calcul du score de risque
        weights = {
            'mean_stress': 0.4,             # Pondération pour le stress moyen
            'stress_variability': 0.3,      # Pondération pour la variabilité du stress
            'capacite_retention_eau': 0.2,  # Pondération pour la capacité de rétention d'eau (inverse)
            'mean_temperature': 0.1         # Pondération pour la température moyenne
        }

        # Calcul d'un score de risque composite
        stress_metrics['risk_score'] = (
            stress_metrics['mean_stress'] * weights['mean_stress'] +
            stress_metrics['stress_variability'] * weights['stress_variability'] +
            (1 - stress_metrics['capacite_retention_eau']) * weights['capacite_retention_eau'] +
            stress_metrics['mean_temperature'] * weights['mean_temperature']
        )

        return stress_metrics


    def analyze_yield_patterns(self, parcelle_id):
        """
        Réalise une analyse approfondie des patterns de rendement
        pour une parcelle donnée.
        """
        from statsmodels.tsa.seasonal import seasonal_decompose

        # Extraction et préparation des données pour la parcelle donnée
        history = self.yield_history[self.yield_history['parcelle_id'] == parcelle_id].copy()
        
        if history.empty:
            raise ValueError(f"Aucune donnée de rendement trouvée pour la parcelle {parcelle_id}.")

        # Vérifier que les données sont ordonnées par l'index 'annee'
        history.sort_index(inplace=True)

        # Décomposer la série temporelle des rendements
        decomposed = seasonal_decompose(history['rendement_final'], model='additive', period=1)  # Période 1 pour une série annuelle

        # Stocker les résultats dans un DataFrame
        result = pd.DataFrame({
            'trend': decomposed.trend,
            'seasonal': decomposed.seasonal,
            'resid': decomposed.resid,
            'observed': decomposed.observed
        }, index=history.index)

        return result