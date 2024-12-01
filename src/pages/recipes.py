
from collections import Counter
import os
from src.visualizations.graphiques import Heatmap
from src.visualizations.graphiques import Histogramme
from src.utils.helper_data import load_dataset
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import re
import streamlit as st
from dotenv import load_dotenv
from streamlit_echarts import st_echarts

import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime



load_dotenv()


recipe_columns_description = {
    "Colonne": [
        "**nom**",
        "**identifiant**",
        "**minutes**",
        "**contributeur_id**",
        "**soumis**",
        "**balises**",
        "**nutrition**",
        "**n_étapes**",
        "**mesures**",
        "**description**"
    ],
    "Description": [
        "Nom de la recette",
        "ID de la recette",
        "Minutes pour préparer la recette",
        "ID utilisateur qui a soumis cette recette",
        "Date à laquelle la recette a été soumise",
        "Balises Food.com pour la recette",
        """Informations nutritionnelles sous la forme `[calories (#), matières grasses totales (PDV), sucre (PDV), sodium (PDV), protéines (PDV), graisses saturées (PDV), glucides (PDV)]` ; 
                    PDV signifie « pourcentage de la valeur quotidienne »""",
        "Nombre d'étapes dans la recette",
        "Texte pour les étapes de la recette, dans l'ordre",
        "Description de la recette"
    ]
}



