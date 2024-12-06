import logging
from src.utils.helper_data import load_dataset_from_file
from datetime import date
from typing import (
    Any, Dict, List, Union, TypedDict
)
import pandas as pd
import streamlit as st
from datetime import datetime
import numpy as np
from scipy import stats
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import os
from src.pages.recipes.Welcom import Welcome

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "recipes")
DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE", "LOCAL")


DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE")
YEAR_MIN = 1999 if DEPLOIEMENT_SITE != "ONLINE" else 2014
YEAR_MAX = 2018 if DEPLOIEMENT_SITE != "ONLINE" else 2018

# Configurer le logger pour écrire dans un fichier
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Type definitions
class NutritionStats(TypedDict):
    mean: float
    median: float
    min: float
    max: float
    quartiles: Dict[float, float]

class TemporalStats(TypedDict):
    date_min: datetime
    date_max: datetime
    total_days: int
    submissions_per_year: Dict[int, int]
    submissions_per_month: Dict[int, int]
    submissions_per_weekday: Dict[int, int]

class ComplexityStats(TypedDict):
    steps_stats: Dict[str, Union[float, int, Dict[int, int]]]
    time_stats: Dict[str, Union[float, int, Dict[str, int]]]

class ContributorStats(TypedDict):
    total_contributors: int
    contributions_per_user: Dict[str, float]
    top_contributors: Dict[str, int]

class TagStats(TypedDict):
    total_unique_tags: int
    most_common_tags: Dict[str, int]
    tags_per_recipe: Dict[str, float]

