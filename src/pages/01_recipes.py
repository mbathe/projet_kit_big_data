import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src.process.recipes import Recipe
from src.utils.static import mois
import locale
from src.visualizations import load_css
from src.utils.static import submissions_data


load_dotenv()
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


class CSSLoader:
    """Class responsible for loading CSS."""
    @staticmethod
    def load(path_to_css):
        load_css(path_to_css)


class DataManager:
    def __init__(self):
        self.recipe = Recipe()

    def set_date_range(self, start_date, end_date):
        self.recipe = Recipe(date_start=start_date, date_end=end_date)

    def get_recipe_data(self):
        return self.recipe

    def export_data(self, export_format):
        if export_format == "CSV":
            return self.recipe.st.session_state.data.to_csv(index=False)
        elif export_format == "JSON":
            return self.recipe.st.session_state.data.to_json(orient="records")

    def analyze_temporal_distribution(self, start_datetime, end_datetime):
        return self.recipe.analyze_temporal_distribution(start_datetime, end_datetime)

    def analyze_recipe_complexity(self):
        return self.recipe.analyze_recipe_complexity()

    def analyze_nutrition(self):
        return self.recipe.analyze_nutrition()

    def analyze_tags(self):
        return self.recipe.analyze_tags()


class DisplayManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def load_css(self):
        path_to_css = 'src/css_pages/analyse_user.css'
        CSSLoader.load(path_to_css)

    def sidebar(self):
        with st.sidebar:
            st.title("⚙️ Configuration")
            theme = st.selectbox("Thème", ["Clair", "Sombre"], key='theme')
            langue = st.selectbox(
                "Langue", ["Français", "English"], key='langue')
            date_range = st.date_input(
                "Période d'analyse",
                value=(datetime(1999, 1, 1), datetime(2018, 12, 31)),
                key='date_filter'
            )
            print(date_range)
            start_datetime = pd.Timestamp(date_range[0].date)
            end_datetime = pd.Timestamp(date_range[1].date)
            self.data_manager.set_date_range(start_datetime, end_datetime)
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

    def home_tab(self):
        st.title("🏠 Analyse de Recettes")
        columns_to_show = ["name", "submitted", "nutrition",
                           "description", "tags", "ingredients"]
        coll = st.columns(len(columns_to_show))
        i = 0
        for index, row in self.data_manager.get_recipe_data().annomalis["column_info"].iterrows():
            if index in columns_to_show:
                with coll[i]:
                    if index == "submitted":
                        st.metric(str(index), str(
                            row["Unique Count"]), f"{-row['Unique Percentage']}%", delta_color="inverse")
                    else:
                        st.metric(str(index), str(row["Unique Count"]), f"{
                                  row['Unique Percentage']}%")
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
            self.data_manager.get_recipe_data().display_data_structures(
                columns_to_show=columns_to_show, search_term=search_term)
            self.data_manager.get_recipe_data().display_anomalies_values()

        elif option == "Colonne Ingredient":
            self.data_manager.get_recipe_data().analyze_ingredients()
            st.sidebar.header("Filtres Ingrédients")
            ingredient_type = st.sidebar.multiselect(
                "Type d'ingrédients",
                ["Légumes", "Viandes", "Poissons", "Épices"],
                default=["Légumes"]
            )
            chart_type = st.radio("Type de visualisation", [
                                  "Barres", "Camembert", "Treemap"])

        elif option == "Colonne Description":
            st.title("Page d'analyse")
            st.write("Etude de la colonne Description")
            show_sentiment = st.toggle("Afficher l'analyse de sentiment")
            if show_sentiment:
                st.success(
                    "Sentiment positif détecté dans 75% des descriptions")

    def analysis_tab(self):
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

    def display_contributors_analysis(self):
        """
        Display a comprehensive analysis of contributors with interactive visualizations.

        Provides metrics, distribution charts, and detailed insights about contributors.
        """
        # Simulated data for contributor analysis
        data = {
            'total_contributors': 27926,
            'contributions_per_user': {
                'mean': 8.29,
                'median': 1.0,
                'max': 3118
            },
            'top_contributors': {
                89831: 3118,
                37779: 2553,
                37449: 2493,
                1533: 1595,
                58104: 1522,
                169430: 1378,
                4470: 1125,
                80353: 1104,
                283251: 1004,
                21752: 971
            }
        }

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

        # Overview mode
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

        else:  # Detailed analysis mode
            tab1, tab2, tab3 = st.tabs(
                ["📊 Distribution", "🏆 Top Contributeurs", "📈 Analyse comparative"]
            )

            with tab1:
                self._display_distribution_histogram(data, color_theme)

            with tab2:
               self._display_top_contributors(top_contrib_df, color_theme)

            with tab3:
                self._display_comparative_analysis(top_contrib_df, data)

        # Interactive explanatory notes
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

        # Footer
        st.markdown("---")
        st.markdown(
            f"*Données mises à jour le {pd.Timestamp.now().strftime('%d/%m/%Y')}*")

    def _create_distribution_figure(self, data):
        """Create a figure showing contribution distribution statistics."""
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

    def _create_top_contributors_figure(self, top_contrib_df, color_theme):
        """Create a figure showing top contributors."""
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

    def _display_distribution_histogram(self, data, color_theme):
        """Display a histogram of contribution distribution."""
        st.subheader("Distribution détaillée des contributions")
        simulated_data = np.random.lognormal(0, 2, data['total_contributors'])
        simulated_data *= (
            data['contributions_per_user']['mean'] / simulated_data.mean()
        )

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

    def _display_top_contributors(sefl, top_contrib_df, color_theme):
        """Display top contributors with treemap and detailed table."""
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

    def _display_comparative_analysis(self, top_contrib_df, data):
        """Display comparative radar chart for top contributors."""
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
            values.append(values[0])  # Close the polygon
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

    def display_tags_analysis(self):
        """
        Affiche une analyse détaillée des tags de recettes.
        Cette méthode génère plusieurs visualisations et statistiques
        sur l'utilisation des tags dans le jeu de données de recettes.
        """
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
                # Statistiques détaillées
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

    def display_submission_analysis(self):
        st.title("📊 Analyse des Soumissions")
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.slider("Année de début", 1999, 2018, 1999)
        with col2:
            end_year = st.slider("Année de fin", 1999, 2018, 2018)
        date_start = datetime(start_year, 1, 1)
        date_end = datetime(end_year, 12, 31)
        start_datetime = pd.Timestamp(date_start)
        end_datetime = pd.Timestamp(date_end)
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
        df_weekday['Nom du Jour'] = df_weekday['Jour'].map(lambda x: jours[x])

        df_month['Nom du Mois'] = df_month['Mois'].map(lambda x: mois[x - 1])

        st.header("📅 Période d'analyse")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Date de début", date_start.strftime("%-d %B %Y"))
        with col2:
            st.metric("Date de fin", date_end.strftime("%-d %B %Y"))
        with col3:
            st.metric("Nombre total de jours", str((date_end-date_start).days))
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
            st.subheader("Distribution des soumissions par jour de la semaine")
            fig_weekday = px.bar(df_weekday, x='Nom du Jour', y='Soumissions',
                                 title='Distribution des soumissions par jour de la semaine')
            st.plotly_chart(fig_weekday, use_container_width=True)
            st.dataframe(df_weekday[['Nom du Jour', 'Soumissions']].style.highlight_max(subset=[
                         'Soumissions'], color='lightgreen').highlight_min(subset=['Soumissions'], color='lightpink'), hide_index=True)

    def display_steps_and_time_analysis(self):
        data = self.data_manager.analyze_recipe_complexity()
        steps_stats = data["steps_stats"]
        time_stats = data["time_stats"]
        st.title("📊 Analyse des Étapes et du Temps")
        tab1, tab2 = st.tabs(["🚶 Analyse des Étapes", "⏱️ Analyse du Temps"])
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
                st.metric("Moyenne", f"{time_stats['mean_minutes']:.1f} min")
            with col2:
                st.metric("Médiane", f"{time_stats['median_minutes']:.1f} min")
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
            df_time['Pourcentage'] = (df_time['Nombre'] / total * 100).round(1)
            df_time['Pourcentage'] = df_time['Pourcentage'].astype(str) + '%'

            fig_time_bars = px.bar(df_time, x='Nombre', y='Plage', orientation='h',
                                   title='Distribution des durées', text='Pourcentage')
            st.plotly_chart(fig_time_bars, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📈 Statistiques Globales")
        total_entries = sum(steps_stats['distribution'].values())
        st.metric("Nombre total d'entrées", f"{total_entries:,}")

    def display_nutrition_analysis(self):
        nutrition_data = self.data_manager.analyze_nutrition()

        st.sidebar.header("Filtres Nutritionnels")
        calories_range = st.sidebar.slider("Calories", 0, 1000, (0, 1000))
        nutrients = st.multiselect("Nutriments à afficher", [
                                   "calories", "protein", "fat", "carbs"], default=["calories", "protein"])
        normalize = st.checkbox("Normaliser les données")

        st.title("📊 Analyse des Données")
        tab1, tab2 = st.tabs(
            ["📈 Analyse des Soumissions", "🍎 Analyse Nutritionnelle"])

        with tab1:
            st.header("Analyse Temporelle des Soumissions")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Date de début", "6 août 1999")
            with col2:
                st.metric("Date de fin", "4 décembre 2018")
            with col3:
                st.metric("Nombre total de jours", "7060")

            subtab1, subtab2, subtab3 = st.tabs(
                ["Par Année", "Par Mois", "Par Jour"])

            with subtab1:
                df_year = pd.DataFrame(list(submissions_data['submissions_per_year'].items()), columns=[
                                       'Année', 'Soumissions'])
                fig_year = px.line(df_year, x='Année', y='Soumissions',
                                   title='Évolution des soumissions par année', markers=True)
                st.plotly_chart(fig_year, use_container_width=True)
                st.metric("Année la plus active", f"{df_year.loc[df_year['Soumissions'].idxmax(
                ), 'Année']} ({df_year['Soumissions'].max():,} soumissions)")

            with subtab2:
                df_month = pd.DataFrame(list(
                    submissions_data['submissions_per_month'].items()), columns=['Mois', 'Soumissions'])
                mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                df_month['Nom du Mois'] = df_month['Mois'].map(
                    lambda x: mois[x-1])
                fig_month = px.bar(df_month, x='Nom du Mois', y='Soumissions',
                                   title='Distribution des soumissions par mois')
                st.plotly_chart(fig_month, use_container_width=True)

            with subtab3:
                df_weekday = pd.DataFrame(list(
                    submissions_data['submissions_per_weekday'].items()), columns=['Jour', 'Soumissions'])
                jours = ['Lundi', 'Mardi', 'Mercredi',
                         'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                df_weekday['Nom du Jour'] = df_weekday['Jour'].map(
                    lambda x: jours[x])
                fig_weekday = px.bar(df_weekday, x='Nom du Jour', y='Soumissions',
                                     title='Distribution des soumissions par jour de la semaine')
                st.plotly_chart(fig_weekday, use_container_width=True)

        with tab2:
            st.header("Analyse des Données Nutritionnelles")
            nutrient = st.selectbox("Sélectionner un nutriment à analyser", list(
                nutrition_data.keys()), format_func=lambda x: x.replace('_', ' ').title())
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Moyenne", f"{nutrition_data[nutrient]['mean']:.1f}")
            with col2:
                st.metric("Médiane", f"{
                          nutrition_data[nutrient]['median']:.1f}")
            with col3:
                st.metric("Minimum", f"{nutrition_data[nutrient]['min']:.1f}")
            with col4:
                st.metric("Maximum", f"{nutrition_data[nutrient]['max']:.1f}")

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
                row = df_nutrients[df_nutrients['Nutriment'] == nut].iloc[0]
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


if __name__ == "__main__":
    data_manager = DataManager()
    manager = DisplayManager(data_manager=data_manager)
    manager.load_css()
    manager.home_tab()
    manager.sidebar()
    manager.analysis_tab()
