import os

from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv



class MongoDBConnector:
    """
    Classe pour se connecter à MongoDB et charger des données d'une collection en DataFrame.
    """

    def __init__(self, connection_string: str, database_name: str):
        """
        Initialise la connexion à MongoDB.

        Args:
            connection_string (str): URI de connexion à MongoDB.
            database_name (str): Nom de la base de données.
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None

    def connect(self):
        """Établit une connexion avec MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            print(f"Connecté à la base de données : {self.database_name}")
        except Exception as e:
            print(f"Erreur lors de la connexion à MongoDB : {e}")
            raise

    def load_collection_as_dataframe(
        self, 
        collection_name: str, 
        query: dict = None, 
        limit: int = None, 
        fields: dict = None
        ) -> pd.DataFrame:  
        """
        Charge une collection MongoDB et retourne un DataFrame Pandas.

        Args:
            collection_name (str): Nom de la collection à charger.
            query (dict): Filtre MongoDB (par défaut : None, pour charger tous les documents).
            limit (int): Nombre maximum de documents à charger (par défaut : None, pour ne pas limiter).
            fields (dict): Colonnes à inclure/exclure dans les résultats (par défaut : None, pour tout inclure).

        Returns:
            pd.DataFrame: DataFrame contenant les données de la collection.
        """
        if self.db is None:
            raise Exception("La connexion à MongoDB n'a pas été initialisée. Appelez `connect()` en premier.")

        try:
            collection = self.db[collection_name]
            
            # Si aucun filtre n'est fourni, charger tous les documents
            if query is None:
                query = {}

            # Appliquer la projection des colonnes
            cursor = collection.find(query, fields) if fields else collection.find(query)

            # Appliquer le critère de limite
            if limit is not None:
                cursor = cursor.limit(limit)

            # Récupérer les documents et les transformer en DataFrame
            data = list(cursor)
            
            if data:
                df = pd.DataFrame(data)
                # Supprimer la colonne '_id' si elle existe (et si elle n'est pas explicitement demandée)
                if '_id' in df.columns and (not fields or fields.get('_id', 1) == 0):
                    df.drop(columns=['_id'], inplace=True)
                return df
            else:
                print(f"La collection '{collection_name}' est vide ou ne contient aucun document correspondant au filtre.")
                return pd.DataFrame()

        except Exception as e:
            print(f"Erreur lors de la récupération des données de la collection '{collection_name}': {e}")
            return pd.DataFrame()

    def close(self):
        """Ferme la connexion à MongoDB."""
        if self.client:
            self.client.close()
            print("Connexion MongoDB fermée.")
