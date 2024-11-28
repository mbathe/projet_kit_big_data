
from collections import Counter
import os
from src.utils.helper_data import load_dataset
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_echarts import st_echarts
from datetime import datetime
import numpy as np
from src.utils.static import recipe_columns_description
from scipy import stats
load_dotenv()


class Recipe:
    def __init__(self, name="RAW_recipes", date_start=datetime(1999, 1, 1), date_end=datetime(2018, 12, 31)):
        self.name = name
        self.st = st
        self.date_start = date_start
        self.date_end = date_end
        self.initialize_session_state(name)
        self.annomalis = self.detect_dataframe_anomalies()
        self.columns = list(self.st.session_state.data.columns)

    def initialize_session_state(self, name):
        if 'data' not in self.st.session_state:
            self.st.session_state.data = load_dataset(dir_name=os.getenv(
                "DIR_DATASET_2"), all_contents=True).get(name)
        self.st.session_state.data['submitted'] = pd.to_datetime(
            self.st.session_state.data['submitted'])
        mask = (self.st.session_state.data['submitted'] >= self.date_start) & (
            self.st.session_state.data['submitted'] <= self.date_end)
        self.st.session_state.data = self.st.session_state.data[mask]

    def detect_dataframe_anomalies(self,
                                   std_threshold=3,  # Seuil pour la méthode de l'écart-type
                                   z_score_threshold=3):  # Seuil pour la méthode Z-score

        anomalies = {}
        missing_df = pd.DataFrame({
            'Missing Count': self.st.session_state.data.isnull().sum(),
            'Missing Percentage': (self.st.session_state.data.isnull().sum() / len(self.st.session_state.data) * 100).round(2)
        }).query('`Missing Count` > 0')
        anomalies['missing_values'] = missing_df if not missing_df.empty else pd.DataFrame()

        # Outlier Detection using Standard Deviation Method
        std_outliers_dict = {}
        numeric_columns = self.st.session_state.data.select_dtypes(
            include=[np.number]).columns

        for col in numeric_columns:
            mean = self.st.session_state.data[col].mean()
            std = self.st.session_state.data[col].std()
            std_outliers = self.st.session_state.data[np.abs(
                self.st.session_state.data[col] - mean) > (std_threshold * std)]

            if not std_outliers.empty:
                std_outliers_info = pd.DataFrame({
                    'Column': [col],
                    'Mean': [mean],
                    'Standard Deviation': [std],
                    'Lower Bound': [mean - (std_threshold * std)],
                    'Upper Bound': [mean + (std_threshold * std)],
                    'Outlier Count': [len(std_outliers)],
                    'Outlier Percentage': [round(len(std_outliers) / len(self.st.session_state.data) * 100, 2)]
                })
                std_outliers_dict[col] = std_outliers_info

        # Outlier Detection using Z-Score Method
        z_score_outliers_dict = {}

        for col in numeric_columns:
            # Calculate Z-scores
            z_scores = np.abs(stats.zscore(self.st.session_state.data[col]))
            z_score_outliers = self.st.session_state.data[z_scores >
                                                          z_score_threshold]
            if not z_score_outliers.empty:
                z_score_outliers_info = pd.DataFrame({
                    'Column': [col],
                    'Mean': [self.st.session_state.data[col].mean()],
                    'Standard Deviation': [self.st.session_state.data[col].std()],
                    'Outlier Count': [len(z_score_outliers)],
                    'Outlier Percentage': [round(len(z_score_outliers) / len(self.st.session_state.data) * 100, 2)]
                })
                z_score_outliers_dict[col] = z_score_outliers_info

        # Combine and store outlier detection results
        anomalies['std_outliers'] = pd.concat(
            std_outliers_dict.values()) if std_outliers_dict else pd.DataFrame()
        anomalies['z_score_outliers'] = pd.concat(
            z_score_outliers_dict.values()) if z_score_outliers_dict else pd.DataFrame()

        def safe_nunique(series):
            # Handle columns that might contain lists
            if series.apply(lambda x: isinstance(x, list)).any():
                # Flatten lists and count unique elements
                unique_elements = set(
                    [item for sublist in series for item in sublist])
                return len(unique_elements)
            else:
                return series.nunique()

        column_info_df = pd.DataFrame({
            'Total Count': len(self.st.session_state.data),
            'Unique Count': {col: safe_nunique(self.st.session_state.data[col])
                             for col in self.st.session_state.data.select_dtypes(include=['object', 'category', 'string']).columns},
            'Unique Percentage': {col: round(safe_nunique(self.st.session_state.data[col]) / len(self.st.session_state.data) * 100, 2)
                                  for col in self.st.session_state.data.select_dtypes(include=['object', 'category', 'string']).columns}
        })
        anomalies['column_info'] = column_info_df

        data_types_df = pd.DataFrame({
            'Data Type': self.st.session_state.data.dtypes,
            'Sample': [self.st.session_state.data[col].iloc[0] for col in self.st.session_state.data.columns]
        })
        anomalies['data_types'] = data_types_df

        return anomalies

    def clean_dataframe(self, anomalies, cleaning_method='std', threshold=3):
        """
        Supprime les anomalies d'un DataFrame basé sur les résultats de détection d'anomalies.
        
        Parameters:
        df (pandas.DataFrame): DataFrame original
        anomalies (dict): Résultats des anomalies détectées
        cleaning_method (str): Méthode de nettoyage ('std' ou 'zscore')
        threshold (float): Seuil pour la détection des anomalies
        
        Returns:
        pandas.DataFrame: DataFrame nettoyé
        """
        numeric_columns = self.st.session_state.data.select_dtypes(
            include=[np.number]).columns
        for col in numeric_columns:
            if cleaning_method == 'std':
                mean = self.st.session_state.data[col].mean()
                std = self.st.session_state.data[col].std()
                lower_bound = mean - (threshold * std)
                upper_bound = mean + (threshold * std)
                self.st.session_state.data = self.st.session_state.data[(self.st.session_state.data[col] >= lower_bound) & (
                    self.st.session_state.data[col] <= upper_bound)]

            elif cleaning_method == 'zscore':
                z_scores = np.abs(stats.zscore(
                    self.st.session_state.data[col]))
                self.st.session_state.data = self.st.session_state.data[z_scores <= threshold]

        # Gestion des valeurs manquantes
        if not anomalies['missing_values'].empty:
            # Supprime les lignes avec des valeurs manquantes
            self.st.session_state.data = self.st.session_state.data.dropna(
                subset=anomalies['missing_values'].index)
        self.st.session_state.data = self.st.session_state.data.reset_index(
            drop=True)

    def display_data_structures(self, columns_to_show=None, search_term=None):
        if columns_to_show is None:
            columns_to_show = self.columns
        number_of_rows = st.selectbox(
            "Sélectionnez le nombre d'éléments à afficher :",
            options=[5, 10, 20, 50],
            index=0,
            key='selectbox_dist'
        )
        st.subheader(f'Afficharger des {
            number_of_rows} premiers elements du dataset')
        if search_term:
            mask = self.st.session_state.data['description'].str.contains(
                search_term, case=False)
            mask = mask.fillna(False)
            st.dataframe(
                self.st.session_state.data[mask][columns_to_show].head(number_of_rows))
        else:
            st.dataframe(
                self.st.session_state.data[columns_to_show].head(number_of_rows))

        colonnes_preview = st.checkbox("Afficher la description des colonnes")
        if colonnes_preview:
            st.write("Ce tableau fournit une description détaillée des colonnes utilisées dans la base de données des recettes. Chaque colonne contient des informations spécifiques permettant d’identifier et de décrire les recettes et leurs attributs.")
            st.markdown("---")
            df = pd.DataFrame(recipe_columns_description)
            st.table(df)

    def display_anomalies_values(self):
        colonnes_preview = st.checkbox("Afficher les valeurs abérantes")
        if colonnes_preview:
            st.subheader("Valeurs manquantes")
            df = pd.DataFrame(self.annomalis["missing_values"])
            st.table(df)
            st.markdown("---")
            st.subheader("valeurs aberrantes std")
            df = pd.DataFrame(self.annomalis["std_outliers"])
            st.table(df)
            st.markdown("---")
            st.subheader("score valeurs aberrantes")
            df = pd.DataFrame(self.annomalis["z_score_outliers"])
            st.table(df)
            st.markdown("---")
            st.subheader("Infos sur les colonnes")
            df = pd.DataFrame(self.annomalis["column_info"])
            st.table(df)

    @st.cache_data
    def analyze_calorie_distribution(self, calorie_data):
        # Analyse de la distribution des calories
        total_recipes = sum(calorie_data.values())
        percentiles = []
        cumsum = 0
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
        ingredient_sample = self.st.session_state.data["ingredients"].apply(
            eval)
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

    def analyze_temporal_distribution(self, date_start, date_end):
        mask = (self.st.session_state.data['submitted'] >= date_start) & (
            self.st.session_state.data['submitted'] <= date_end)
        df = self.st.session_state.data[mask]
        # df['submitted'] = pd.to_datetime(df['submitted'])
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
        return tag_stats

    def analyze_contributors(self):
        df = self.self.st.session_state.data
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
    @st.cache_data
    def analyze_recipe_dataset(self):
        """Analyse complète du dataset de recettes"""
        data = self.self.st.session_state.data
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
