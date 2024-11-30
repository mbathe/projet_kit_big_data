import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError, BulkWriteError
from bson import ObjectId
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Fonction sécurisée pour évaluer des chaînes de type JSON ou listes


def safe_eval(value, default=None):
    try:
        return eval(value) if isinstance(value, str) else value
    except Exception:
        return default

# Conversion des données du DataFrame en documents MongoDB


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

# Chargement des données dans MongoDB avec gestion des erreurs et insertion par lots


def load_dataframe_to_mongodb(df, connection_string, database_name, collection_name, batch_size=1000):
    try:
        # Établir la connexion à MongoDB
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,  # Timeout pour la sélection du serveur
            socketTimeoutMS=20000,         # Timeout pour les opérations réseau
            retryWrites=True               # Activer la reconnexion automatique
        )

        # Tester la connexion
        try:
            client.admin.command('ping')
            print("Connexion MongoDB réussie.")
        except ServerSelectionTimeoutError as e:
            print(f"Erreur de connexion à MongoDB : {e}")
            return

        # Sélectionner la base de données et la collection
        db = client[database_name]
        collection = db[collection_name]

        # Convertir le DataFrame en documents
        documents = convert_dataframe_to_documents(df)

        # Insérer les documents par lots
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                # `ordered=False` pour ignorer les erreurs sur un seul document
                result = collection.insert_many(batch, ordered=False)
                print(
                    f"Batch {i//batch_size + 1}: {len(result.inserted_ids)} documents insérés.")
            except BulkWriteError as bwe:
                print(f"Erreur d'écriture en masse : {bwe.details}")
            except AutoReconnect as ar:
                print(f"Problème de reconnexion : {ar}. Réessayer...")

    except Exception as e:
        print(f"Erreur inattendue : {e}")
    finally:
        # Fermer la connexion à MongoDB
        client.close()
        print("Connexion MongoDB fermée.")


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de DataFrame
    data = {
        'name': ['Recette 1', 'Recette 2'],
        'tags': ['["facile", "rapide"]', '["végétarien", "sans gluten"]'],
        'nutrition': ['{"calories": 200, "fat": 10}', '{"calories": 150, "fat": 5}'],
        'steps': ['["Étape 1", "Étape 2"]', '["Étape A", "Étape B"]'],
        'ingredients': ['["pomme", "sucre"]', '["riz", "lait de coco"]'],
        'submitted': ['2023-01-01', '2023-02-15']
    }
    # df = pd.DataFrame(data)

    # Charger les variables d'environnement
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "recipes")
    df = pd.read_csv('../data/dataset/recipe/RAW_recipes.csv')
    # Charger les données dans MongoDB
    load_dataframe_to_mongodb(df, CONNECTION_STRING,
                              DATABASE_NAME, COLLECTION_NAME)

    """ load_dataframe_to_mongodb(df, os.getenv("CONNECTION_STRING"), os.getenv(
        "DATABASE_NAME"), os.getenv("COLLECTION_NAME")) """
