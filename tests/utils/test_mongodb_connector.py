# test_mongodb_connector.py

import mongomock
import pytest
from pymongo import MongoClient
import pandas as pd
from unittest.mock import patch, MagicMock

# Remplacez par le chemin de votre module
from src.utils.MongoDBConnector import MongoDBConnector


@pytest.fixture
def mongo_connector():
    # Création d'une instance de MongoDBConnector avec mongomock
    connection_string = "mongodb://localhost:27017"
    database_name = "test_database"

    # Utiliser mongomock pour simuler MongoDB
    client = mongomock.MongoClient()
    connector = MongoDBConnector(connection_string, database_name)
    connector.client = client
    connector.db = client[database_name]

    yield connector

    connector.close()




def test_connect(mongo_connector):
    mongo_connector.connect()
    assert mongo_connector.client is not None
    assert mongo_connector.db.name == "test_database"


def test_load_collection_as_dataframe(mongo_connector):
    # Ajouter des documents à la collection simulée
    test_data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
    mongo_connector.db['users'].insert_many(test_data)

    # Charger la collection dans un DataFrame
    df = mongo_connector.load_collection_as_dataframe('users')

    assert not df.empty
    assert len(df) == 2
    assert set(df['name']) == {'Alice', 'Bob'}


def test_load_collection_with_query(mongo_connector):
    # Ajouter des documents à la collection simulée
    test_data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
    mongo_connector.db['users'].insert_many(test_data)

    # Charger la collection avec un filtre
    df = mongo_connector.load_collection_as_dataframe(
        'users', query={'age': {'$gt': 26}})

    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]['name'] == 'Alice'


def test_load_collection_empty(mongo_connector):
    # Essayer de charger une collection vide
    df = mongo_connector.load_collection_as_dataframe('users')

    assert df.empty


def test_close_connection(mongo_connector):
    mongo_connector.connect()
    mongo_connector.close()
    assert mongo_connector.client is None

## AJOUTE PAR SACHA ##

@pytest.fixture
def mongo_uri():
    return "mongodb://localhost:27017"

@pytest.fixture
def db_name():
    return "test_db"

@pytest.fixture
def connector(mongo_uri, db_name):
    return MongoDBConnector(mongo_uri, db_name)

@patch("builtins.print")
def test_connect_success(mock_print, connector, mongo_uri, db_name):
    # Test pour lignes 51-53 : connexion réussie
    # On mock le MongoClient pour qu'il ne lève pas d'exception.
    with patch.object(MongoClient, "__init__", return_value=None) as mock_client_init, \
         patch.object(MongoClient, "__getitem__", return_value="test_db_obj") as mock_get_item:
        # On doit s'assurer que MongoClient(...) renvoie un objet simulé
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = "test_db_obj"
        # On redéfinit le retour du constructeur pour retourner l'objet mock
        mock_client_init.return_value = None
        with patch("pymongo.MongoClient", return_value=mock_client):
            connector.connect()
            # Vérifie que la base de données est définie
            assert connector.db == "test_db_obj"
            mock_print.assert_called_once_with("Connecté à la base de données : test_db")

def test_load_collection_no_connection(connector):
    # Test pour la ligne 86 : if self.db is None:
    # Sans appel à connector.connect(), db est None
    with pytest.raises(Exception) as exc_info:
        connector.load_collection_as_dataframe("my_collection")
    assert "La connexion à MongoDB n'a pas été initialisée" in str(exc_info.value)

@patch("builtins.print")
def test_load_collection_with_limit(mock_print, connector):
    # Test pour ligne 98 : if limit is not None
    # On simule une connexion et un curseur Mongo
    connector.db = MagicMock()
    mock_collection = MagicMock()
    connector.db.__getitem__.return_value = mock_collection

    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [{'data': 1}, {'data': 2}]
    mock_collection.find.return_value = mock_cursor

    df = connector.load_collection_as_dataframe("my_collection", limit=2)
    # Vérification que le limit est bien appliqué
    mock_cursor.limit.assert_called_once_with(2)
    # Vérification du DataFrame renvoyé
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

@patch("builtins.print")
def test_load_collection_exception(mock_print, connector):
    # Test pour lignes 111-113 : except Exception dans load_collection_as_dataframe
    connector.db = MagicMock()
    mock_collection = MagicMock()
    connector.db.__getitem__.return_value = mock_collection

    # On force une exception lors de l'appel à find()
    mock_collection.find.side_effect = Exception("Test error")

    df = connector.load_collection_as_dataframe("my_collection")
    # Vérification que l'exception a bien été gérée
    mock_print.assert_called_with("Erreur lors de la récupération des données de la collection 'my_collection': Test error")
    # On doit renvoyer un DataFrame vide
    assert isinstance(df, pd.DataFrame)
    assert df.empty
