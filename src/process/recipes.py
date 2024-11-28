import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from src.utils.helper_data import load_dataset
from collections import Counter
from typing import (
    Any, Dict, List, Optional, Union, Tuple,
    Callable, Sequence, TypedDict, cast
)
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
from scipy import stats
from src.utils.static import recipe_columns_description

# Configuration avancée du logging


def setup_logging(log_file='recipe_analysis.log', log_level=logging.INFO):
    """
    Configuration centralisée du logging avec plusieurs handlers
    
    Args:
        log_file: Chemin du fichier de log
        log_level: Niveau de log par défaut
    """
    # Création du logger racine
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Formatter personnalisé
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler de console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Handler de fichier avec rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 Mo
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Ajout des handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Initialisation du logger
logger = setup_logging()


class RecipeDataLoadError(Exception):
    """Exception personnalisée pour les erreurs de chargement de données."""
    pass


class RecipeDataProcessingError(Exception):
    """Exception personnalisée pour les erreurs de traitement des données."""
    pass


class Recipe:
    def __init__(
        self,
        name: str = "RAW_recipes",
        date_start: datetime = datetime(1999, 1, 1),
        date_end: datetime = datetime(2018, 12, 31)
    ):
        self.name: str = name
        self.st: Any = st
        self.date_start: datetime = date_start
        self.date_end: datetime = date_end

        logger.info(f"Initialisation de l'analyse des recettes : {name}")

        try:
            self.initialize_session_state(name)
            logger.info("État de session initialisé avec succès")
        except Exception as e:
            logger.error(f"Échec de l'initialisation de l'état de session : {
                         e}", exc_info=True)
            raise RecipeDataLoadError(
                f"Impossible d'initialiser l'état de session : {e}")

        try:
            self.annomalis: Dict[str,
                                 pd.DataFrame] = self.detect_dataframe_anomalies()
            logger.info("Détection des anomalies de DataFrame terminée")
        except Exception as e:
            logger.error(f"Erreur lors de la détection des anomalies : {
                         e}", exc_info=True)
            raise RecipeDataProcessingError(
                f"Impossible de détecter les anomalies : {e}")

        self.columns: List[str] = list(self.st.session_state.data.columns)
        logger.debug(f"Colonnes du DataFrame : {self.columns}")

    def initialize_session_state(self, name: str) -> None:
        """Initialize session state with filtered dataset."""
        try:
            dataset_dir = os.getenv("DIR_DATASET_2")
            if dataset_dir is None:
                logger.warning(
                    "Variable d'environnement pour le répertoire de dataset non définie")
                raise ValueError(
                    "La variable d'environnement pour le répertoire de dataset n'est pas définie")

            logger.info(f"Chargement du dataset : {name}")
            self.st.session_state.data = load_dataset(
                dir_name=dataset_dir,
                all_contents=True
            ).get(name)

            if self.st.session_state.data is None:
                logger.error(f"Impossible de charger le dataset : {name}")
                raise RecipeDataLoadError(
                    f"Impossible de charger le dataset : {name}")

            logger.debug("Conversion des dates de soumission")
            self.st.session_state.data['submitted'] = pd.to_datetime(
                self.st.session_state.data['submitted']
            )

            logger.info(f"Filtrage des données entre {
                        self.date_start} et {self.date_end}")
            mask = (
                (self.st.session_state.data['submitted'] >= self.date_start) &
                (self.st.session_state.data['submitted'] <= self.date_end)
            )
            self.st.session_state.data = self.st.session_state.data[mask]
            logger.info(f"Nombre de recettes après filtrage : {
                        len(self.st.session_state.data)}")

        except (KeyError, ValueError) as e:
            logger.error(f"Erreur lors de la préparation des données : {
                         e}", exc_info=True)
            raise RecipeDataLoadError(
                f"Erreur de préparation des données : {e}")

    def clean_dataframe(
        self,
        cleaning_method: str = 'std',
        threshold: float = 3.0
    ) -> None:
        """
        Remove anomalies from DataFrame based on detection results.
        """
        try:
            logger.info(f"Début du nettoyage du DataFrame avec méthode : {
                        cleaning_method}")

            if cleaning_method not in ['std', 'zscore']:
                logger.error(f"Méthode de nettoyage non valide : {
                             cleaning_method}")
                raise ValueError(f"Méthode de nettoyage non valide : {
                                 cleaning_method}")

            initial_size = len(self.st.session_state.data)
            logger.debug(f"Taille initiale du DataFrame : {initial_size}")

            numeric_columns = self.st.session_state.data.select_dtypes(
                include=[np.number]).columns
            logger.debug(f"Colonnes numériques : {list(numeric_columns)}")

            for col in numeric_columns:
                logger.debug(f"Nettoyage de la colonne : {col}")
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
                logger.info("Suppression des valeurs manquantes")
                self.st.session_state.data = self.st.session_state.data.dropna(
                    subset=self.annomalis['missing_values'].index
                )

            self.st.session_state.data = self.st.session_state.data.reset_index(
                drop=True)

            final_size = len(self.st.session_state.data)
            logger.info(f"Nettoyage terminé. Taille initiale : {
                        initial_size}, Taille finale : {final_size}")
            logger.warning(f"Nombre de lignes supprimées : {
                           initial_size - final_size}")

        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du DataFrame : {
                         e}", exc_info=True)
            raise RecipeDataProcessingError(
                f"Nettoyage du DataFrame échoué : {e}")

    # Les autres méthodes gardent la même structure avec des logs ajoutés
    # ... (reste du code avec ajout de logs similaires)

    def analyze_recipe_dataset(self) -> Dict[str, Any]:
        """
        Perform comprehensive dataset analysis.
        """
        try:
            logger.info("Début de l'analyse complète du dataset")
            data = self.st.session_state.data

            general_stats = {
                'total_recipes': len(data),
                'dataset_size_mb': data.memory_usage(deep=True).sum() / 1024 / 1024,
                'columns': list(data.columns),
                'missing_values': data.isnull().sum().to_dict()
            }

            logger.debug(f"Statistiques générales : {general_stats}")

            result = {
                'general_stats': general_stats,
                'temporal_analysis': self.analyze_temporal_distribution(
                    self.date_start, self.date_end
                ),
                'complexity_analysis': self.analyze_recipe_complexity(),
                'nutrition_analysis': self.analyze_nutrition(),
                'tag_analysis': self.analyze_tags(),
                'contributor_analysis': self.analyze_contributors()
            }

            logger.info("Analyse complète du dataset terminée")
            return result

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse complète du dataset : {
                         e}", exc_info=True)
            raise RecipeDataProcessingError(
                f"Analyse du dataset échouée : {e}")


# Configuration du niveau de log via variable d'environnement
if os.getenv('LOG_LEVEL', '').upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL').upper()))
