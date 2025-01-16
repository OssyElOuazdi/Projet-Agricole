from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, DateRangeSlider, HoverTool, LinearColorMapper, ColorBar, CustomJS, Span, DatetimeTickFormatter
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_folium import st_folium
from map_visualization import AgriculturalMap
from data_manager import AgriculturalDataManager



class AgriculturalDashboard:
    def __init__(self, data_manager):
        """
        Initialise le tableau de bord avec le gestionnaire de données.
        """
        self.data_manager = data_manager
        self.source = None
        self.hist_source = None
        self.selected_parcelle = None
        self.create_data_sources()

    def create_data_sources(self):
        """
        Prépare les sources de données pour Bokeh en intégrant
        les données actuelles et historiques.
        """
        # Charger les données enrichies
        features = self.data_manager.prepare_features()

        # Préparer les données pour l'historique des rendement_finals
        yield_history = self.data_manager.yield_history.reset_index()

        # Créer les sources de données Bokeh
        self.source = ColumnDataSource(features)
        self.hist_source = ColumnDataSource(yield_history)

        print("Sources de données préparées.")

    def create_yield_history_plot(self):
        """
        Crée un graphique montrant l'évolution historique des rendement_finals
        pour une parcelle sélectionnée via un widget interactif.
        """
        # Initialisation des données
        yield_data = self.hist_source.data
        parcelles = self.get_parcelle_options()  # Liste unique des parcelles

        # Source de données dynamique
        filtered_source = ColumnDataSource(data={key: [] for key in yield_data.keys()})

        # Initialisation du graphique
        p = figure(
            title="Historique des rendement_finals par Parcelle",
            x_axis_type="datetime",
            height=400,
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )

        # Ajouter la courbe et les points (données dynamiques)
        line = p.line(
            x='date',
            y='rendement_final',
            source=filtered_source,
            line_width=2,
            color="blue",
            legend_label="rendement_final",
        )
        points = p.scatter(
            x='date',
            y='rendement_final',
            source=filtered_source,
            size=8,
            color="red",
            legend_label="Points de rendement_final",
        )

        # Ajouter les outils interactifs
        p.add_tools(HoverTool(
            tooltips=[
                ("Parcelle", "@parcelle_id"),
                ("Année", "@date{%Y}"),
                ("rendement_final", "@rendement_final{0.2f} t/ha"),
            ],
            formatters={"@date": "datetime"},
            mode="vline",
        ))

        p.legend.location = "top_left"
        p.xaxis.axis_label = "Année"
        p.yaxis.axis_label = "rendement_final (t/ha)"

        # Widget de sélection
        select = Select(
            title="Sélectionnez une parcelle :",
            value="Choisir",  # Parcelle par défaut
            options=parcelles,
        )

        # Callback JavaScript pour mettre à jour les données affichées
        callback = CustomJS(
            args=dict(source=self.hist_source, filtered_source=filtered_source, select=select),
            code="""
            const data = source.data;
            const filtered = filtered_source.data;
            const selected_parcelle = select.value;

            // Réinitialiser les données filtrées
            for (let key in filtered) {
                filtered[key] = [];
            }

            // Filtrer les données pour la parcelle sélectionnée
            for (let i = 0; i < data['parcelle_id'].length; i++) {
                if (data['parcelle_id'][i] === selected_parcelle) {
                    for (let key in filtered) {
                        filtered[key].push(data[key][i]);
                    }
                }
            }

            // Mettre à jour la source filtrée
            filtered_source.change.emit();
            """
        )
        select.js_on_change('value', callback)

        # Retourner le graphique et le widget dans une disposition
        return column(select, p)

    def create_ndvi_temporal_plot(self):
        """
        Crée un graphique montrant l’évolution du NDVI avec
        des seuils de référence basés sur l’historique,
        et filtrage interactif par parcelle et par plage de dates.
        """
        # Préparation des données
        ndvi_data = self.source.data
        df = pd.DataFrame(ndvi_data)
        parcelles = self.get_parcelle_options()  # Liste unique des parcelles

        # Source de données dynamique filtrée
        filtered_source = ColumnDataSource(data={key: [] for key in ndvi_data.keys()})

        # Créer une figure Bokeh
        p = figure(
            title="Évolution du NDVI et Seuils Historiques",
            x_axis_type='datetime',
            height=400,
            width=700,
            tools="pan,box_zoom,reset,save"
        )

        # Ajouter la ligne NDVI
        p.line(
            source=filtered_source,
            x='date',
            y='ndvi',
            line_width=2,
            color='green',
            legend_label="NDVI"
        )

        # Ajouter les points NDVI
        p.scatter(
            source=filtered_source,
            x='date',
            y='ndvi',
            size=4,
            color='orange',
            legend_label="Point de NDVI"
        )

        # Définir les seuils NDVI
        seuil_bas = Span(location=0.3, dimension='width', line_color='red', line_dash='dashed', line_width=2)
        seuil_haut = Span(location=0.7, dimension='width', line_color='blue', line_dash='dashed', line_width=2)
        p.add_layout(seuil_bas)
        p.add_layout(seuil_haut)

        # Ajouter les seuils dans la légende
        p.line(
            x='date',
            y=[0.3] * len(df['date']),
            line_dash='dashed',
            line_width=2,
            color='red',
            legend_label="Seuil Bas (0.3)",
        )
        p.line(
            x='date',
            y=[0.7] * len(df['date']),
            line_dash='dashed',
            line_width=2,
            color='blue',
            legend_label="Seuil Haut (0.7)",
        )

        # Ajouter un outil de survol (HoverTool)
        p.add_tools(HoverTool(
            tooltips=[
                ("Date", "@date{%F}"),
                ("NDVI", "@ndvi{0.00}")
            ],
            formatters={'@date': 'datetime'},
            mode='vline'
        ))

        # Configurer les axes
        p.xaxis.axis_label = "Date"
        p.yaxis.axis_label = "NDVI"
        p.xaxis.formatter = DatetimeTickFormatter(days="%d %b %Y")
        p.legend.location = "top_left"

        # Widget de sélection de parcelle
        select = Select(
            title="Sélectionnez une parcelle :",
            value="Choisir",  # Parcelle par défaut
            options=parcelles
        )

        # Widget de sélection de plage de dates
        date_range_slider = DateRangeSlider(
            title="Plage de dates",
            start=df['date'].min(),
            end=df['date'].max(),
            value=(df['date'].min(), df['date'].max()),
            step=1
        )

        # Callback JavaScript pour filtrer les données selon la parcelle et la plage de dates sélectionnées
        callback = CustomJS(
            args=dict(source=self.source, filtered_source=filtered_source, select=select, date_range_slider=date_range_slider),
            code="""
            const data = source.data;
            const filtered = filtered_source.data;
            const selected_parcelle = select.value;
            const [start, end] = date_range_slider.value;  // Plage de dates sélectionnée (timestamps)

            // Réinitialiser les données filtrées
            for (let key in filtered) {
                filtered[key] = [];
            }

            // Filtrer les données pour la parcelle et la plage de dates sélectionnées
            for (let i = 0; i < data['parcelle_id'].length; i++) {
                const date = new Date(data['date'][i]).getTime();
                if (data['parcelle_id'][i] === selected_parcelle && date >= start && date <= end) {
                    for (let key in filtered) {
                        filtered[key].push(data[key][i]);
                    }
                }
            }

            // Mettre à jour la source filtrée
            filtered_source.change.emit();
            """
        )

        # Lier les widgets au callback
        select.js_on_change('value', callback)
        date_range_slider.js_on_change('value', callback)

        # Retourner la disposition avec les widgets et le graphique
        return column(select, date_range_slider, p)


    def create_stress_matrix(self):
        """
        Crée une matrice de stress combinant stress hydrique
        et conditions météorologiques.
        """
        # Générer les données simulées ou utiliser les données réelles
        data = self.source.data
        stress_hydrique = np.array(data['stress_hydrique'])
        temperature = np.array(data['temperature'])

        # Normaliser les données entre 0 et 1
        stress_hydrique_norm = (stress_hydrique - stress_hydrique.min()) / (stress_hydrique.max() - stress_hydrique.min())
        temperature_norm = (temperature - temperature.min()) / (temperature.max() - temperature.min())

        # Calculer le stress combiné (pondération ajustable)
        alpha, beta = 0.6, 0.4
        stress_total = alpha * stress_hydrique_norm + beta * temperature_norm

        # Préparer les données pour la heatmap
        grid_size = 10
        x_bins = np.linspace(0, 1, grid_size + 1)
        y_bins = np.linspace(0, 1, grid_size + 1)

        heatmap, x_edges, y_edges = np.histogram2d(
            stress_hydrique_norm, temperature_norm, bins=(x_bins, y_bins), weights=stress_total
        )

        # Calculer les centres des cellules pour chaque combinaison de x et y
        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2

        # Créer une grille 2D des centres
        x_grid, y_grid = np.meshgrid(x_centers, y_centers)

        # Transformer les données en format DataFrame
        heatmap_df = pd.DataFrame({
            'x': x_grid.ravel(),  # Aplatir la grille 2D en 1D
            'y': y_grid.ravel(),
            'stress': heatmap.T.flatten(),  # Transposer la matrice pour correspondre à l'orientation de Bokeh
        })

        source = ColumnDataSource(heatmap_df)

        # Créer le graphique
        p = figure(
            title="Matrice de Stress",
            x_range=(0, 1),
            y_range=(0, 1),
            height=400,
            width=400,
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )

        # Ajouter la carte de chaleur
        mapper = LinearColorMapper(palette="Viridis256", low=heatmap_df['stress'].min(), high=heatmap_df['stress'].max())
        p.rect(
            x='x',
            y='y',
            width=1/grid_size,
            height=1/grid_size,
            source=source,
            fill_color=linear_cmap('stress', palette="Viridis256", low=heatmap_df['stress'].min(), high=heatmap_df['stress'].max()),
            line_color=None,
        )

        # Ajouter une barre de couleur
        color_bar = ColorBar(color_mapper=mapper, location=(0, 0))
        p.add_layout(color_bar, 'right')

        # Configurer les axes
        p.xaxis.axis_label = "Stress Hydrique (Normalisé)"
        p.yaxis.axis_label = "Température (Normalisée)"

        return p

    def create_yield_prediction_plot(self):
        """
        Crée un graphique interactif de prédiction des rendement_finals basé sur les données
        historiques et actuelles, filtré par parcelle.
        """
        # Données historiques et actuelles
        historical_data = self.hist_source.data

        # Liste des parcelles disponibles
        parcelles = self.get_parcelle_options()

        # Préparer les sources de données dynamiques
        filtered_source = ColumnDataSource(data={key: [] for key in historical_data.keys()})
        prediction_source = ColumnDataSource(data={'date': [], 'rendement_final': [], 'parcelle_id': []})

        # Initialisation du graphique
        p = figure(
            title="Prédiction des rendement_finals par Parcelle",
            x_axis_type="datetime",
            height=400,
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )

        # Ajouter les rendement_finals historiques
        p.line(
            x='date',
            y='rendement_final',
            source=filtered_source,
            line_width=2,
            color="blue",
            legend_label="Historique"
        )
        p.scatter(
            x='date',
            y='rendement_final',
            source=filtered_source,
            size=8,
            color="blue",
            legend_label="Points historiques"
        )

        # Ajouter les prédictions futures
        p.line(
            x='date',
            y='rendement_final',
            source=prediction_source,
            line_width=2,
            color="green",
            line_dash="dashed",
            legend_label="Prédictions futures"
        )
        p.scatter(
            x='date',
            y='rendement_final',
            source=prediction_source,
            size=8,
            color="green",
            legend_label="Points de prédiction"
        )

        # Ajouter un HoverTool
        hover = HoverTool()
        hover.tooltips = [
            ("Année", "@date{%F}"),  # Affiche l'année au format yyyy
            ("rendement_final", "@rendement_final{0.00} t/ha"),  # Affiche le rendement_final avec une décimale
            ("Parcelle", "@parcelle_id")  # Affiche la parcelle sélectionnée
        ]
        hover.formatters = {
            '@date': 'datetime'  # Formatage de l'année en date
        }
        p.add_tools(hover)

        # Configurer les axes
        p.xaxis.axis_label = "Année"
        p.yaxis.axis_label = "rendement_final (t/ha)"
        p.legend.location = "top_left"

        # Ajouter un widget pour sélectionner une parcelle
        select = Select(
            title="Sélectionnez une parcelle :",
            value="Choisir",  # Parcelle par défaut
            options=parcelles
        )

        # Callback pour filtrer les données et calculer les prédictions
        callback = CustomJS(
            args=dict(source=self.hist_source, filtered_source=filtered_source, prediction_source=prediction_source, select=select),
            code="""
            const data = source.data;
            const filtered = filtered_source.data;
            const prediction = prediction_source.data;
            const selected_parcelle = select.value;

            // Réinitialiser les données filtrées
            for (let key in filtered) {
                filtered[key] = [];
            }
            for (let key in prediction) {
                prediction[key] = [];
            }

            // Filtrer les données historiques pour la parcelle sélectionnée
            const years = [];
            const yields = [];
            for (let i = 0; i < data['parcelle_id'].length; i++) {
                if (data['parcelle_id'][i] === selected_parcelle) {
                    for (let key in filtered) {
                        filtered[key].push(data[key][i]);
                    }
                    years.push(new Date(data['date'][i]).getTime());  // Années en millisecondes
                    yields.push(data['rendement_final'][i]);
                }
            }

            // Si suffisamment de données, calculer les prédictions futures
            if (years.length >= 2) {
                // Ajustement linéaire simple (remplacer par un modèle plus sophistiqué si nécessaire)
                const n = years.length;
                const x_mean = years.reduce((a, b) => a + b, 0) / n;
                const y_mean = yields.reduce((a, b) => a + b, 0) / n;
                const slope = years.reduce((sum, x, i) => sum + (x - x_mean) * (yields[i] - y_mean), 0) /
                            years.reduce((sum, x) => sum + Math.pow(x - x_mean, 2), 0);
                const intercept = y_mean - slope * x_mean;

                // Prédictions futures
                const future_years = [];
                const future_yields = [];
                const last_year = Math.max(...years);
                for (let i = 1; i <= 5; i++) {  // 5 années futures
                    const future_year = last_year + i * 365 * 24 * 60 * 60 * 1000;  // Ajouter un an (en millisecondes)
                    future_years.push(future_year);
                    future_yields.push(intercept + slope * future_year);
                }

                prediction['date'] = future_years;
                prediction['rendement_final'] = future_yields;
                prediction['parcelle_id'] = new Array(future_years.length).fill(selected_parcelle);  // Ajouter la parcelle dans les prédictions
            }

            // Mettre à jour les sources de données
            filtered_source.change.emit();
            prediction_source.change.emit();
            """
        )

        # Lier le callback au widget de sélection
        select.js_on_change('value', callback)

        # Retourner la disposition avec le widget et le graphique
        return column(select, p)

    def create_layout(self):
        """
        Organise tous les graphiques dans une mise en page cohérente.
        """
        # Créer les graphiques
        yield_plot = self.create_yield_history_plot()
        ndvi_plot = self.create_ndvi_temporal_plot()
        stress_matrix = self.create_stress_matrix()
        prediction_plot = self.create_yield_prediction_plot()

        # Organiser les graphiques en lignes et colonnes
        # Disposition: 2 lignes de 2 graphiques
        top_row = row(yield_plot, ndvi_plot)  # Première ligne avec 2 graphiques
        bottom_row = row(stress_matrix, prediction_plot)  # Deuxième ligne avec 2 graphiques

        # Retourner une disposition en colonne avec les lignes organisées
        layout = column(top_row, bottom_row)
        return layout
    

    def get_parcelle_options(self):
        """
        Retourne la liste des parcelles disponibles.
        """
        return sorted(self.data_manager.monitoring_data['parcelle_id'].unique())
    

    
    def prepare_stress_data(self):
        """
        Prépare les données pour la matrice de stress.
        """
        data = self.data_manager.prepare_features()

        # Exemple de calcul d'un indice de stress combiné
        data['stress_combine'] = (
            0.7 * data['stress_hydrique'] +
            0.3 * data['temperature'] / data['temperature'].max()
        )

        self.source = ColumnDataSource(data)

    def update_plots(self, attr, old, new):
        """
        Met à jour les graphiques en fonction des nouvelles données sélectionnées.
        """
        selected_parcelle = self.parcelle_selector.value

        # Filtrer les données pour la parcelle sélectionnée
        filtered_monitoring = self.data_manager.monitoring_data[
            self.data_manager.monitoring_data['parcelle_id'] == selected_parcelle
        ]
        filtered_yield = self.data_manager.yield_history[
            self.data_manager.yield_history['parcelle_id'] == selected_parcelle
        ]

        # Mettre à jour les sources de données
        self.source.data = ColumnDataSource(filtered_monitoring).data
        self.hist_source.data = ColumnDataSource(filtered_yield).data







