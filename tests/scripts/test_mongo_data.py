from pymongo import MongoClient
import mongomock
import os
import pytest
import pandas as pd
from pymongo.errors import BulkWriteError
from scripts.mongo_data import (
    safe_eval,
    convert_dataframe_to_documents,
    DataFrameConverter,
    load_dataframe_to_mongodb
)


@pytest.mark.parametrize("input_value, expected_output", [
    ('[1, 2, 3]', [1, 2, 3]),
    ('{"key": "value"}', {"key": "value"}),
    ('not_valid_json', None),
    (123, 123)
])
def test_safe_eval(input_value, expected_output):
    assert safe_eval(input_value, default=None) == expected_output


def test_convert_dataframe_to_documents():
    data = {
        'tags': ['["tag1", "tag2"]', '["tag3"]'],
        'nutrition': ['{"calories": 100}', '{}'],
        'steps': ['["step1", "step2"]', '[]'],
        'ingredients': ['["item1", "item2"]', '["item3"]'],
        'submitted': ['2023-01-01', None]
    }
    df = pd.DataFrame(data)

    documents = convert_dataframe_to_documents(df)

    assert len(documents) == 2
    assert documents[0]['tags'] == ["tag1", "tag2"]
    assert documents[1]['nutrition'] == {}
    assert pd.isna(documents[1]['submitted'])


def test_dataframe_converter():
    data = {
        'name': ['Recipe 1', 'Recipe 2'],
        'id': [1, 2],
        'minutes': [10, 20],
        'contributor_id': [1001, 1002],
        'submitted': ['2023-01-01', '2023-02-01'],
        'tags': ['["easy", "quick"]', '["vegan"]'],
        'nutrition': ['{"calories": 200}', '{"calories": 150}'],
        'n_steps': [2, 3],
        'steps': ['["Step 1", "Step 2"]', '["Step A", "Step B"]'],
        'description': ['Delicious recipe', 'Another great recipe'],
        'ingredients': ['["sugar", "milk"]', '["flour", "water"]'],
        'n_ingredients': [2, 2]
    }
    df = pd.DataFrame(data)

    documents = DataFrameConverter.convert_raw_recipe_dataframe(df)

    assert len(documents) == 2
    assert documents[0]['name'] == 'Recipe 1'
    assert documents[1]['n_ingredients'] == 2


@pytest.fixture
def mock_mongo_client(mocker):
    mock_client = mocker.patch("my_script.MongoClient")
    mock_client.return_value.__enter__.return_value = mock_client
    return mock_client


def test_dataframe_converter_missing_columns():
    df = pd.DataFrame({
        'name': ['Recipe 1'],
        'id': [1],
        'minutes': [10]
    })

    with pytest.raises(ValueError):
        DataFrameConverter.convert_raw_recipe_dataframe(df)


# test_dataframe_converter.py

# Exemple de données pour les tests
test_data = {
    'name': ['Recette 1', 'Recette 2'],
    'tags': ['["facile", "rapide"]', '["végétarien", "sans gluten"]'],
    'nutrition': ['{"calories": 200, "fat": 10}', '{"calories": 150, "fat": 5}'],
    'steps': ['["Étape 1", "Étape 2"]', '["Étape A", "Étape B"]'],
    'ingredients': ['["pomme", "sucre"]', '["riz", "lait de coco"]'],
    'submitted': ['2023-01-01', '2023-02-15']
}


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(test_data)


def test_safe_eval():
    assert safe_eval('{"key": "value"}') == {"key": "value"}
    assert safe_eval('[1, 2, 3]') == [1, 2, 3]
    assert safe_eval('invalid', default='default') == 'default'


def test_convert_dataframe_to_documents(sample_dataframe):
    documents = convert_dataframe_to_documents(sample_dataframe)

    assert len(documents) == 2
    assert documents[0]['name'] == 'Recette 1'
    assert documents[0]['tags'] == ['facile', 'rapide']
    assert documents[0]['nutrition']['calories'] == 200
    # Vérifie que la date est bien convertie
    assert pd.isna(documents[0]['submitted']) is False


def test_load_dataframe_to_mongodb(mocker, sample_dataframe):
    mock_client = mongomock.MongoClient()
    mocker.patch('scripts.mongo_data.MongoClient', return_value=mock_client)

    connection_string = "mongodb://localhost:27017"
    database_name = "testdb"
    collection_name = "recipes"

    load_dataframe_to_mongodb(
        sample_dataframe, connection_string, database_name, collection_name)

    # Vérification des documents insérés
    db = mock_client[database_name]
    collection = db[collection_name]
    # Vérifie que 2 documents ont été insérés
    assert collection.count_documents({}) == 2


def test_convert_dataframe_to_documents_with_missing_columns(sample_dataframe):
    incomplete_dataframe = sample_dataframe.drop(columns=['tags'])

    with pytest.raises(ValueError, match="Le DataFrame est incomplet. Colonnes manquantes"):
        DataFrameConverter.convert_dataframe_to_documents(
            incomplete_dataframe, required_columns=['name', 'tags'])


def test_convert_raw_interaction_dataframe():
    interaction_data = {
        'user_id': [1, 2],
        'recipe_id': [1, 2],
        'date': ['2023-01-01', '2023-01-02'],
        'rating': [5, 4],
        'review': ['Delicious!', 'Very good!']
    }
    interaction_dataframe = pd.DataFrame(interaction_data)
    documents = DataFrameConverter.convert_raw_interaction_dataframe(
        interaction_dataframe)

    assert len(documents) == 2
    assert documents[0]['rating'] == 5
    assert pd.to_datetime(documents[0]['date'], errors='coerce') is not pd.NaT


if __name__ == "__main__":
    pytest.main()
