import folium
from folium import plugins
from branca.colormap import LinearColormap


class AgriculturalMap:
    def __init__(self, data_manager):
        """
        Initialise la carte avec le gestionnaire de données.
        
        Args:
            data_manager (AgriculturalDataManager): Instance de la classe AgriculturalDataManager
        """
        self.data_manager = data_manager
        self.map = None
        self.yield_colormap = LinearColormap(
            colors=['red', 'yellow', 'green'],  # Du rouge (faible rendement_final) au vert (haut rendement_final)
            vmin=0,  # rendement_final minimum (ajuster selon les données)
            vmax=3  # rendement_final maximum (ajuster selon les données)
        )

    def create_base_map(self):
        """Crée la carte de base avec les couches appropriées."""
        mean_lat = self.data_manager.monitoring_data['latitude'].mean()
        mean_lon = self.data_manager.monitoring_data['longitude'].mean()
        self.map = folium.Map(location=[mean_lat, mean_lon], zoom_start=12)
        folium.TileLayer('OpenStreetMap').add_to(self.map)

    def add_yield_history_layer(self):
        self.create_base_map()
        """
        Ajoute une couche visualisant l'historique des rendement_finals.
        """
        if self.map is None:
            raise ValueError("La carte n'a pas encore été initialisée. Utilisez `create_base_map` d'abord.")

        for _, row in self.data_manager.soil_data.iterrows():
            parcelle_id = row['parcelle_id']
            latitude = row['latitude']
            longitude = row['longitude']

            # Extraire les données de rendement_final pour la parcelle
            yield_data = self.data_manager.yield_history[
                self.data_manager.yield_history['parcelle_id'] == parcelle_id
            ]

            if not yield_data.empty:
                mean_yield = yield_data['rendement_final'].mean()
                trend = "Tendance : {:.2f}".format(mean_yield)
            else:
                mean_yield = 0
                trend = "Pas de données disponibles"

            # Ajouter un marqueur pour chaque parcelle
            folium.CircleMarker(
                location=(latitude, longitude),
                radius=8,
                color=self.yield_colormap(mean_yield),
                fill=True,
                fill_opacity=0.7,
                tooltip=f"Parcelle ID: {parcelle_id}<br>{trend}<br>rendement_final moyen : {mean_yield:.2f} tonnes/ha"
            ).add_to(self.map)

    def add_current_ndvi_layer(self):
        self.create_base_map()
        """
        Ajoute une couche de la situation actuelle des NDVI.
        """
        if self.map is None:
            raise ValueError("La carte n'a pas encore été initialisée. Utilisez `create_base_map` d'abord.")

        for _, row in self.data_manager.monitoring_data.iterrows():
            latitude = row['latitude']
            longitude = row['longitude']
            ndvi = row['ndvi']

            # Ajouter un marqueur représentant le NDVI actuel
            folium.CircleMarker(
                location=(latitude, longitude),
                radius=6,
                color="Green",
                fill=True,
                fill_opacity=0.6,
                tooltip=f"Latitude: {latitude}<br>Longitude: {longitude}<br>NDVI: {ndvi:.2f}"
            ).add_to(self.map)


    def add_risk_heatmap(self):
        #self.create_base_map(center_coords=(33.85, -5.52), zoom_start=12)
        """
        Ajoute une carte de chaleur représentant les zones à risque calculées
        à partir des métriques de risque combinant le stress hydrique et la température.
        """
        self.create_base_map()
        if self.map is None:
            raise ValueError("La carte n'a pas encore été initialisée. Utilisez create_base_map d'abord.")

        self.data_manager.monitoring_data.reset_index(inplace=True)
        self.data_manager.weather_data.reset_index(inplace=True)
        self.data_manager.yield_history.reset_index(inplace=True)

        # Calculer les métriques de risque
        risk_data = self.data_manager.calculate_risk_metrics(self.data_manager.prepare_features())

            # Fusionner avec les coordonnées des parcelles depuis monitoring_data
        risk_with_coords = risk_data.merge(
            self.data_manager.monitoring_data.reset_index(),
            on='parcelle_id'
        )
        
        # Préparer les données pour la carte de chaleur
        heat_data = [
            [row['latitude'], row['longitude'], row['risk_score']]
            for _, row in risk_with_coords.iterrows()
        ]

        # Ajouter la carte de chaleur avec les scores de risque
        plugins.HeatMap(heat_data, name='Carte de chaleur des risques', radius=10, blur=15, max_zoom=12).add_to(self.map)


    def save_map(self, file_path="map.html"):
        """
        Sauvegarde la carte dans un fichier HTML.

        Args:
            file_path (str): Chemin du fichier HTML où la carte sera sauvegardée.
        """
        if self.map is None:
            raise ValueError("La carte n'a pas encore été initialisée. Utilisez `create_base_map` d'abord.")
        self.map.save(file_path)
