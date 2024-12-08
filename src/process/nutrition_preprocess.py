# fmt: off
from src.utils.helper_data import load_dataset_from_file
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import ast
import logging
from datetime import date
from pathlib import Path
from datetime import datetime
from src.pages.recipes.Welcom import Welcome

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.join(
            os.path.dirname(__file__), '../..'), "app.log")),
        logging.StreamHandler()
    ]
)


error_handler = logging.FileHandler(os.path.join(os.path.join(
    os.path.dirname(__file__), '../..'), "error.log"))
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

# Ajouter le FileHandler à la configuration de logging
logging.getLogger().addHandler(error_handler)


logger = logging.getLogger(__name__)

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "recipes")
DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE", "LOCAL")
COLLECTION_RAW_INTERACTIONS = os.getenv(
    "COLLECTION_RAW_INTERACTIONS", "raw_interactio")
CONNECTION_STRING = os.getenv("CONNECTION_STRING")

DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE")
YEAR_MIN = 1999 if DEPLOIEMENT_SITE != "ONLINE" else 2014
YEAR_MAX = 2018 if DEPLOIEMENT_SITE != "ONLINE" else 2018

start_date = date(YEAR_MIN, 1, 1)
end_date = date(YEAR_MAX, 12, 31)




cwd = str(Path.cwd())


def load_data(limit=500000):
    """
    Charge et prépare les données des recettes et des interactions, puis les fusionne en un seul DataFrame.

    Cette fonction effectue plusieurs étapes :
    1. Charge les fichiers CSV contenant les recettes et les interactions.
    2. Calcule la moyenne des notes et le nombre de notes pour chaque recette.
    3. Fusionne les données des recettes avec les données de notes.
    4. Transforme la colonne 'nutrition' en listes de valeurs individuelles.
    5. Sépare les valeurs nutritionnelles en colonnes distinctes.
    6. Convertit ces valeurs en types numériques.

    Returns:
        pd.DataFrame: Un DataFrame contenant les informations fusionnées et nettoyées sur les recettes, 
                      incluant les colonnes 'Moyenne des notes', 'Nombre de notes' et les valeurs nutritionnelles.
    """
    logger.info("Chargement des données...")

    try:

        dataset_dir = os.getenv("DIR_DATASET")
        if "limit" not in st.session_state:
            st.session_state.limit = limit
        if DEPLOIEMENT_SITE !="ONLINE":
            if "data" not in st.session_state:
                df_RAW_recipes = Welcome.show_welcom(DEPLOIEMENT_SITE, load_dataset_from_file, os.path.join(dataset_dir, "RAW_recipes.csv"), None, None, datetime(1999, 1, 1), datetime(2018, 12, 31))
            else:    
                df_RAW_recipes = st.session_state.data
        else:
            if "data" not in st.session_state:
                df_RAW_recipes = Welcome.show_welcom(DEPLOIEMENT_SITE, load_dataset_from_file, CONNECTION_STRING, DATABASE_NAME, COLLECTION_NAME, datetime(1999, 1, 1), datetime(2018, 12, 31), is_interactional=True, limit=limit)
            else:
                df_RAW_recipes = st.session_state.data
        if "df_RAW_interactions" not in st.session_state or limit!=st.session_state.limit:
            if DEPLOIEMENT_SITE !="ONLINE":
                df_RAW_interactions = Welcome.show_welcom(DEPLOIEMENT_SITE, load_dataset_from_file, os.path.join(dataset_dir, "RAW_interactions.csv"), None, None, datetime(1999, 1, 1), datetime(2018, 12, 31), is_interactional=True)
            else:
                df_RAW_interactions = Welcome.show_welcom(DEPLOIEMENT_SITE, load_dataset_from_file, CONNECTION_STRING, DATABASE_NAME,COLLECTION_RAW_INTERACTIONS , datetime(1999, 1, 1), datetime(2018, 12, 31), is_interactional=True, limit=limit)
        else:
            df_RAW_interactions =st.session_state.df_RAW_interactions
        logger.info(
            "Données des recettes et des interactions chargées avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des fichiers CSV: {e}")
        raise
    # On ne garde que la moyenne des notes de la recette
    df_mean_rating = df_RAW_interactions[[
        'recipe_id', 'rating']].groupby(['recipe_id']).mean().round(2)
    logger.info("Moyenne des notes par recette calculée.")

    # On ne garde que le nombre de notes de la recette
    df_count_rating = df_RAW_interactions[[
        'recipe_id', 'rating']].groupby(['recipe_id']).count()
    logger.info("Nombre de notes par recette calculé.")

    df_nutrition = df_RAW_recipes[['id', 'name', 'nutrition']]

    # Fusionner les DataFrames
    merged_df = df_nutrition.merge(df_mean_rating, left_on='id', right_on='recipe_id').merge(
        df_count_rating, left_on='id', right_on='recipe_id')
    logger.info("Données fusionnées avec succès.")

    merged_df.rename(columns={'rating_x': 'Moyenne des notes',
                              'rating_y': 'Nombre de notes'}, inplace=True)

    # Convertir les chaînes de caractères en listes
    merged_df['nutrition'] = merged_df['nutrition'].apply(ast.literal_eval) if DEPLOIEMENT_SITE!="ONLINE" else  merged_df['nutrition']
    logger.info("Les données de nutrition ont été converties en listes.")

    # Convertir la colonne de listes en plusieurs colonnes
    valeurs_df = pd.DataFrame(
        merged_df['nutrition'].tolist(), index=merged_df.index)

    # Renommer les colonnes si nécessaire
    valeurs_df.columns = ['Calories', 'Graisses', 'Sucre', 'Sodium',
                          'Protéines', 'Graisse_saturées', 'Glucides']

    # Joindre le DataFrame original avec le nouveau DataFrame
    nutrition_df = merged_df.drop(columns=['nutrition', 'id']).join(valeurs_df)
    logger.info("Données de nutrition séparées en colonnes individuelles.")

    # Convertir les colonnes en numériques
    nutrition_df[['Calories', 'Graisses', 'Sucre', 'Sodium',
                  'Protéines', 'Graisse_saturées', 'Glucides']] = nutrition_df[[
                      'Calories', 'Graisses', 'Sucre', 'Sodium',
                      'Protéines', 'Graisse_saturées', 'Glucides']].apply(pd.to_numeric)
    logger.info(
        "Les colonnes de valeurs nutritionnelles ont été converties en numériques.")

    return nutrition_df


