import os
import logging
from typing import List, Dict

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError, BulkWriteError
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.join(
            os.path.dirname(__file__), '..'), 'app.log')),
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



def safe_eval(value, default=None):
    try:
        return eval(value) if isinstance(value, str) else value
    except Exception:
        return default


def convert_dataframe_to_documents(df):
    documents = []
    for _, row in df.iterrows():
        document = row.to_dict()

        # Conversion des colonnes spécifiques si elles sont des chaînes JSON
        document['tags'] = safe_eval(row.get('tags', '[]'), default=[])
        document['nutrition'] = safe_eval(
            row.get('nutrition', '{}'), default={})
        document['steps'] = safe_eval(row.get('steps', '[]'), default=[])
        document['ingredients'] = safe_eval(
            row.get('ingredients', '[]'), default=[])

        # Conversion de la colonne 'submitted' en datetime
        document['submitted'] = pd.to_datetime(
            row.get('submitted', pd.NaT), errors='coerce')

        documents.append(document)
    return documents


def load_dataframe_to_mongodb(df, connection_string, database_name, collection_name, batch_size=1000, use_convertisseur=True):
    try:
        # Établir la connexion à MongoDB
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=20000,
            retryWrites=True
        )
        try:
            client.admin.command('ping')
            logging.info("Connexion MongoDB réussie.")
        except ServerSelectionTimeoutError as e:
            logging.error(f"Erreur de connexion à MongoDB : {e}")
            return

        # Sélectionner la base de données et la collection
        db = client[database_name]
        collection = db[collection_name]

        if use_convertisseur:
            documents = convert_dataframe_to_documents(df)
        else:
            documents = df

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                result = collection.insert_many(batch, ordered=False)
                print(
                    f"Batch {i//batch_size + 1}: {len(result.inserted_ids)} documents insérés.")
            except BulkWriteError as bwe:
                print(f"Erreur d'écriture en masse : {bwe.details}")
            except AutoReconnect as ar:
                logging.error(f"Problème de reconnexion : {ar}. Réessayer...")

    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")
    finally:
        client.close()
        logging.info("Connexion MongoDB fermée.")


class DataFrameConverter:
    """
    Classe utilitaire pour convertir différents types de DataFrames en documents MongoDB.
    """

    @staticmethod
    def convert_dataframe_to_documents(df: pd.DataFrame, required_columns: List[str]) -> List[Dict]:
        """
        Convertit un DataFrame en une liste de documents MongoDB, après validation des colonnes.

        Args:
            df (pd.DataFrame): Le DataFrame à convertir.
            required_columns (List[str]): Liste des colonnes nécessaires.

        Returns:
            List[Dict]: Liste de documents compatibles MongoDB.
        """
        # Vérification des colonnes requises
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Le DataFrame est incomplet. Colonnes manquantes : {
                             missing_columns}")

        # Convertir les colonnes spécifiques au bon format
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(
                df['date'], errors='coerce')  # Convertir les dates
        if 'rating' in df.columns:
            # S'assurer que les notes sont des entiers
            df['rating'] = df['rating'].astype(int)

        # Convertir le DataFrame en liste de dictionnaires
        return df.to_dict(orient='records')

    @staticmethod
    def convert_raw_recipe_dataframe(df: pd.DataFrame) -> List[Dict]:
        """
        Convertit un DataFrame contenant des recettes en documents MongoDB.

        Args:
            df (pd.DataFrame): DataFrame des recettes.

        Returns:
            List[Dict]: Liste de documents MongoDB.
        """
        required_columns = [
            'name', 'id', 'minutes', 'contributor_id', 'submitted',
            'tags', 'nutrition', 'n_steps', 'steps', 'description',
            'ingredients', 'n_ingredients'
        ]
        return DataFrameConverter.convert_dataframe_to_documents(df, required_columns)

    @staticmethod
    def convert_raw_interaction_dataframe(df: pd.DataFrame) -> List[Dict]:
        """
        Convertit un DataFrame contenant des avis utilisateurs en documents MongoDB.

        Args:
            df (pd.DataFrame): DataFrame des avis utilisateurs.

        Returns:
            List[Dict]: Liste de documents MongoDB.
        """
        required_columns = ['user_id', 'recipe_id', 'date', 'rating', 'review']
        return DataFrameConverter.convert_dataframe_to_documents(df, required_columns)


# Exemple d'utilisation
if __name__ == "__main__":
    df = pd.read_csv(os.path.join(os.getenv("DIR_DATASET"), "RAW_recipes.csv"))
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
    COLLECTION_RECIPES_NAME = os.getenv("COLLECTION_RECIPES_NAME", "recipes2")
    load_dataframe_to_mongodb(df, CONNECTION_STRING,
                              DATABASE_NAME, COLLECTION_RECIPES_NAME)
