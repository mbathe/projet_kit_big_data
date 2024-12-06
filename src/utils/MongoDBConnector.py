from pymongo import MongoClient
import pandas as pd


class MongoDBConnector:
    """
    Classe pour se connecter à MongoDB et charger des données d'une collection en DataFrame.

    Cette classe facilite la connexion à une base de données MongoDB, le chargement de
    collections spécifiques en tant que DataFrame Pandas, et la gestion de la connexion.

    Args:
        connection_string (str): URI de connexion à MongoDB.
        database_name (str): Nom de la base de données.

    Attributes:
        connection_string (str): URI de connexion à MongoDB.
        database_name (str): Nom de la base de données.
        client (MongoClient or None): Instance du client MongoDB après connexion.
        db (Database or None): Instance de la base de données MongoDB après connexion.
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
        """
        Établit une connexion avec MongoDB.

        Cette méthode tente de se connecter à MongoDB en utilisant l'URI de connexion fourni
        et initialise les attributs `client` et `db`. En cas d'échec de la connexion,
        une exception est levée.

        Raises:
            Exception: Si une erreur survient lors de la connexion à MongoDB.
        """
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

        Cette méthode récupère les documents d'une collection MongoDB spécifiée, applique
        des filtres, limite le nombre de documents si nécessaire, et projette les champs
        souhaités. Les données récupérées sont ensuite converties en DataFrame Pandas.

        Args:
            collection_name (str): Nom de la collection à charger.
            query (dict, optional): Filtre MongoDB pour sélectionner les documents.
                Par défaut : None, pour charger tous les documents.
            limit (int, optional): Nombre maximum de documents à charger.
                Par défaut : None, pour ne pas limiter.
            fields (dict, optional): Projection des colonnes à inclure ou exclure.
                Par défaut : None, pour inclure toutes les colonnes.

        Returns:
            pd.DataFrame: DataFrame contenant les données de la collection.
                Retourne un DataFrame vide si la collection est vide ou si aucun document ne correspond au filtre.

        Raises:
            Exception: Si la connexion à MongoDB n'a pas été établie avant l'appel de cette méthode.
        """
        if self.db is None:
            raise Exception("La connexion à MongoDB n'a pas été initialisée. Appelez `connect()` en premier.")

        try:
            collection = self.db[collection_name]

            if query is None:
                query = {}

            cursor = collection.find(query, fields) if fields else collection.find(query)


            if limit is not None:
                cursor = cursor.limit(limit)

            data = list(cursor)
            
            if data:
                df = pd.DataFrame(data)
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
        """
        Ferme la connexion à MongoDB.

        Cette méthode ferme la connexion active avec MongoDB si elle est établie.
        """
        if self.client:
            self.client.close()
            self.client = None  # Réinitialiser l'attribut client
            self.db = None  # Réinitialiser l'attribut db si nécessaire
            print("Connexion MongoDB fermée.")
