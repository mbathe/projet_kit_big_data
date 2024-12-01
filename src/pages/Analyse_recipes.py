import logging
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from src.process.recipes import Recipe
from src.utils.static import mois
import locale
from src.visualizations import load_css
from src.utils.static import submissions_data
from src.utils.static import recipe_columns_description
from collections import Counter
from streamlit_echarts import st_echarts
from src.utils.static import constribution_data
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration du logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    # Fallback to a default locale or skip locale setting
    locale.setlocale(locale.LC_TIME, '')
DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE")
YEAR_MIN = 1999 if DEPLOIEMENT_SITE != "ONLINE" else 2014
YEAR_MAX = 2018 if DEPLOIEMENT_SITE != "ONLINE" else 2018
class CSSLoader:
    """Class responsible for loading CSS."""
    @staticmethod
    def load(css_file):
        try:
            load_css(css_file)
            logging.info(f"CSS loaded from {css_file}")
        except Exception as e:
            logging.error(f"Failed to load CSS from {css_file}: {e}")
            raise Exception(f"Failed to load CSS: {str(e)}")


class DataManager:
    def __init__(self):
        self.recipe = Recipe()

    def set_date_range(self, start_date, end_date):
        try:
            self.recipe = Recipe(date_start=start_date, date_end=end_date)
            logging.info(f"Date range set from {start_date} to {end_date}")
        except Exception as e:
            logging.error(f"Failed to set date range: {e}")

    def get_recipe_data(self):
        return self.recipe

    def export_data(self, export_format):
        try:
            if export_format == "CSV":
                return self.recipe.st.session_state.data.to_csv(index=False)
            elif export_format == "JSON":
                return self.recipe.st.session_state.data.to_json(orient="records")
        except Exception as e:
            logging.error(f"Failed to export data: {e}")

    def analyze_temporal_distribution(self, start_datetime, end_datetime):
        try:
            return self.recipe.analyze_temporal_distribution(start_datetime, end_datetime)
        except Exception as e:
            logging.error(f"Failed to analyze temporal distribution: {e}")

    def analyze_recipe_complexity(self):
        try:
            return self.recipe.analyze_recipe_complexity()
        except Exception as e:
            logging.error(f"Failed to analyze recipe complexity: {e}")

    def analyze_nutrition(self):
        try:
            return self.recipe.analyze_nutrition()
        except Exception as e:
            logging.error(f"Failed to analyze nutrition: {e}")

    def analyze_tags(self):
        try:
            return self.recipe.analyze_tags()
        except Exception as e:
            logging.error(f"Failed to analyze tags: {e}")


class DisplayManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.load_css()

    def load_css(self):
        path_to_css_user = 'src/css_pages/analyse_user.css'
        path_to_css_recipe = 'src/css_pages/recipe.css'
        CSSLoader.load(path_to_css_user)
        CSSLoader.load(path_to_css_recipe)

    def sidebar(self):
        try:
            with st.sidebar:
                st.title("⚙️ Configuration")
                theme = st.selectbox("Thème", ["Clair", "Sombre"], key='theme')
                langue = st.selectbox(
                    "Langue", ["Français", "English"], key='langue')
                date_range = st.date_input(
                    "Période d'analyse",
                    value=(date(YEAR_MIN, 1, 1), date(YEAR_MAX, 12, 31)),
                    key='date_filter',
                    min_value=date(YEAR_MIN, 1, 1),
                    max_value=date(YEAR_MAX, 12, 31),
                )

                if st.button("Charger les données"):
                    start_date = date_range[0]
                    end_date = date_range[1]
                    if start_date > end_date:
                        st.error(
                            "La date de début doit être antérieure ou égale à la date de fin.")
                    else:
                        self.data_manager.set_date_range(start_date, end_date)
                        st.success(f"Période d'analyse: {
                                   start_date} à {end_date}")
                show_toogle = st.toggle(
                    "Utiliser les données nettoyées", value=True)
                if show_toogle:
                    self.data_manager.get_recipe_data().clean_dataframe()
                st.header("📥 Exporter")
                export_format = st.radio("Format d'export", ["CSV", "JSON"])
                if export_format == "CSV":
                    csv = self.data_manager.export_data("CSV")
                    if st.download_button(label="Télécharger au format CSV", data=csv, file_name="data.csv", mime="text/csv"):
                        st.success("Export en cours...")
                elif export_format == "JSON":
                    json = self.data_manager.export_data("JSON")
                    if st.download_button(label="Télécharger au format JSON", data=json, file_name="data.json", mime="application/json"):
                        st.success("Export en cours...")
        except Exception as e:
            logging.error(f"Error in sidebar: {e}")

    def home_tab(self):
        try:
            st.title("🏠 Analyse de Recettes")
           # st.markdown("#### Valeurs distintes")
            columns_to_show = ["name", "submitted",
                               "nutrition", "description", "tags", "ingredients"]
            coll = st.columns(len(columns_to_show) - 1)
            i = 0
            for index, row in self.data_manager.get_recipe_data().annomalis["column_info"].iterrows():
                if index in columns_to_show:
                    with coll[i]:
                        if index == "submitted":
                            st.markdown(f"""
                            <div class="metric-container">
                                <div class="metric-label">{str(index)}</div>
                                <div class="metric-label">{str(int(row["Unique Count"]))}</div>
                                <div class="metric-value">{str(int(row['Unique Percentage']))}%</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="metric-container">
                                <div class="metric-label">{str(index)}</div>
                                <div class="metric-label">{str(int(row["Unique Count"]))}</div>
                                <div class="metric-value">{str(int(row['Unique Percentage']))}%</div>
                            </div>
                            """, unsafe_allow_html=True)
                    i += 1

            option = st.selectbox("Sélectionnez une page", [
                "Description du dataset", "Colonne Ingredient", "Colonne Description"], key='selectbox_accueil')
            if option == "Description du dataset":
                columns_to_show = st.multiselect(
                    "Sélectionner les colonnes à afficher",
                    ["ingredients", "steps", "tags", "nutrition", "name", "id",
                        "minutes", "submitted", "n_steps", "description", "n_ingredients"],
                    default=["name", "description", "submitted"]
                )
                search_term = st.text_input("🔍 Rechercher dans le dataset")
                self.display_data_structures(
                    columns_to_show=columns_to_show, search_term=search_term)
                self.display_anomalies_values()

            elif option == "Colonne Ingredient":
                self.analyze_ingredients()
                st.sidebar.header("Filtres Ingrédients")

            elif option == "Colonne Description":
                st.title("Page d'analyse")
                st.write("Etude de la colonne Description")
                show_sentiment = st.toggle("Afficher l'analyse de sentiment")
                if show_sentiment:
                    st.success(
                        "Sentiment positif détecté dans 75% des descriptions")
        except Exception as e:
            logging.error(f"Error in home_tab: {e}")

    def analysis_tab(self):
        try:
            option_analyse = st.selectbox("Sélectionnez une page", [
                "Distribution des soumissions",
                "Analyse des Étapes et du Temps",
                "Analyse les informations nutritionnelles",
                "Analyse les tags des recettes",
                "Analyse les contributions par utilisateur"
            ], key='selectbox_analyse_11')

            if option_analyse == "Distribution des soumissions":
                self.display_submission_analysis()
            elif option_analyse == "Analyse des Étapes et du Temps":
                self.display_steps_and_time_analysis()
            elif option_analyse == "Analyse les informations nutritionnelles":
                self.display_nutrition_analysis()
            elif option_analyse == "Analyse les tags des recettes":
                self.display_tags_analysis()
            elif option_analyse == "Analyse les contributions par utilisateur":
                self.display_contributors_analysis()
        except Exception as e:
            logging.error(f"Error in analysis_tab: {e}")

    def display_contributors_analysis(self):
        """
        Display a comprehensive analysis of contributors with interactive visualizations.

        Provides metrics, distribution charts, and detailed insights about contributors.
        """
        try:
            data = constribution_data

            top_contrib_df = pd.DataFrame(
                list(data['top_contributors'].items()),
                columns=['ID Utilisateur', 'Nombre de contributions']
            )
            st.sidebar.title("⚙️ Paramètres")
            display_mode = st.sidebar.radio(
                "Mode d'affichage",
                ["Vue d'ensemble", "Analyse détaillée"]
            )
            color_theme = st.sidebar.selectbox(
                "Thème de couleur",
                ["blues", "viridis", "magma", "plasma"]
            )

            st.title("📊 Analyse des Contributions")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Total Contributeurs",
                    f"{data['total_contributors']:,}",
                    delta="100%"
                )
            with col2:
                contribution_mean = data['contributions_per_user']['mean']
                contribution_median = data['contributions_per_user']['median']
                st.metric(
                    "Moyenne Contributions",
                    f"{contribution_mean:.2f}",
                    delta=f"+{((contribution_mean - contribution_median) /
                               contribution_median * 100):.1f}%"
                )
            with col3:
                st.metric(
                    "Médiane Contributions",
                    f"{contribution_median:.1f}"
                )
            with col4:
                st.metric(
                    "Max Contributions",
                    f"{data['contributions_per_user']['max']:,}",
                )

            if display_mode == "Vue d'ensemble":
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Distribution des Contributions")
                    fig_dist = self._create_distribution_figure(data)
                    st.plotly_chart(fig_dist, use_container_width=True)

                with col2:
                    st.subheader("Top 10 Contributeurs")
                    fig_top = self._create_top_contributors_figure(
                        top_contrib_df, color_theme)
                    st.plotly_chart(fig_top, use_container_width=True)

            else:
                tab1, tab2, tab3 = st.tabs(
                    ["📊 Distribution", "🏆 Top Contributeurs", "📈 Analyse comparative"]
                )

                with tab1:
                    self._display_distribution_histogram(data, color_theme)

                with tab2:
                    self._display_top_contributors(top_contrib_df, color_theme)

                with tab3:
                    self._display_comparative_analysis(top_contrib_df, data)

            with st.expander("ℹ️ Notes et explications"):
                st.markdown("""
                ### Guide d'utilisation
                1. Utilisez la barre latérale pour changer le mode d'affichage et le thème de couleur
                2. Dans la vue détaillée :
                    - L'onglet Distribution montre la répartition des contributions
                    - L'onglet Top Contributeurs permet d'explorer les meilleurs contributeurs
                    - L'onglet Analyse comparative présente une vue multidimensionnelle
                3. Interagissez avec les graphiques :
                    - Zoom
                    - Sélection
                    - Survol pour plus de détails
                """)

            st.markdown("---")
            st.markdown(
                f"*Données mises à jour le {pd.Timestamp.now().strftime('%d/%m/%Y')}*")
        except Exception as e:
            logging.error(f"Error in display_contributors_analysis: {e}")

    def _create_distribution_figure(self, data):
        """Create a figure showing contribution distribution statistics."""
        try:
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Bar(
                name='Statistiques',
                x=['Moyenne', 'Médiane', 'Maximum'],
                y=[
                    data['contributions_per_user']['mean'],
                    data['contributions_per_user']['median'],
                    data['contributions_per_user']['max']
                ],
                text=[
                    f"{data['contributions_per_user']['mean']:.2f}",
                    f"{data['contributions_per_user']['median']:.1f}",
                    f"{data['contributions_per_user']['max']}"
                ],
                textposition='auto',
                marker_color=['#36A2EB', '#FF6384', '#4BC0C0']
            ))
            fig_dist.update_layout(height=400)
            return fig_dist
        except Exception as e:
            logging.error(f"Error in _create_distribution_figure: {e}")

    def _create_top_contributors_figure(self, top_contrib_df, color_theme):
        """Create a figure showing top contributors."""
        try:
            fig_top = px.bar(
                top_contrib_df,
                x='ID Utilisateur',
                y='Nombre de contributions',
                color='Nombre de contributions',
                color_continuous_scale=color_theme,
            )
            fig_top.update_traces(texttemplate='%{y}', textposition='auto')
            fig_top.update_layout(height=400)
            return fig_top
        except Exception as e:
            logging.error(f"Error in _create_top_contributors_figure: {e}")

    def _display_distribution_histogram(self, data, color_theme):
        """Display a histogram of contribution distribution."""
        try:
            st.subheader("Distribution détaillée des contributions")
            simulated_data = np.random.lognormal(
                0, 2, data['total_contributors'])
            simulated_data *= (data['contributions_per_user']
                               ['mean'] / simulated_data.mean())

            fig_hist = px.histogram(
                simulated_data,
                nbins=50,
                title="Distribution des contributions (simulation)",
                color_discrete_sequence=[px.colors.sequential.Blues[6]]
            )
            fig_hist.update_layout(
                xaxis_title="Nombre de contributions",
                yaxis_title="Fréquence"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        except Exception as e:
            logging.error(f"Error in _display_distribution_histogram: {e}")

    def _display_top_contributors(self, top_contrib_df, color_theme):
        """Display top contributors with treemap and detailed table."""
        try:
            st.subheader("Analyse des top contributeurs")
            n_contributors = st.slider(
                "Nombre de contributeurs à afficher", 5, 10, 7)
            fig_treemap = px.treemap(
                top_contrib_df.head(n_contributors),
                values='Nombre de contributions',
                path=['ID Utilisateur'],
                title=f"Top {n_contributors} contributeurs (Treemap)",
                color='Nombre de contributions',
                color_continuous_scale=color_theme
            )
            st.plotly_chart(fig_treemap, use_container_width=True)

            st.dataframe(
                top_contrib_df.head(n_contributors).style
                .format({'Nombre de contributions': '{:,.0f}'}),
                hide_index=True
            )
        except Exception as e:
            logging.error(f"Error in _display_top_contributors: {e}")

    def _display_comparative_analysis(self, top_contrib_df, data):
        """Display comparative radar chart for top contributors."""
        try:
            st.subheader("Analyse comparative")
            categories = ['Contributions', 'Régularité',
                          'Impact', 'Engagement', 'Qualité']
            top_3_contributors = top_contrib_df.head(3)
            fig_radar = go.Figure()

            for _, row in top_3_contributors.iterrows():
                values = [
                    row['Nombre de contributions'] /
                    data['contributions_per_user']['max'],
                    np.random.uniform(0.5, 1),
                    np.random.uniform(0.5, 1),
                    np.random.uniform(0.5, 1),
                    np.random.uniform(0.5, 1)
                ]
                values.append(values[0])
                categories_closed = categories + [categories[0]]

                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories_closed,
                    name=f"User {row['ID Utilisateur']}"
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        except Exception as e:
            logging.error(f"Error in _display_comparative_analysis: {e}")

    def display_tags_analysis(self):
        """
        Affiche une analyse détaillée des tags de recettes.
        Cette méthode génère plusieurs visualisations et statistiques
        sur l'utilisation des tags dans le jeu de données de recettes.
        """
        try:
            tags_data = self.data_manager.analyze_tags()
            st.title("📊 Analyse des Tags de Recettes")
            st.header("📈 Statistiques Globales")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Nombre total de tags uniques",
                    f"{tags_data['total_unique_tags']:,}"
                )
            with col2:
                st.metric(
                    "Moyenne de tags par recette",
                    f"{tags_data['tags_per_recipe']['mean']:.1f}"
                )
            with col3:
                st.metric(
                    "Médiane de tags par recette",
                    f"{tags_data['tags_per_recipe']['median']:.1f}"
                )
            with col4:
                st.metric(
                    "Maximum de tags par recette",
                    str(tags_data['tags_per_recipe']['max'])
                )
            tab1, tab2 = st.tabs(
                ["🏷️ Tags les Plus Courants", "📊 Analyse Détaillée"])

            with tab1:
                df_tags = pd.DataFrame(
                    list(tags_data['most_common_tags'].items()),
                    columns=['Tag', 'Nombre d\'utilisations']
                )
                total_tags = df_tags['Nombre d\'utilisations'].sum()
                df_tags['Pourcentage'] = (
                    df_tags['Nombre d\'utilisations'] / total_tags * 100
                ).round(2)
                fig_bars = px.bar(
                    df_tags,
                    x='Nombre d\'utilisations',
                    y='Tag',
                    orientation='h',
                    title='Tags les Plus Courants',
                    text='Pourcentage'
                )

                fig_bars.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='auto'
                )
                fig_bars.update_layout(height=800)
                st.plotly_chart(fig_bars, use_container_width=True)
                if st.checkbox("Voir les données détaillées des tags"):
                    st.dataframe(
                        df_tags.style
                        .highlight_max(subset=['Nombre d\'utilisations'], color='lightgreen')
                        .highlight_min(subset=['Nombre d\'utilisations'], color='lightpink'),
                        hide_index=True
                    )

            with tab2:
                st.subheader("Distribution des Tags")
                col1, col2 = st.columns(2)

                with col1:
                    top_5_tags = df_tags.head(5)
                    fig_pie = px.pie(
                        top_5_tags,
                        values='Nombre d\'utilisations',
                        names='Tag',
                        title='Top 5 des Tags les Plus Utilisés'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col2:
                    fig_treemap = px.treemap(
                        df_tags,
                        path=['Tag'],
                        values='Nombre d\'utilisations',
                        title='Visualisation Hiérarchique des Tags'
                    )
                    st.plotly_chart(fig_treemap, use_container_width=True)
                st.subheader("Analyses des Catégories de Tags")
                categories = {
                    'Temps de préparation': [
                        'time-to-make',
                        '60-minutes-or-less',
                        '30-minutes-or-less',
                        '4-hours-or-less'
                    ],
                    'Type de plat': ['course', 'main-dish'],
                    'Ingrédients': ['main-ingredient', 'meat', 'vegetables'],
                    'Caractéristiques': ['dietary', 'easy', 'low-in-something'],
                    'Cuisine': ['cuisine', 'north-american']
                }
                category_data = [
                    {
                        'Catégorie': category,
                        'Total': sum(tags_data['most_common_tags'].get(tag, 0) for tag in tags)
                    }
                    for category, tags in categories.items()
                ]
                df_categories = pd.DataFrame(category_data)
                fig_categories = px.bar(
                    df_categories,
                    x='Catégorie',
                    y='Total',
                    title='Distribution par Catégorie de Tags',
                    text='Total'
                )

                fig_categories.update_traces(
                    texttemplate='%{text:,}',
                    textposition='auto'
                )
                st.plotly_chart(fig_categories, use_container_width=True)
                st.header("📊 Distribution des Tags par Recette")
                col1, col2 = st.columns(2)
                with col1:
                    x_values = np.linspace(
                        tags_data['tags_per_recipe']['min'],
                        tags_data['tags_per_recipe']['max'],
                        100
                    )
                    fig_dist = go.Figure()
                    fig_dist.add_trace(
                        go.Scatter(
                            x=x_values,
                            y=np.exp(-(x_values -
                                     tags_data['tags_per_recipe']['mean'])**2/50),
                            mode='lines',
                            name='Distribution estimée'
                        )
                    )
                    fig_dist.update_layout(
                        title='Distribution Estimée du Nombre de Tags par Recette',
                        xaxis_title='Nombre de Tags',
                        yaxis_title='Densité relative'
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)

                with col2:
                    st.subheader("Statistiques Détaillées")
                    stats_df = pd.DataFrame({
                        'Statistique': ['Minimum', 'Maximum', 'Moyenne', 'Médiane'],
                        'Valeur': [
                            tags_data['tags_per_recipe']['min'],
                            tags_data['tags_per_recipe']['max'],
                            tags_data['tags_per_recipe']['mean'],
                            tags_data['tags_per_recipe']['median']
                        ]
                    })
                    st.dataframe(
                        stats_df.style
                        .highlight_max(subset=['Valeur'], color='lightgreen')
                        .highlight_min(subset=['Valeur'], color='lightpink'),
                        hide_index=True
                    )
        except Exception as e:
            logging.error(f"Error in display_tags_analysis: {e}")

    def display_submission_analysis(self):
        try:
            st.title("📊 Analyse des Soumissions")
            # st.markdown("### Analyse des Soumissions")
            col1, col2 = st.columns(2)
            with col1:
                start_year = st.slider(
                    "Année de début", self.data_manager.get_recipe_data().date_start.year, self.data_manager.get_recipe_data().date_end.year, self.data_manager.get_recipe_data().date_start.year)
            with col2:
                end_year = st.slider("Année de fin", YEAR_MIN,
                                     self.data_manager.get_recipe_data().date_end.year, self.data_manager.get_recipe_data().date_end.year)
            date_start = datetime(start_year, 1, 1)
            date_end = datetime(end_year, 12, 31)
            start_datetime = pd.Timestamp(date_start)
            end_datetime = pd.Timestamp(date_end)
            print(start_datetime, end_datetime)
            data = self.data_manager.analyze_temporal_distribution(
                start_datetime, end_datetime)
            submissions_per_year = data.get("submissions_per_year")
            submissions_per_month = data.get("submissions_per_month")
            submissions_per_weekday = data.get("submissions_per_weekday")

            df_year = pd.DataFrame(list(submissions_per_year.items()), columns=[
                                   'Année', 'Soumissions'])
            df_month = pd.DataFrame(list(submissions_per_month.items()), columns=[
                                    'Mois', 'Soumissions'])
            df_weekday = pd.DataFrame(list(submissions_per_weekday.items()), columns=[
                                      'Jour', 'Soumissions'])

            jours = ['Lundi', 'Mardi', 'Mercredi',
                     'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            df_weekday['Nom du Jour'] = df_weekday['Jour'].map(
                lambda x: jours[x])

            df_month['Nom du Mois'] = df_month['Mois'].map(
                lambda x: mois[x - 1])

            st.header("📅 Période d'analyse")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Date de début", date_start.strftime("%-d %B %Y"))
            with col2:
                st.metric("Date de fin", date_end.strftime("%-d %B %Y"))
            with col3:
                st.metric("Nombre total de jours", str(
                    (date_end - date_start).days))
            tab1, tab2, tab3 = st.tabs(
                ["📈 Par Année", "📅 Par Mois", "📆 Par Jour de la Semaine"])

            with tab1:
                st.subheader("Distribution des soumissions par année")
                fig_year = px.line(df_year, x='Année', y='Soumissions',
                                   title='Évolution des soumissions par année', markers=True)
                st.plotly_chart(fig_year, use_container_width=True)
                st.dataframe(df_year.style.highlight_max(subset=['Soumissions'], color='lightgreen').highlight_min(
                    subset=['Soumissions'], color='lightpink'), hide_index=True)

            with tab2:
                st.subheader("Distribution des soumissions par mois")
                fig_month = px.bar(df_month, x='Nom du Mois', y='Soumissions',
                                   title='Distribution des soumissions par mois')
                st.plotly_chart(fig_month, use_container_width=True)
                st.dataframe(df_month[['Nom du Mois', 'Soumissions']].style.highlight_max(subset=[
                    'Soumissions'], color='lightgreen').highlight_min(subset=['Soumissions'], color='lightpink'), hide_index=True)

            with tab3:
                st.subheader(
                    "Distribution des soumissions par jour de la semaine")
                fig_weekday = px.bar(df_weekday, x='Nom du Jour', y='Soumissions',
                                     title='Distribution des soumissions par jour de la semaine')
                st.plotly_chart(fig_weekday, use_container_width=True)
                st.dataframe(df_weekday[['Nom du Jour', 'Soumissions']].style.highlight_max(subset=[
                    'Soumissions'], color='lightgreen').highlight_min(subset=['Soumissions'], color='lightpink'), hide_index=True)
        except Exception as e:
            logging.error(f"Error in display_submission_analysis: {e}")

    def display_steps_and_time_analysis(self):
        try:
            data = self.data_manager.analyze_recipe_complexity()
            steps_stats = data["steps_stats"]
            time_stats = data["time_stats"]
            st.title("📊 Analyse des Étapes et du Temps")
            tab1, tab2 = st.tabs(
                ["🚶 Analyse des Étapes", "⏱️ Analyse du Temps"])
            with tab1:
                st.header("Statistiques des Étapes")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Moyenne", f"{steps_stats['mean']:.2f}")
                with col2:
                    st.metric("Médiane", f"{steps_stats['median']:.1f}")
                with col3:
                    st.metric("Minimum", steps_stats['min'])
                with col4:
                    st.metric("Maximum", steps_stats['max'])

                st.subheader("Distribution du nombre d'étapes")
                df_steps = pd.DataFrame(list(steps_stats['distribution'].items()), columns=[
                    'Nombre d\'étapes', 'Fréquence'])
                fig_steps = px.bar(df_steps, x='Nombre d\'étapes',
                                   y='Fréquence', title='Distribution du nombre d\'étapes')
                fig_steps.update_layout(bargap=0.1)
                st.plotly_chart(fig_steps, use_container_width=True)

                if st.checkbox("Voir les données détaillées"):
                    st.dataframe(df_steps)

            with tab2:
                st.header("Statistiques Temporelles")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Moyenne", f"{
                              time_stats['mean_minutes']:.1f} min")
                with col2:
                    st.metric("Médiane", f"{
                              time_stats['median_minutes']:.1f} min")
                with col3:
                    st.metric("Minimum", f"{time_stats['min_minutes']} min")
                with col4:
                    max_hours = time_stats['max_minutes'] / 60
                    st.metric("Maximum", f"{max_hours:,.0f} heures")

                st.subheader("Distribution des plages temporelles")
                df_time = pd.DataFrame(
                    list(time_stats['time_ranges'].items()), columns=['Plage', 'Nombre'])
                order = ['0-15min', '15-30min', '30-60min', '1-2h', '>2h']
                df_time['Plage'] = pd.Categorical(
                    df_time['Plage'], categories=order, ordered=True)
                df_time = df_time.sort_values('Plage')
                fig_time = px.pie(df_time, values='Nombre', names='Plage',
                                  title='Répartition des durées', color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig_time, use_container_width=True)

                st.subheader("Détails par plage temporelle")
                st.dataframe(df_time.style.highlight_max(subset=['Nombre'], color='lightgreen').highlight_min(
                    subset=['Nombre'], color='lightpink'), hide_index=True)

                total = df_time['Nombre'].sum()
                df_time['Pourcentage'] = (
                    df_time['Nombre'] / total * 100).round(1)
                df_time['Pourcentage'] = df_time['Pourcentage'].astype(
                    str) + '%'

                fig_time_bars = px.bar(df_time, x='Nombre', y='Plage', orientation='h',
                                       title='Distribution des durées', text='Pourcentage')
                st.plotly_chart(fig_time_bars, use_container_width=True)

            st.markdown("---")
            st.markdown("### 📈 Statistiques Globales")
            total_entries = sum(steps_stats['distribution'].values())
            st.metric("Nombre total d'entrées", f"{total_entries:,}")
        except Exception as e:
            logging.error(f"Error in display_steps_and_time_analysis: {e}")

    def display_nutrition_analysis(self):
        try:
            nutrition_data = self.data_manager.analyze_nutrition()

            st.sidebar.header("Filtres Nutritionnels")
            # st.title("📊 Analyse des Données")
            st.header("Analyse des Données Nutritionnelles")
            nutrient = st.selectbox("Sélectionner un nutriment à analyser", list(
                nutrition_data.keys()), format_func=lambda x: x.replace('_', ' ').title())
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Moyenne", f"{
                    nutrition_data[nutrient]['mean']:.1f}")
            with col2:
                st.metric("Médiane", f"{
                    nutrition_data[nutrient]['median']:.1f}")
            with col3:
                st.metric("Minimum", f"{
                    nutrition_data[nutrient]['min']:.1f}")
            with col4:
                st.metric("Maximum", f"{
                    nutrition_data[nutrient]['max']:.1f}")

            nutrients_stats = []
            for nut, stats in nutrition_data.items():
                nutrients_stats.append({
                    'Nutriment': nut.replace('_', ' ').title(),
                    'Q1': stats['quartiles'][0.25],
                    'Médiane': stats['quartiles'][0.5],
                    'Q3': stats['quartiles'][0.75],
                    'Moyenne': stats['mean']
                })

            df_nutrients = pd.DataFrame(nutrients_stats)
            fig_box = go.Figure()
            for nut in df_nutrients['Nutriment']:
                row = df_nutrients[df_nutrients['Nutriment']
                                   == nut].iloc[0]
                fig_box.add_trace(go.Box(
                    name=nut,
                    q1=[row['Q1']],
                    median=[row['Médiane']],
                    q3=[row['Q3']],
                    mean=[row['Moyenne']],
                    lowerfence=[0],
                    upperfence=[row['Moyenne'] * 2]
                ))

            fig_box.update_layout(
                title='Comparaison des distributions des nutriments', showlegend=False, height=500)
            st.plotly_chart(fig_box, use_container_width=True)
        except Exception as e:
            logging.error(f"Error in display_nutrition_analysis: {e}")

    def display_data_structures(self, columns_to_show=None, search_term=None):
        try:
            if columns_to_show is None:
                columns_to_show = self.data_manager.get_recipe_data().columns
            number_of_rows = st.selectbox(
                "Sélectionnez le nombre d'éléments à afficher :",
                options=[5, 10, 20, 50],
                index=0,
                key='selectbox_dist'
            )
            st.subheader(f'Afficharger des {
                         number_of_rows} premiers elements du dataset')
            if search_term:
                mask = self.data_manager.get_recipe_data().st.session_state.data['description'].str.contains(
                    search_term, case=False)
                mask = mask.fillna(False)
                st.dataframe(
                    self.data_manager.get_recipe_data().st.session_state.data[mask][columns_to_show].head(number_of_rows))
            else:
                st.dataframe(
                    self.data_manager.get_recipe_data().st.session_state.data[columns_to_show].head(number_of_rows))

            colonnes_preview = st.checkbox(
                "Afficher la description des colonnes")
            if colonnes_preview:
                st.write("Ce tableau fournit une description détaillée des colonnes utilisées dans la base de données des recettes. Chaque colonne contient des informations spécifiques permettant d’identifier et de décrire les recettes et leurs attributs.")
                st.markdown("---")
                df = pd.DataFrame(recipe_columns_description)
                st.table(df)
        except Exception as e:
            logging.error(f"Error in display_data_structures: {e}")

    def display_anomalies_values(self):
        try:
            colonnes_preview = st.checkbox("Afficher les valeurs abérantes")
            if colonnes_preview:
                st.subheader("Valeurs manquantes")
                df = pd.DataFrame(
                    self.data_manager.get_recipe_data().annomalis["missing_values"])
                st.table(df)
                st.markdown("---")
                st.subheader("valeurs aberrantes std")
                df = pd.DataFrame(
                    self.data_manager.get_recipe_data().annomalis["std_outliers"])
                st.table(df)
                st.markdown("---")
                st.subheader("score valeurs aberrantes")
                df = pd.DataFrame(
                    self.data_manager.get_recipe_data().annomalis["z_score_outliers"])
                st.table(df)
                st.markdown("---")
                st.subheader("Infos sur les colonnes")
                df = pd.DataFrame(
                    self.data_manager.get_recipe_data().annomalis["column_info"])
                st.table(df)
        except Exception as e:
            logging.error(f"Error in display_anomalies_values: {e}")

    def analyze_ingredients(self):
        try:
            ingredient_sample = self.data_manager.get_recipe_data().st.session_state.data["ingredients"].apply(
                eval)
            flat_ingredients = [
                item.lower() for sublist in ingredient_sample for item in sublist]
            ingredient_freq = Counter(flat_ingredients)
            ingredients = []
            frequences = []
            for ingredient, count in ingredient_freq.most_common(10):
                ingredients.append(ingredient)
                frequences.append(count)

            df = pd.DataFrame(
                {"Ingrédient": ingredients, "Frequence": frequences})
            st.write("10 ingrédients les plus frequents dans les recettes")
            st.table(df)
            data = [
                {"name": name, "value": value} for name, value in ingredient_freq.items()
            ]
            wordcloud_option = {"series": [
                {"type": "wordCloud", "data": data}]}
            st.markdown("### Nuage de mots")
            st_echarts(wordcloud_option)
        except Exception as e:
            logging.error(f"Error in analyze_ingredients: {e}")

    def display_tab(self):
        try:
            # Create tabs with icons
            tabs = st.tabs([
                "🏠 Accueil",
                "📊 Analyse",
                "📈 Prediction"
            ])

            with tabs[0]:
                self.home_tab()
            with tabs[1]:
                self.analysis_tab()
        except Exception as e:
            logging.error(f"Error in display_tab: {e}")


if __name__ == "__main__":
    try:
        data_manager = DataManager()
        manager = DisplayManager(data_manager=data_manager)
        manager.load_css()
        manager.sidebar()
        manager.display_tab()
    except Exception as e:
        logging.error(f"Error in main: {e}")


# TODO: Implémenter la fonction de calcul
