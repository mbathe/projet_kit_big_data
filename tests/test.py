
from collections import Counter
import os
from src.visualizations.graphiques.heatmap import Heatmap
from src.visualizations.graphiques.histogramme import Histogramme
from src.utils.helper_data import load_dataset
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
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
        self.data = load_dataset(dir_name=os.getenv(
            "DIR_DATASET_2"), all_contents=True).get(name)
        self.columns = list(self.data.columns)
        self.annomalis = self.preprocess_and_detect_anomalies()
        print(self.annomalis)
        # self.processing()

    def preprocess_and_detect_anomalies(self):

        # Convertir les colonnes appropriées en types de données adaptés
        self.data['submitted'] = pd.to_datetime(self.data['submitted'])
        self.data['n_steps'] = self.data['n_steps'].astype(int)
        self.data['minutes'] = self.data['minutes'].astype(int)

        nutrition_cols = ['calories', 'total_fat', 'sugar',
                          'sodium', 'protein', 'saturated_fat', 'carbohydrates']
        nutrition_cols = []
        # self.data['nutrition'] = self.data['nutrition'].apply(eval)

        for col in nutrition_cols:
            self.data[col] = self.data['nutrition'].apply(
                lambda x: float(x[nutrition_cols.index(col)]))

        # Détection des anomalies
        anomalies = pd.DataFrame(
            columns=['index', 'column', 'value', 'reason'])

        # Vérifier les valeurs manquantes
        for col in self.data.columns:
            null_count = self.data[col].isnull().sum()
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
            q1 = self.data[col].quantile(0.25)
            q3 = self.data[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Trouver les indices des valeurs extrêmes
            """  outliers = self.data[(self.data[col] < lower_bound) | (
                self.data[col] > upper_bound)].index

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
                        'value': [self.data.loc[idx, col]],
                        # Utiliser une liste pour respecter la forme
                        'reason': ['Valeur extrême']
                    })
                ], ignore_index=True) """

        # Vérifier les incohérences dans les tags
        """  tag_counts = Counter([tag for tags in self.data['tags']
                             for tag in tags])
        for tag, count in tag_counts.items():
            if count < 5:
                anomalies = pd.concat([
                    anomalies,
                    pd.DataFrame({
                        'index': ['global'],
                        'column': ['tags'],
                        'value': [tag],
                        'reason': ['Tag peu fréquent']
                    })
                ], ignore_index=True)
 """
        return anomalies

    def display_data_structures(self):
        show_preview = st.checkbox("Afficher un aperçu du dataset")
        if show_preview:
            number_of_rows = st.selectbox(
                "Sélectionnez le nombre d'éléments à afficher :",
                options=[5, 10, 20, 50],
                index=0  # Valeur par défaut
            )
            st.subheader(f'Afficharger des {
                         number_of_rows} premiers elements du dataset')
            st.dataframe(self.data.head(number_of_rows))

        colonnes_preview = st.checkbox("Afficher la description des colonnes")
        if colonnes_preview:
            st.write("Ce tableau fournit une description détaillée des colonnes utilisées dans la base de données des recettes. Chaque colonne contient des informations spécifiques permettant d’identifier et de décrire les recettes et leurs attributs.")
            st.markdown("---")  # Séparateur horizontal
            df = pd.DataFrame(recipe_columns_description)
            st.table(df)

    def afficher_correlation(self):
       print()

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

    def analyze_techniques(self, technique_data):
        techniques_count = sum(1 for t in technique_data if t == 1)
        return f"Moyenne de {techniques_count} techniques par recette"

    def analyze_ingredients(self, ingredient_sample):
        # Analyse d'un échantillon d'ingrédients
        flat_ingredients = [
            item for sublist in ingredient_sample for item in sublist]
        ingredient_freq = Counter(flat_ingredients)

        print("\nAnalyse des ingrédients les plus communs:")
        for ingredient, count in ingredient_freq.most_common(10):
            print(f"Ingrédient ID {ingredient}: {count} occurrences")

        return len(set(flat_ingredients))

    def analyze_temporal_distribution(self, df):
        # Analyse la distribution temporelle des soumissions
        df['submitted'] = pd.to_datetime(df['submitted'])
        temporal_stats = {
            'date_min': df['submitted'].min(),
            'date_max': df['submitted'].max(),
            'total_days': (df['submitted'].max() - df['submitted'].min()).days,
            'submissions_per_year': df.groupby(df['submitted'].dt.year).size().to_dict(),
            'submissions_per_month': df.groupby(df['submitted'].dt.month).size().to_dict(),
            'submissions_per_weekday': df.groupby(df['submitted'].dt.dayofweek).size().to_dict()
        }
        return temporal_stats

    def analyze_recipe_complexity(self, df):
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
        return complexity_stats

    def analyze_nutrition(self, df):
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

        return nutrition_stats

    def analyze_tags(self, df):
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
        return tag_stats

    def analyze_contributors(self, df):
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
        return contributor_stats

    # Fonction principale d'analyse
    def analyze_recipe_dataset(self, data):
        """Analyse complète du dataset de recettes"""

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