@st.cache_data
def clean_data(df):
    """
    Nettoie les données en filtrant les recettes ayant trop peu de notes et en supprimant les valeurs aberrantes 
    dans les données nutritionnelles.

    Cette fonction effectue les opérations suivantes :
    1. Filtre les recettes ayant moins de 5 notes.
    2. Supprime les valeurs nutritionnelles aberrantes dans les colonnes 'Graisses', 'Graisse_saturées', 
       'Sucre', 'Sodium', 'Protéines', 'Glucides' en supprimant les valeurs supérieures à 100.
    3. Supprime les recettes ayant plus de 800 calories.

    Parameters:
        df (pd.DataFrame): Le DataFrame contenant les données des recettes, y compris les valeurs nutritionnelles.

    Returns:
        pd.DataFrame: Un DataFrame nettoyé, avec les valeurs aberrantes et les recettes ayant peu de notes supprimées.
    """

    logger.info("Nettoyage des données...")

    # Filtrer les données (nombre de notes >= 5)
    df = df[(df['Nombre de notes'] >= 5)]
    logger.info("Filtrage des recettes ayant moins de 5 notes effectué.")

    # Supprimer les valeurs nutritionnelles aberrantes
    nutrition_columns = ['Graisses', 'Graisse_saturées',
                         'Sucre', 'Sodium', 'Protéines', 'Glucides']
    for column in nutrition_columns:
        df = df.drop(df[df[column] > 100].index)
        logger.info(f"Valeurs aberrantes supprimées pour la colonne {column}.")

    df = df.drop(df[df[('Calories')] > 800].index)
    logger.info("Valeurs aberrantes supprimées pour la colonne Calories.")

    logger.info("Nettoyage des données terminé.")

    return df
