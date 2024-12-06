# test_mongodb_connector.py

import mongomock
import pytest
from pymongo import MongoClient
import pandas as pd

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