class Recipe:
    def __init__(self, name="RAW_recipes"):
        self.name = name
        self.initialize_session_state(name)
        self.annomalis = self.preprocess_and_detect_anomalies()
        self.st = st
        self.columns = list(self.st.session_state.data.columns)

    def initialize_session_state(self, name):
        if 'data' not in st.session_state:
            st.session_state.data = load_dataset(dir_name=os.getenv(
                "DIR_DATASET_2"), all_contents=True).get(name)





    def preprocess_and_detect_anomalies(self):

        # Convertir les colonnes appropriées en types de données adaptés
        st.session_state.data['submitted'] = pd.to_datetime(
            st.session_state.data['submitted'])
        st.session_state.data['n_steps'] = st.session_state.data['n_steps'].astype(
            int)
        st.session_state.data['minutes'] = st.session_state.data['minutes'].astype(
            int)

        nutrition_cols = ['calories', 'total_fat', 'sugar',
                          'sodium', 'protein', 'saturated_fat', 'carbohydrates']
        nutrition_cols = []
        # st.session_state.data['nutrition'] = st.session_state.data['nutrition'].apply(eval)

        for col in nutrition_cols:
            st.session_state.data[col] = st.session_state.data['nutrition'].apply(
                lambda x: float(x[nutrition_cols.index(col)]))

        # Détection des anomalies
        anomalies = pd.DataFrame(
            columns=['index', 'column', 'value', 'reason'])

        for col in st.session_state.data.columns:
            null_count = st.session_state.data[col].isnull().sum()
            if null_count > 0:
                anomalies = pd.concat([
                    anomalies,
                    pd.DataFrame({
                        # Utiliser une liste pour respecter la forme
                        'index': ['global'],
                        # Utiliser une liste pour respecter la forme
                        'column': [col],
                        # Utiliser une liste pour respecter la forme
                        'value': [null_count],
                        # Utiliser une liste pour respecter la forme
                        'reason': [f'{null_count} valeurs manquantes']
                    })
                ], ignore_index=True)

        # Vérifier les valeurs extrêmes
        for col in ['minutes', 'n_steps'] + nutrition_cols:
            q1 = st.session_state.data[col].quantile(0.25)
            q3 = st.session_state.data[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Trouver les indices des valeurs extrêmes
            outliers = st.session_state.data[(st.session_state.data[col] < lower_bound) | (
                st.session_state.data[col] > upper_bound)].index

            # Ajouter les anomalies au DataFrame
            for idx in outliers:
                anomalies = pd.concat([
                    anomalies,
                    pd.DataFrame({
                        # Utiliser une liste pour respecter la forme
                        'index': [idx],
                        # Utiliser une liste pour respecter la forme
                        'column': [col],
                        # Utiliser une liste pour respecter la forme
                        'value': [st.session_state.data.loc[idx, col]],
                        # Utiliser une liste pour respecter la forme
                        'reason': ['Valeur extrême']
                    })
                ], ignore_index=True)

        return anomalies


    def display_data_structures(self):
        show_preview = st.checkbox("Afficher un aperçu du dataset")
        if show_preview:
            number_of_rows = st.selectbox(
                "Sélectionnez le nombre d'éléments à afficher :",
                options=[5, 10, 20, 50],
                index=0,  # Valeur par défaut
                key='selectbox_dist'
            )
            st.subheader(f'Afficharger des {
                         number_of_rows} premiers elements du dataset')
            st.dataframe(st.session_state.data.head(number_of_rows))

        colonnes_preview = st.checkbox("Afficher la description des colonnes")
        if colonnes_preview:
            st.write("Ce tableau fournit une description détaillée des colonnes utilisées dans la base de données des recettes. Chaque colonne contient des informations spécifiques permettant d’identifier et de décrire les recettes et leurs attributs.")
            st.markdown("---")  # Séparateur horizontal
            df = pd.DataFrame(recipe_columns_description)
            st.table(df)


    def afficher_correlation(self):
       print()

    @st.cache_data
    def analyze_calorie_distribution(self, calorie_data):
        # Analyse de la distribution des calories
        total_recipes = sum(calorie_data.values())
        percentiles = []
        cumsum = 0

        print("Distribution des calories:")
        print(f"Nombre total de recettes: {total_recipes}")
        print("\nAnalyse par tranches de calories:")

        for range_str, count in calorie_data.items():
            low, high = map(float, range_str.split(' - '))
            percentage = (count / total_recipes) * 100
            cumsum += percentage
            if cumsum in [25, 50, 75]:
                percentiles.append((low, high))

            print(f"{range_str:20} : {count:6d} recettes ({percentage:5.1f}%)")

        return {
            "Q1": percentiles[0] if len(percentiles) > 0 else None,
            "Médiane": percentiles[1] if len(percentiles) > 1 else None,
            "Q3": percentiles[2] if len(percentiles) > 2 else None
        }

    @st.cache_data
    def analyze_techniques(self, technique_data):
        techniques_count = sum(1 for t in technique_data if t == 1)
        return f"Moyenne de {techniques_count} techniques par recette"

    def analyze_ingredients(self, ):
        ingredient_sample = st.session_state.data["ingredients"].apply(eval)
        flat_ingredients = [
            item.lower() for sublist in ingredient_sample for item in sublist]
        ingredient_freq = Counter(flat_ingredients)
        print("\nAnalyse des ingrédients les plus communs:")
        ingredients = []
        frequences = []
        for ingredient, count in ingredient_freq.most_common(10):
            ingredients.append(ingredient)
            frequences.append(count)

        df = pd.DataFrame({"Ingrédient": ingredients, "Frequence": frequences})
        st.write("10 ingrédients les plus frequents dans les recettes")

        st.table(df)
        data = [
            {"name": name, "value": value} for name, value in ingredient_freq.items()
        ]
        wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
        self.st.write("Nuage de mots")
        st_echarts(wordcloud_option)

        return

    def analyze_temporal_distribution(self):
        df = self.st.session_state.data
        df['submitted'] = pd.to_datetime(df['submitted'])
        temporal_stats = {
            'date_min': df['submitted'].min(),
            'date_max': df['submitted'].max(),
            'total_days': (df['submitted'].max() - df['submitted'].min()).days,
            'submissions_per_year': df.groupby(df['submitted'].dt.year).size().to_dict(),
            'submissions_per_month': df.groupby(df['submitted'].dt.month).size().to_dict(),
            'submissions_per_weekday': df.groupby(df['submitted'].dt.dayofweek).size().to_dict()
        }
        # print(temporal_stats)
        return temporal_stats

    def analyze_recipe_complexity(self):
        df = self.st.session_state.data
        """Analyse la complexité des recettes"""
        complexity_stats = {
            'steps_stats': {
                'mean': df['n_steps'].mean(),
                'median': df['n_steps'].median(),
                'min': df['n_steps'].min(),
                'max': df['n_steps'].max(),
                'distribution': df['n_steps'].value_counts().sort_index().to_dict()
            },
            'time_stats': {
                'mean_minutes': df['minutes'].mean(),
                'median_minutes': df['minutes'].median(),
                'min_minutes': df['minutes'].min(),
                'max_minutes': df['minutes'].max(),
                'time_ranges': pd.cut(df['minutes'],
                                      bins=[0, 15, 30, 60, 120, float('inf')],
                                      labels=['0-15min', '15-30min', '30-60min', '1-2h', '>2h']).value_counts().to_dict()
            }
        }
        # print(complexity_stats)
        return complexity_stats

    def word_cloud(self, df):
        """Analyse la complexité des recettes"""

    def analyze_nutrition(self):
        df = self.st.session_state.data
        """Analyse les informations nutritionnelles"""
        # Conversion de la string nutrition en liste de valeurs
        df['nutrition_list'] = df['nutrition'].apply(eval)
        nutrition_columns = ['calories', 'total_fat', 'sugar',
                             'sodium', 'protein', 'saturated_fat', 'carbohydrates']

        nutrition_df = pd.DataFrame(
            df['nutrition_list'].tolist(), columns=nutrition_columns)

        nutrition_stats = {col: {
            'mean': nutrition_df[col].mean(),
            'median': nutrition_df[col].median(),
            'min': nutrition_df[col].min(),
            'max': nutrition_df[col].max(),
            'quartiles': nutrition_df[col].quantile([0.25, 0.5, 0.75]).to_dict()
        } for col in nutrition_columns}

        # print(nutrition_stats)
        return nutrition_stats

    def analyze_tags(self):
        df = self.st.session_state.data
        """Analyse les tags des recettes"""
        # Conversion de la string tags en liste
        df['tags_list'] = df['tags'].apply(eval)

        # Extraction de tous les tags uniques
        all_tags = [tag for tags in df['tags_list'] for tag in tags]
        tag_counts = pd.Series(all_tags).value_counts()

        tag_stats = {
            'total_unique_tags': len(tag_counts),
            'most_common_tags': tag_counts.head(20).to_dict(),
            'tags_per_recipe': {
                'mean': df['tags_list'].str.len().mean(),
                'median': df['tags_list'].str.len().median(),
                'min': df['tags_list'].str.len().min(),
                'max': df['tags_list'].str.len().max()
            }
        }
        print(tag_stats)
        return tag_stats

    def analyze_contributors(self):
        df = self.st.session_state.data
        """Analyse les contributions par utilisateur"""
        contributor_stats = {
            'total_contributors': df['contributor_id'].nunique(),
            'contributions_per_user': {
                'mean': df['contributor_id'].value_counts().mean(),
                'median': df['contributor_id'].value_counts().median(),
                'max': df['contributor_id'].value_counts().max()
            },
            'top_contributors': df['contributor_id'].value_counts().head(10).to_dict()
        }

        print(contributor_stats)
        return contributor_stats

    # Fonction principale d'analyse
    @st.cache_data
    def analyze_recipe_dataset(self):
        """Analyse complète du dataset de recettes"""
        data = self.st.session_state.data
        # Statistiques générales
        general_stats = {
            'total_recipes': len(data),
            'dataset_size_mb': data.memory_usage(deep=True).sum() / 1024 / 1024,
            'columns': list(data.columns),
            'missing_values': data.isnull().sum().to_dict()
        }

        # Analyses spécifiques
        temporal_analysis = self.analyze_temporal_distribution(data)
        complexity_analysis = self.analyze_recipe_complexity(data)
        nutrition_analysis = self.analyze_nutrition(data)
        tag_analysis = self.analyze_tags(data)
        contributor_analysis = self.analyze_contributors(data)

        print({
            'general_stats': general_stats,
            'temporal_analysis': temporal_analysis,
            'complexity_analysis': complexity_analysis,
            'nutrition_analysis': nutrition_analysis,
            'tag_analysis': tag_analysis,
            'contributor_analysis': contributor_analysis
        }
        )

        return {
            'general_stats': general_stats,
            'temporal_analysis': temporal_analysis,
            'complexity_analysis': complexity_analysis,
            'nutrition_analysis': nutrition_analysis,
            'tag_analysis': tag_analysis,
            'contributor_analysis': contributor_analysis
        }








tabs = st.tabs(["Accueil", "Analyse Statistique", "Paramètres"])
recipe = Recipe()
# Onglet Accueil
with tabs[0]:
    option = st.selectbox("Sélectionnez une page", [
        "Description du dataset", "Colonne Ingredient", "Colonne Description"], key='selectbox_accueil')

    if option == "Description du dataset":
        recipe.display_data_structures()
    elif option == "Colonne Ingredient":
        recipe.analyze_ingredients()
    elif option == "Colonne Description":
        st.title("Page d'analyse")
        st.write("Etude de la colonne Description")

# Onglet Analyse Statistique
with tabs[1]:
    # st.title("Analyse")
    # st.write("Analyse des données ici.")
    option_analyse = st.selectbox("Sélectionnez une page", [
                                  "Distribution des soumissions", "Analyse des Étapes et du Temps", "Analyse les informations nutritionnelles", "Analyse les tags des recettes", "Analyse les contributions par utilisateur"], key='selectbox_analyse_11')

    if option_analyse == "Distribution des soumissions":
        data = recipe.analyze_temporal_distribution()
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

        # Ajout des noms des mois
        mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        df_month['Nom du Mois'] = df_month['Mois'].map(lambda x: mois[x - 1])

        # Titre de l'application
        st.title("📊 Analyse des Soumissions")

        st.header("📅 Période d'analyse")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Date de début", "6 août 1999")
        with col2:
            st.metric("Date de fin", "4 décembre 2018")
        with col3:
            st.metric("Nombre total de jours", "7060")

        # Création des onglets de l'analyse
        tab1, tab2, tab3 = st.tabs(
            ["📈 Par Année", "📅 Par Mois", "📆 Par Jour de la Semaine"])

        with tab1:
            st.subheader("Distribution des soumissions par année")
            fig_year = px.line(df_year, x='Année', y='Soumissions',
                               title='Évolution des soumissions par année', markers=True)
            st.plotly_chart(fig_year, use_container_width=True)
            st.dataframe(df_year.style.highlight_max(subset=['Soumissions'], color='lightgreen')
                         .highlight_min(subset=['Soumissions'], color='lightpink'), hide_index=True)

        with tab2:
            st.subheader("Distribution des soumissions par mois")
            fig_month = px.bar(df_month, x='Nom du Mois', y='Soumissions',
                               title='Distribution des soumissions par mois')
            st.plotly_chart(fig_month, use_container_width=True)
            st.dataframe(df_month[['Nom du Mois', 'Soumissions']]
                         .style.highlight_max(subset=['Soumissions'], color='lightgreen')
                         .highlight_min(subset=['Soumissions'], color='lightpink'), hide_index=True)

        with tab3:
            st.subheader("Distribution des soumissions par jour de la semaine")
            fig_weekday = px.bar(df_weekday, x='Nom du Jour', y='Soumissions',
                                 title='Distribution des soumissions par jour de la semaine')
            st.plotly_chart(fig_weekday, use_container_width=True)
            st.dataframe(df_weekday[['Nom du Jour', 'Soumissions']]
                         .style.highlight_max(subset=['Soumissions'], color='lightgreen')
                         .highlight_min(subset=['Soumissions'], color='lightpink'), hide_index=True)

    elif option_analyse == "Analyse des Étapes et du Temps":
       # self.analyze_recipe_dataset()
        print("test")
       # recipe.analyze_recipe_complexity()

        # Configuration de la page

        # Données des étapes
        steps_stats = {
            'mean': 9.7654994668382,
            'median': 9.0,
            'min': 0,
            'max': 145,
            'distribution': {0: 1, 1: 2442, 2: 6982, 3: 11461, 4: 14753, 5: 18047, 6: 19927,
                             7: 20785, 8: 19980, 9: 18265, 10: 16272, 11: 14131, 12: 11940,
                             13: 10137, 14: 8297, 15: 6759, 16: 5522, 17: 4640, 18: 3621,
                             19: 3184, 20: 2468, 21: 2005, 22: 1683, 23: 1334, 24: 1128,
                             25: 926, 26: 791, 27: 654, 28: 545, 29: 428, 30: 364, 31: 298,
                             32: 244, 33: 233, 34: 182, 35: 149, 36: 139, 37: 107, 38: 100,
                             39: 85, 40: 80, 41: 74, 42: 50, 43: 40, 44: 45, 45: 42, 46: 28,
                             47: 30, 48: 27, 49: 30, 50: 15}  # Tronqué pour lisibilité
        }

        # Données temporelles
        time_stats = {
            'mean_minutes': 9398.546009488984,
            'median_minutes': 40.0,
            'min_minutes': 0,
            'max_minutes': 2147483647,
            'time_ranges': {
                '30-60min': 70077,
                '15-30min': 55131,
                '0-15min': 42828,
                '1-2h': 36683,
                '>2h': 25824
            }
        }

        # Titre de l'application
        st.title("📊 Analyse des Étapes et du Temps")

        # Création des onglets
        tab1, tab2 = st.tabs(["🚶 Analyse des Étapes", "⏱️ Analyse du Temps"])

        with tab1:
            st.header("Statistiques des Étapes")

            # Métriques des étapes
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Moyenne", f"{steps_stats['mean']:.2f}")
            with col2:
                st.metric("Médiane", f"{steps_stats['median']:.1f}")
            with col3:
                st.metric("Minimum", steps_stats['min'])
            with col4:
                st.metric("Maximum", steps_stats['max'])

            # Distribution des étapes
            st.subheader("Distribution du nombre d'étapes")
            df_steps = pd.DataFrame(list(steps_stats['distribution'].items()),
                                    columns=['Nombre d\'étapes', 'Fréquence'])

            fig_steps = px.bar(df_steps,
                               x='Nombre d\'étapes',
                               y='Fréquence',
                               title='Distribution du nombre d\'étapes')
            fig_steps.update_layout(bargap=0.1)
            st.plotly_chart(fig_steps, use_container_width=True)

            # Statistiques détaillées
            if st.checkbox("Voir les données détaillées"):
                st.dataframe(df_steps)

        with tab2:
            st.header("Statistiques Temporelles")

            # Métriques temporelles
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

            # Distribution des plages temporelles
            st.subheader("Distribution des plages temporelles")
            df_time = pd.DataFrame(list(time_stats['time_ranges'].items()),
                                   columns=['Plage', 'Nombre'])

            # Réorganiser les plages dans un ordre logique
            order = ['0-15min', '15-30min', '30-60min', '1-2h', '>2h']
            df_time['Plage'] = pd.Categorical(
                df_time['Plage'], categories=order, ordered=True)
            df_time = df_time.sort_values('Plage')

            fig_time = px.pie(df_time,
                              values='Nombre',
                              names='Plage',
                              title='Répartition des durées',
                              color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_time, use_container_width=True)

            # Tableau des données temporelles
            st.subheader("Détails par plage temporelle")
            st.dataframe(df_time.style.highlight_max(subset=['Nombre'], color='lightgreen')
                                .highlight_min(subset=['Nombre'], color='lightpink'),
                         hide_index=True)

            # Calcul des pourcentages
            total = df_time['Nombre'].sum()
            df_time['Pourcentage'] = (df_time['Nombre'] / total * 100).round(1)
            df_time['Pourcentage'] = df_time['Pourcentage'].astype(str) + '%'

            # Graphique en barres horizontal
            fig_time_bars = px.bar(df_time,
                                   x='Nombre',
                                   y='Plage',
                                   orientation='h',
                                   title='Distribution des durées',
                                   text='Pourcentage')
            st.plotly_chart(fig_time_bars, use_container_width=True)

        # Footer avec statistiques globales
        st.markdown("---")
        st.markdown("### 📈 Statistiques Globales")
        total_entries = sum(steps_stats['distribution'].values())
        st.metric("Nombre total d'entrées", f"{total_entries:,}")

    elif option_analyse == "Analyse les informations nutritionnelles":
        # st.title("Page d'analyse")
        # st.write("Etude de la colonne Description")
        recipe.analyze_nutrition()

        # Données des soumissions
        submissions_data = {
            'submissions_per_year': {1999: 2054, 2000: 1038, 2001: 4682, 2002: 20056, 2003: 18000,
                                     2004: 16601, 2005: 23865, 2006: 27260, 2007: 34299, 2008: 30745,
                                     2009: 22547, 2010: 11902, 2011: 7573, 2012: 5187, 2013: 3792,
                                     2014: 1049, 2015: 306, 2016: 204, 2017: 288, 2018: 189},
            'submissions_per_month': {1: 21856, 2: 18536, 3: 20571, 4: 20186, 5: 21684, 6: 18726,
                                      7: 18584, 8: 18866, 9: 18631, 10: 19131, 11: 18771, 12: 16095},
            'submissions_per_weekday': {0: 48087, 1: 42757, 2: 37537, 3: 35823, 4: 29612, 5: 16624, 6: 21197}
        }

        # Données nutritionnelles
        nutrition_data = {
            'calories': {'mean': 473.94, 'median': 313.4, 'min': 0.0, 'max': 434360.2,
                         'quartiles': {0.25: 174.4, 0.5: 313.4, 0.75: 519.7}},
            'total_fat': {'mean': 36.08, 'median': 20.0, 'min': 0.0, 'max': 17183.0,
                          'quartiles': {0.25: 8.0, 0.5: 20.0, 0.75: 41.0}},
            'sugar': {'mean': 84.30, 'median': 25.0, 'min': 0.0, 'max': 362729.0,
                      'quartiles': {0.25: 9.0, 0.5: 25.0, 0.75: 68.0}},
            'sodium': {'mean': 30.15, 'median': 14.0, 'min': 0.0, 'max': 29338.0,
                       'quartiles': {0.25: 5.0, 0.5: 14.0, 0.75: 33.0}},
            'protein': {'mean': 34.68, 'median': 18.0, 'min': 0.0, 'max': 6552.0,
                        'quartiles': {0.25: 7.0, 0.5: 18.0, 0.75: 51.0}},
            'saturated_fat': {'mean': 45.59, 'median': 23.0, 'min': 0.0, 'max': 10395.0,
                              'quartiles': {0.25: 7.0, 0.5: 23.0, 0.75: 52.0}},
            'carbohydrates': {'mean': 15.56, 'median': 9.0, 'min': 0.0, 'max': 36098.0,
                              'quartiles': {0.25: 4.0, 0.5: 9.0, 0.75: 16.0}}
        }

        # Titre de l'application
        st.title("📊 Analyse des Données")

        # Création des onglets principaux
        tab1, tab2 = st.tabs(
            ["📈 Analyse des Soumissions", "🍎 Analyse Nutritionnelle"])

        with tab1:
            st.header("Analyse Temporelle des Soumissions")

            # Métriques générales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Date de début", "6 août 1999")
            with col2:
                st.metric("Date de fin", "4 décembre 2018")
            with col3:
                st.metric("Nombre total de jours", "7060")

            # Sous-onglets pour les différentes vues temporelles
            subtab1, subtab2, subtab3 = st.tabs(
                ["Par Année", "Par Mois", "Par Jour"])

            with subtab1:
                # Analyse par année
                df_year = pd.DataFrame(list(submissions_data['submissions_per_year'].items()),
                                       columns=['Année', 'Soumissions'])

                fig_year = px.line(df_year, x='Année', y='Soumissions',
                                   title='Évolution des soumissions par année',
                                   markers=True)
                st.plotly_chart(fig_year, use_container_width=True)

                # Statistiques annuelles
                st.metric("Année la plus active",
                          f"{df_year.loc[df_year['Soumissions'].idxmax(), 'Année']} "
                          f"({df_year['Soumissions'].max():,} soumissions)")

            with subtab2:
                # Analyse par mois
                df_month = pd.DataFrame(list(submissions_data['submissions_per_month'].items()),
                                        columns=['Mois', 'Soumissions'])
                mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                df_month['Nom du Mois'] = df_month['Mois'].map(
                    lambda x: mois[x-1])

                fig_month = px.bar(df_month, x='Nom du Mois', y='Soumissions',
                                   title='Distribution des soumissions par mois')
                st.plotly_chart(fig_month, use_container_width=True)

            with subtab3:
                # Analyse par jour de la semaine
                df_weekday = pd.DataFrame(list(submissions_data['submissions_per_weekday'].items()),
                                          columns=['Jour', 'Soumissions'])
                jours = ['Lundi', 'Mardi', 'Mercredi',
                         'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                df_weekday['Nom du Jour'] = df_weekday['Jour'].map(
                    lambda x: jours[x])

                fig_weekday = px.bar(df_weekday, x='Nom du Jour', y='Soumissions',
                                     title='Distribution des soumissions par jour de la semaine')
                st.plotly_chart(fig_weekday, use_container_width=True)

        with tab2:
            st.header("Analyse des Données Nutritionnelles")

            # Sélection du nutriment
            nutrient = st.selectbox("Sélectionner un nutriment à analyser",
                                    list(nutrition_data.keys()),
                                    format_func=lambda x: x.replace('_', ' ').title())

            # Affichage des statistiques du nutriment sélectionné
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

            # Création du box plot pour tous les nutriments
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

            # Box plot comparatif
            fig_box = go.Figure()
            for nut in df_nutrients['Nutriment']:
                row = df_nutrients[df_nutrients['Nutriment'] == nut].iloc[0]
                fig_box.add_trace(go.Box(
                    name=nut,
                    q1=[row['Q1']],
                    median=[row['Médiane']],
                    q3=[row['Q3']],
                    mean=[row['Moyenne']],
                    lowerfence=[0],  # Utilisation de 0 comme minimum
                    # Estimation approximative pour l'affichage
                    upperfence=[row['Moyenne'] * 2]
                ))

            fig_box.update_layout(
                title='Comparaison des distributions des nutriments',
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig_box, use_container_width=True)

            # Tableau détaillé
            if st.checkbox("Voir les statistiques détaillées"):
                st.dataframe(df_nutrients.style.highlight_max(subset=['Moyenne'], color='lightgreen')
                             .highlight_min(subset=['Moyenne'], color='lightpink'),
                             hide_index=True)

        # Footer
        st.markdown("---")
        st.markdown("### 📊 Statistiques Globales")
        total_submissions = sum(
            submissions_data['submissions_per_year'].values())
        st.metric("Nombre total de soumissions", f"{total_submissions:,}")

    elif option_analyse == "Analyse les tags des recettes":
        recipe.analyze_tags()
        # Données
        tags_data = {
            'total_unique_tags': 552,
            'most_common_tags': {
                'preparation': 230546,
                'time-to-make': 225326,
                'course': 218148,
                'main-ingredient': 170446,
                'dietary': 165091,
                'easy': 126062,
                'occasion': 114145,
                'cuisine': 91165,
                'low-in-something': 85776,
                'main-dish': 71786,
                'equipment': 70436,
                '60-minutes-or-less': 69990,
                'number-of-servings': 58949,
                'meat': 56042,
                '30-minutes-or-less': 55077,
                'vegetables': 53814,
                'taste-mood': 52143,
                '4-hours-or-less': 49497,
                'north-american': 48479,
                '3-steps-or-less': 44933
            },
            'tags_per_recipe': {
                'mean': 17.88,
                'median': 17.0,
                'min': 1,
                'max': 73
            }
        }

        # Titre de l'application
        st.title("📊 Analyse des Tags de Recettes")

        # Métriques principales
        st.header("📈 Statistiques Globales")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre total de tags uniques", f"{
                      tags_data['total_unique_tags']:,}")
        with col2:
            st.metric("Moyenne de tags par recette", f"{
                      tags_data['tags_per_recipe']['mean']:.1f}")
        with col3:
            st.metric("Médiane de tags par recette", f"{
                      tags_data['tags_per_recipe']['median']:.1f}")
        with col4:
            st.metric("Maximum de tags par recette", str(
                tags_data['tags_per_recipe']['max']))

        # Création des onglets
        tab1, tab2 = st.tabs(
            ["🏷️ Tags les Plus Courants", "📊 Analyse Détaillée"])

        with tab1:
            # Convertir les données en DataFrame
            df_tags = pd.DataFrame(list(tags_data['most_common_tags'].items()),
                                   columns=['Tag', 'Nombre d\'utilisations'])

            # Calculer les pourcentages
            total_tags = df_tags['Nombre d\'utilisations'].sum()
            df_tags['Pourcentage'] = (
                df_tags['Nombre d\'utilisations'] / total_tags * 100).round(2)

            # Graphique en barres horizontal
            fig_bars = px.bar(df_tags,
                              x='Nombre d\'utilisations',
                              y='Tag',
                              orientation='h',
                              title='Tags les Plus Courants',
                              text='Pourcentage')

            fig_bars.update_traces(
                texttemplate='%{text:.1f}%', textposition='auto')
            fig_bars.update_layout(height=800)
            st.plotly_chart(fig_bars, use_container_width=True)

            # Option pour voir les données en tableau
            if st.checkbox("Voir les données détaillées des tags"):
                st.dataframe(df_tags.style.highlight_max(subset=['Nombre d\'utilisations'],
                                                         color='lightgreen')
                             .highlight_min(subset=['Nombre d\'utilisations'],
                                            color='lightpink'),
                             hide_index=True)

        with tab2:
            st.subheader("Distribution des Tags")

            # Créer des colonnes pour l'affichage des statistiques
            col1, col2 = st.columns(2)

            with col1:
                # Graphique circulaire des top 5 tags
                top_5_tags = df_tags.head(5)
                fig_pie = px.pie(top_5_tags,
                                 values='Nombre d\'utilisations',
                                 names='Tag',
                                 title='Top 5 des Tags les Plus Utilisés')
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Graphique en treemap
                fig_treemap = px.treemap(df_tags,
                                         path=['Tag'],
                                         values='Nombre d\'utilisations',
                                         title='Visualisation Hiérarchique des Tags')
                st.plotly_chart(fig_treemap, use_container_width=True)

            # Analyses supplémentaires
            st.subheader("Analyses des Catégories de Tags")

            # Regrouper les tags par catégories
            categories = {
                'Temps de préparation': ['time-to-make', '60-minutes-or-less', '30-minutes-or-less', '4-hours-or-less'],
                'Type de plat': ['course', 'main-dish'],
                'Ingrédients': ['main-ingredient', 'meat', 'vegetables'],
                'Caractéristiques': ['dietary', 'easy', 'low-in-something'],
                'Cuisine': ['cuisine', 'north-american']
            }

            # Créer un DataFrame pour chaque catégorie
            category_data = []
            for category, tags in categories.items():
                total = sum(tags_data['most_common_tags'].get(
                    tag, 0) for tag in tags)
                category_data.append({'Catégorie': category, 'Total': total})

            df_categories = pd.DataFrame(category_data)

            # Graphique en barres des catégories
            fig_categories = px.bar(df_categories,
                                    x='Catégorie',
                                    y='Total',
                                    title='Distribution par Catégorie de Tags',
                                    text='Total')

            fig_categories.update_traces(
                texttemplate='%{text:,}', textposition='auto')
            st.plotly_chart(fig_categories, use_container_width=True)

        # Statistiques sur la distribution des tags par recette
        st.header("📊 Distribution des Tags par Recette")
        col1, col2 = st.columns(2)

        with col1:
            # Créer un histogramme théorique basé sur les statistiques
            x = np.linspace(tags_data['tags_per_recipe']['min'],
                            tags_data['tags_per_recipe']['max'],
                            100)
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Scatter(x=x, y=np.exp(-(x-tags_data['tags_per_recipe']['mean'])**2/50),
                                          mode='lines', name='Distribution estimée'))
            fig_dist.update_layout(title='Distribution Estimée du Nombre de Tags par Recette',
                                   xaxis_title='Nombre de Tags',
                                   yaxis_title='Densité relative')
            st.plotly_chart(fig_dist, use_container_width=True)

        with col2:
            # Statistiques détaillées
            st.subheader("Statistiques Détaillées")
            stats_df = pd.DataFrame({
                'Statistique': ['Minimum', 'Maximum', 'Moyenne', 'Médiane'],
                'Valeur': [tags_data['tags_per_recipe']['min'],
                           tags_data['tags_per_recipe']['max'],
                           tags_data['tags_per_recipe']['mean'],
                           tags_data['tags_per_recipe']['median']]
            })
            st.dataframe(stats_df.style.highlight_max(subset=['Valeur'], color='lightgreen')
                         .highlight_min(subset=['Valeur'], color='lightpink'),
                         hide_index=True)
    elif option_analyse == "Analyse les contributions par utilisateur":
        recipe.analyze_contributors()

# Onglet Paramètres
with tabs[2]:
    st.title("Paramètres")
    st.write("Options de configuration.")
