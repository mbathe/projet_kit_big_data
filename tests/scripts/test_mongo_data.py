import pytest
import pandas as pd
from pymongo.errors import BulkWriteError
from scripts.mongo_data import (
    safe_eval,
    convert_dataframe_to_documents,
    DataFrameConverter
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