class Recipe:
    def __init__(
        self,
        name: str = "RAW_recipes",
        date_start: datetime = datetime(YEAR_MIN, 1, 1),
        date_end: datetime = datetime(YEAR_MAX, 12, 31)
    ):
        self.name: str = name
        self.st: Any = st
        self.date_start: datetime = date_start
        self.date_end: datetime = date_end
        try:
            self.initialize_session_state(date_start, date_end)
        except Exception as e:
            logging.error(f"Error initializing session state: {e}")
            raise
        try:
            self.annomalis: Dict[str,
                                 pd.DataFrame] = self.detect_dataframe_anomalies()
        except Exception as e:
            logging.error(f"Error detecting dataframe anomalies: {e}")
            raise
        self.columns: List[str] = list(self.st.session_state.data.columns)



    def initialize_session_state(self, start_date, end_date) -> None:
        """
        Initialiser l'état de session avec un jeu de données filtré.

        Cette fonction configure l'état de session avec le jeu de données approprié en fonction du site de déploiement
        et de la plage de dates. Elle gère les déploiements en ligne et locaux, en récupérant les données à partir de MongoDB ou
        en les chargeant à partir d'un fichier local.

        Paramètres:
        start_date (datetime or date): La date de début pour filtrer le jeu de données.
        end_date (datetime or date): La date de fin pour filtrer le jeu de données.

        Retourne:
        None

        Lève:
        Exception: Si une erreur se produit pendant le processus d'initialisation, elle enregistre l'erreur et la relance.
        """
        try:
            print(DEPLOIEMENT_SITE)
            if DEPLOIEMENT_SITE == "ONLINE":
                if 'data' not in self.st.session_state:
                    if 'start_date' not in self.st.session_state:
                        self.st.session_state.start_date = self._ensure_date(
                            start_date)
                    if 'end_date' not in self.st.session_state:
                        st.empty()
                        self.st.session_state.end_date = self._ensure_date(
                            end_date)
                    welcome_container = self.st.empty()
                    self.st.session_state.data = Welcome.show_welcom(DEPLOIEMENT_SITE,
                                                                     self.fetch_data_from_mongodb, CONNECTION_STRING, DATABASE_NAME, COLLECTION_NAME, start_date, end_date)
                    welcome_container.empty()
                elif (self._ensure_date(start_date) != self.st.session_state.start_date and self._ensure_date(start_date) != date(YEAR_MIN, 1, 1)) or (self._ensure_date(end_date) != self.st.session_state.end_date and self._ensure_date(end_date) != date(YEAR_MAX, 12, 31)):
                    with self.st.spinner("⏳ **Chargement en cours...**"):
                        try:
                            self.st.session_state.data = self.fetch_data_from_mongodb(
                            CONNECTION_STRING, DATABASE_NAME, COLLECTION_NAME, start_date, end_date)
                            self.st.session_state.start_date = self._ensure_date(
                                start_date)
                            self.st.session_state.end_date = self._ensure_date(
                                end_date)

                        except Exception as e:
                            self.st.error(f"❌ Erreur de chargement : {e}")

            else:
                if 'data' not in self.st.session_state:
                    dataset_dir = os.getenv("DIR_DATASET_2")
                    self.st.session_state.data = Welcome.show_welcom(DEPLOIEMENT_SITE, load_dataset_from_file, os.path.join(
                        dataset_dir, "RAW_recipes.csv"), None, None, start_date, end_date)
                    self.st.session_state.start_date = self._ensure_date(
                        start_date)
                    self.st.session_state.end_date = self._ensure_date(
                        end_date)
                elif (self._ensure_date(start_date) != self.st.session_state.start_date and self._ensure_date(start_date) != date(YEAR_MIN, 1, 1)) or (self._ensure_date(end_date) != self.st.session_state.end_date and self._ensure_date(end_date) != date(YEAR_MAX, 12, 31)):
                    dataset_dir = os.getenv("DIR_DATASET_2")
                    self.st.session_state.data = load_dataset_from_file(
                        os.path.join(dataset_dir, "RAW_recipes.csv"), self._ensure_datetime(start_date), self._ensure_datetime(end_date))
                    self.st.session_state.start_date = self._ensure_date(
                        start_date)
                    self.st.session_state.end_date = self._ensure_date(
                        end_date)
        except Exception as e:
            logging.error(f"Error in initialize_session_state: {e}")
            raise

    def _ensure_datetime(self, obj):
        if isinstance(obj, datetime):
            return obj
        elif isinstance(obj, date):
            return datetime.combine(obj, datetime.min.time())
        else:
            raise TypeError("L'objet doit être de type datetime ou date.")

    def _ensure_date(sefl, obj):
        if isinstance(obj, date):
            return obj
        elif isinstance(obj, datetime):
            return obj.date()
        else:
            raise TypeError("L'objet doit être de type date ou datetime.")

    def detect_dataframe_anomalies(
        self,
        std_threshold: float = 3.0,
        z_score_threshold: float = 3.0
    ) -> Dict[str, pd.DataFrame]:
        """
        Détecter les anomalies dans le DataFrame à l'aide de diverses méthodes statistiques.

        Cette fonction effectue plusieurs techniques de détection d'anomalies sur le DataFrame,
        notamment la détection des valeurs manquantes, la détection des valeurs aberrantes basée sur l'écart-type,
        et la détection des valeurs aberrantes basée sur le score Z. Elle fournit également des informations sur les types de colonnes
        et les décomptes de valeurs uniques.

        Paramètres:
        std_threshold (float): Le nombre d'écarts-types à utiliser comme seuil
                                pour identifier les valeurs aberrantes dans la méthode de l'écart-type.
                                Par défaut à 3.0.
        z_score_threshold (float): Le seuil de score Z à utiliser pour identifier les valeurs
                                    aberrantes dans la méthode du score Z. Par défaut à 3.0.

        Retourne:
        Dict[str, pd.DataFrame]: Un dictionnaire contenant divers DataFrames avec les
                                    anomalies détectées et les informations sur les données. Les clés du dictionnaire sont :
                                    - 'missing_values': DataFrame avec les nombres et pourcentages de valeurs manquantes
                                    - 'std_outliers': DataFrame avec les valeurs aberrantes basées sur l'écart-type
                                    - 'z_score_outliers': DataFrame avec les valeurs aberrantes basées sur le score Z
                                    - 'column_info': DataFrame avec les informations sur les colonnes (décomptes uniques, etc.)
                                    - 'data_types': DataFrame avec les types de données et des exemples de valeurs pour chaque colonne

        Lève:
        Exception: Si une erreur se produit pendant le processus de détection d'anomalies.
            """
        anomalies: Dict[str, pd.DataFrame] = {}
        try:
            # Missing values detection
            missing_df = pd.DataFrame({
                'Missing Count': self.st.session_state.data.isnull().sum(),
                'Missing Percentage': (
                    self.st.session_state.data.isnull().sum() /
                    len(self.st.session_state.data) * 100
                ).round(2)
            }).query('`Missing Count` > 0')
            anomalies['missing_values'] = missing_df if not missing_df.empty else pd.DataFrame()

            # Numeric columns detection
            numeric_columns = self.st.session_state.data.select_dtypes(
                include=[np.number]).columns

            # Standard deviation outliers
            std_outliers_dict: Dict[str, pd.DataFrame] = {}
            for col in numeric_columns:
                mean = self.st.session_state.data[col].mean()
                std = self.st.session_state.data[col].std()
                std_outliers = self.st.session_state.data[
                    np.abs(
                        self.st.session_state.data[col] - mean) > (std_threshold * std)
                ]

                if not std_outliers.empty:
                    std_outliers_info = pd.DataFrame({
                        'Column': [col],
                        'Mean': [mean],
                        'Standard Deviation': [std],
                        'Lower Bound': [mean - (std_threshold * std)],
                        'Upper Bound': [mean + (std_threshold * std)],
                        'Outlier Count': [len(std_outliers)],
                        'Outlier Percentage': [
                            round(len(std_outliers) /
                                  len(self.st.session_state.data) * 100, 2)
                        ]
                    })
                    std_outliers_dict[col] = std_outliers_info

            # Z-score outliers
            z_score_outliers_dict: Dict[str, pd.DataFrame] = {}
            for col in numeric_columns:
                z_scores = np.abs(stats.zscore(
                    self.st.session_state.data[col]))
                z_score_outliers = self.st.session_state.data[z_scores >
                                                              z_score_threshold]

                if not z_score_outliers.empty:
                    z_score_outliers_info = pd.DataFrame({
                        'Column': [col],
                        'Mean': [self.st.session_state.data[col].mean()],
                        'Standard Deviation': [self.st.session_state.data[col].std()],
                        'Outlier Count': [len(z_score_outliers)],
                        'Outlier Percentage': [
                            round(len(z_score_outliers) /
                                  len(self.st.session_state.data) * 100, 2)
                        ]
                    })
                    z_score_outliers_dict[col] = z_score_outliers_info

            # Combine outlier results
            anomalies['std_outliers'] = (
                pd.concat(std_outliers_dict.values())
                if std_outliers_dict else pd.DataFrame()
            )
            anomalies['z_score_outliers'] = (
                pd.concat(z_score_outliers_dict.values())
                if z_score_outliers_dict else pd.DataFrame()
            )

            # Column information
            def safe_nunique(series: pd.Series) -> int:
                """Handle columns that might contain lists."""
                if series.apply(lambda x: isinstance(x, list)).any():
                    unique_elements = set(
                        [item for sublist in series for item in sublist]
                    )
                    return len(unique_elements)
                return series.nunique()

            column_info_df = pd.DataFrame({
                'Total Count': len(self.st.session_state.data),
                'Unique Count': {
                    col: safe_nunique(self.st.session_state.data[col])
                    for col in self.st.session_state.data.select_dtypes(
                        include=['object', 'category', 'string']
                    ).columns
                },
                'Unique Percentage': {
                    col: round(
                        safe_nunique(self.st.session_state.data[col]) /
                        len(self.st.session_state.data) * 100,
                        2
                    )
                    for col in self.st.session_state.data.select_dtypes(
                        include=['object', 'category', 'string']
                    ).columns
                }
            })
            anomalies['column_info'] = column_info_df

            # Data types information
            data_types_df = pd.DataFrame({
                'Data Type': self.st.session_state.data.dtypes,
                'Sample': [self.st.session_state.data[col].iloc[0] for col in self.st.session_state.data.columns]
            })
            anomalies['data_types'] = data_types_df
        except Exception as e:
            logging.error(f"Error detecting dataframe anomalies: {e}")
            raise

        return anomalies

    def clean_dataframe(
        self,
        cleaning_method: str = 'std',
        threshold: float = 3.0
    ) -> None:
        """
        Supprimer les anomalies du DataFrame en fonction des résultats de détection.

        Args:
            anomalies: Résultats de la détection d'anomalies
            cleaning_method: Méthode de nettoyage ('std' ou 'zscore')
            threshold: Seuil pour la détection d'anomalies
        """
        try:
            numeric_columns = self.st.session_state.data.select_dtypes(
                include=[np.number]).columns

            for col in numeric_columns:
                if cleaning_method == 'std':
                    mean = self.st.session_state.data[col].mean()
                    std = self.st.session_state.data[col].std()
                    lower_bound = mean - (threshold * std)
                    upper_bound = mean + (threshold * std)
                    self.st.session_state.data = self.st.session_state.data[
                        (self.st.session_state.data[col] >= lower_bound) &
                        (self.st.session_state.data[col] <= upper_bound)
                    ]

                elif cleaning_method == 'zscore':
                    z_scores = np.abs(stats.zscore(
                        self.st.session_state.data[col]))
                    self.st.session_state.data = self.st.session_state.data[z_scores <= threshold]

            # Handle missing values
            if not self.annomalis['missing_values'].empty:
                self.st.session_state.data = self.st.session_state.data.dropna(
                    subset=self.annomalis['missing_values'].index
                )

            self.st.session_state.data = self.st.session_state.data.reset_index(
                drop=True)
        except Exception as e:
            logging.error(f"Error cleaning dataframe: {e}")
            raise

    def analyze_nutrition(self) -> Dict[str, NutritionStats]:
        """
        Analyser les informations nutritionnelles.

        Retourne :
            Statistiques nutritionnelles pour chaque catégorie
        """
        try:
            df = self.st.session_state.data

            if DEPLOIEMENT_SITE != "ONLINE":
                df['nutrition_list'] = df['nutrition'].apply(eval)
            else:
                df['nutrition_list'] = df['nutrition']
            nutrition_columns = [
                'calories', 'total_fat', 'sugar',
                'sodium', 'protein', 'saturated_fat', 'carbohydrates'
            ]

            nutrition_df = pd.DataFrame(
                df['nutrition_list'].tolist(),
                columns=nutrition_columns
            )

            nutrition_stats: Dict[str, NutritionStats] = {
                col: {
                    'mean': nutrition_df[col].mean(),
                    'median': nutrition_df[col].median(),
                    'min': nutrition_df[col].min(),
                    'max': nutrition_df[col].max(),
                    'quartiles': nutrition_df[col].quantile([0.25, 0.5, 0.75]).to_dict()
                } for col in nutrition_columns
            }
        except Exception as e:
            logging.error(f"Error analyzing nutrition: {e}")
            raise

        return nutrition_stats

    def analyze_temporal_distribution(
        self,
        date_start: datetime,
        date_end: datetime
    ) -> TemporalStats:
        """
        Analyse la distribution temporelle des recettes.

        Args :
            date_start : Date de début de l'analyse
            date_end : Date de fin de l'analyse

        Returns :
            Statistiques de distribution temporelle
        """
        try:
            mask = (
                (self.st.session_state.data['submitted'] >= date_start) &
                (self.st.session_state.data['submitted'] <= date_end)
            )
            df = self.st.session_state.data[mask]

            temporal_stats: TemporalStats = {
                'date_min': df['submitted'].min(),
                'date_max': df['submitted'].max(),
                'total_days': (df['submitted'].max() - df['submitted'].min()).days,
                'submissions_per_year': df.groupby(df['submitted'].dt.year).size().to_dict(),
                'submissions_per_month': df.groupby(df['submitted'].dt.month).size().to_dict(),
                'submissions_per_weekday': df.groupby(df['submitted'].dt.dayofweek).size().to_dict()
            }
        except Exception as e:
            logging.error(f"Error analyzing temporal distribution: {e}")
            raise
        return temporal_stats

    def analyze_tags(self) -> TagStats:
        """
        Analyse les étiquettes de recettes et génère des statistiques liées aux étiquettes.

        Cette fonction traite les étiquettes associées aux recettes dans l'ensemble de données,
        calculant diverses statistiques telles que le nombre total de balises uniques, les balises les plus courantes et des statistiques sur le nombre de balises par recette,
        les balises les plus courantes et des statistiques sur le nombre de balises par recette.
        Retourne :
            TagStats : Un dictionnaire contenant les statistiques suivantes relatives aux étiquettes :
                - 'total_unique_tags' : Le nombre total de tags uniques dans toutes les recettes.
                - 'most_common_tags' : Un dictionnaire des 20 tags les plus courants et de leur fréquence.
                - 'tags_per_recipe' : Un dictionnaire contenant des statistiques sur le nombre de tags par recette :
                    - 'mean' : Le nombre moyen de tags par recette.
                    - 'median' : Le nombre médian de tags par recette : Le nombre médian de tags par recette.
                    - 'min' : Le nombre minimum de tags par recette : Le nombre minimum de tags pour une recette.
                    - 'max' : Le nombre maximum de tags pour une recette : Le nombre maximum de tags pour une recette.

        Lève :
            Exception : Si une erreur se produit pendant le processus d'analyse des balises.
        """
        try:
            df = self.st.session_state.data
            if DEPLOIEMENT_SITE != "ONLINE":
                df['tags_list'] = df['tags'].apply(eval)
            else:
                df['tags_list'] = df['tags']

            all_tags = [tag for tags in df['tags_list'] for tag in tags]
            tag_counts = pd.Series(all_tags).value_counts()

            tag_stats: TagStats = {
                'total_unique_tags': len(tag_counts),
                'most_common_tags': tag_counts.head(20).to_dict(),
                'tags_per_recipe': {
                    'mean': df['tags_list'].str.len().mean(),
                    'median': df['tags_list'].str.len().median(),
                    'min': df['tags_list'].str.len().min(),
                    'max': df['tags_list'].str.len().max()
                }
            }
        except Exception as e:
            logging.error(f"Error analyzing tags: {e}")
            raise

        return tag_stats

    def analyze_contributors(self):
        """
        Analyse les contributions par utilisateur.

        Cette fonction calcule le nombre total de contributeurs,
        les statistiques de contributions par utilisateur (moyenne, médiane, maximum),
        et les 10 principaux contributeurs.

        Returns:
            Un dictionnaire contenant les statistiques de contributions par utilisateur.
            Le dictionnaire a les clés suivantes :
            - 'total_contributors': Nombre total de contributeurs.
            - 'contributions_per_user': Statistiques de contributions par utilisateur (moyenne, médiane, maximum).
            - 'top_contributors': Les 10 principaux contributeurs avec leur nombre de contributions.

        Raises:
            Exception: Si une erreur se produit lors de l'analyse des contributions.
        """
        try:
            df = self.st.session_state.data
            contributor_stats = {
                'total_contributors': df['contributor_id'].nunique(),
                'contributions_per_user': {
                    'mean': df['contributor_id'].value_counts().mean(),
                    'median': df['contributor_id'].value_counts().median(),
                    'max': df['contributor_id'].value_counts().max()
                },
                'top_contributors': df['contributor_id'].value_counts().head(10).to_dict()
            }
        except Exception as e:
            logging.error(f"Error analyzing contributors: {e}")
            raise

        return contributor_stats

    def analyze_recipe_dataset(self) -> Dict[str, Any]:
        """
        Effectuer une analyse complète de l'ensemble des données.

        Retours :
            Analyse complète de l'ensemble de données de la recette
        """
        try:
            data = self.st.session_state.data

            general_stats = {
                'total_recipes': len(data),
                'dataset_size_mb': data.memory_usage(deep=True).sum() / 1024 / 1024,
                'columns': list(data.columns),
                'missing_values': data.isnull().sum().to_dict()
            }
        except Exception as e:
            logging.error(f"Error analyzing recipe dataset: {e}")
            raise

        return {
            'general_stats': general_stats,
            'temporal_analysis': self.analyze_temporal_distribution(
                self.date_start, self.date_end
            ),
            'complexity_analysis': self.analyze_recipe_complexity(),
            'nutrition_analysis': self.analyze_nutrition(),
            'tag_analysis': self.analyze_tags(),
            'contributor_analysis': self.analyze_contributors()
        }

    def analyze_recipe_complexity(self):
        """Analyse la complexité des recettes"""
        try:
            df = self.st.session_state.data
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
                                          bins=[0, 15, 30, 60,
                                                120, float('inf')],
                                          labels=['0-15min', '15-30min', '30-60min', '1-2h', '>2h']).value_counts().to_dict()
                }
            }
        except Exception as e:
            logging.error(f"Error analyzing recipe complexity: {e}")
            raise
        return complexity_stats

    def fetch_data_from_mongodb(self, connection_string, database_name, collection_name, start_date, end_date):
        """
        Charge les données depuis MongoDB en fonction d'un intervalle de dates et retourne un DataFrame.

        :param connection_string: URI de connexion à MongoDB
        :param database_name: Nom de la base de données
        :param collection_name: Nom de la collection
        :param start_date: Date de début (string ou datetime)
        :param end_date: Date de fin (string ou datetime)
        :return: DataFrame contenant les données
        """
        try:
            client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000
            )
            client.admin.command('ping')
            db = client[database_name]
            collection = db[collection_name]
            query = {"submitted": {"$gte": pd.to_datetime(
                start_date), "$lte": pd.to_datetime(end_date)}}
            projection = {"_id": 0}
            data = list(collection.find(query, projection))
            if not data:
                st.warning(
                    "Aucune donnée trouvée pour cet intervalle de dates.")
                return pd.DataFrame()
            df = pd.DataFrame(data)
            return df

        except ServerSelectionTimeoutError as e:
            st.error(f"Erreur de connexion à MongoDB : {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            return pd.DataFrame()
        finally:
            client.close()