class IntegratedDashboard:
    def __init__(self, data_manager):
        """
        Initialize the dashboard with the data manager.
        """
        self.data_manager = data_manager

    def create_streamlit_dashboard(self):
        """
        Create the Streamlit interface for displaying visualizations.
        """
        # Set Streamlit page configuration
        st.set_page_config(
            page_title="Tableau de Bord Agricole Intégré",
            page_icon="🌾",
            layout="wide",
        )

        # Add a sidebar with convenient content
        st.sidebar.title("Navigation 🌟")
        st.sidebar.markdown(
            """
            Bienvenue dans le Tableau de Bord Agricole Intégré !  
            Utilisez les onglets pour explorer les visualisations :
            
            - **📊 Historique des Rendements**
            - **🌱 NDVI Actuels**
            - **🔥 Carte de Chaleur des Risques**
            
            ---
            **À propos**  
            Ce tableau de bord vise à aider les agriculteurs et chercheurs 
            à mieux comprendre et visualiser les données agricoles.
            
            ---
            """
        )
        st.sidebar.info("Développé par Oussama El Ouazdi")

        # Tabs for independent visualizations
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)  # Open center div
        st.title("🌾 Tableau de Bord Agricole Intégré")
        st.markdown(
            """
            Ce tableau de bord interactif vous permet d'explorer les données agricoles via des visualisations riches et informatives :
            - **Historique des Rendements**
            - **NDVI Actuels (Indice de Végétation)**
            - **Carte de Chaleur des Risques**
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)  # Close center div

        # Visualizations in tabs
        tab1, tab2, tab3 = st.tabs(
            ["📊 Historique des Rendements", "🌱 NDVI Actuels", "🔥 Carte de Chaleur des Risques"]
        )

        with tab1:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.header("📊 Visualisation de l'Historique des Rendements")
            st.markdown("</div>", unsafe_allow_html=True)
            yield_map = AgriculturalMap(self.data_manager)
            yield_map.create_base_map()
            yield_map.add_yield_history_layer()
            st_folium(yield_map.map, width=900, height=600)

        with tab2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.header("🌱 Visualisation des NDVI Actuels")
            st.markdown("</div>", unsafe_allow_html=True)
            ndvi_map = AgriculturalMap(self.data_manager)
            ndvi_map.create_base_map()
            ndvi_map.add_current_ndvi_layer()
            st_folium(ndvi_map.map, width=900, height=600)

        with tab3:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.header("🔥 Carte de Chaleur des Risques")
            st.markdown("</div>", unsafe_allow_html=True)
            risk_map = AgriculturalMap(self.data_manager)
            risk_map.create_base_map()
            risk_map.add_risk_heatmap()
            st_folium(risk_map.map, width=900, height=600)


# Main execution block
if __name__ == "__main__":
    # Initialize the data manager
    data_manager = AgriculturalDataManager()
    data_manager.load_data()  # Load all necessary data

    # Create the integrated dashboard
    dashboard = IntegratedDashboard(data_manager)
    dashboard.create_streamlit_dashboard()


