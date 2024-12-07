import streamlit as st
import pandas as pd
import ast
import logging
from pathlib import Path

# Configuration du logger
logging.basicConfig(level=logging.INFO)  # Définir le niveau de log à INFO
logger = logging.getLogger(__name__)

cwd = str(Path.cwd())


@st.cache_data
def load_data():
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
        df_RAW_recipes = pd.read_csv(cwd + '\\data\\RAW_recipes.csv')
        df_RAW_interactions = pd.read_csv(cwd + '\\data\\RAW_interactions.csv')
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
    merged_df['nutrition'] = merged_df['nutrition'].apply(ast.literal_eval)
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
