import pytest
import pandas as pd
from datetime import datetime, date
from unittest.mock import patch, MagicMock

# Importez votre classe Recipe
from src.process.recipes import Recipe


@pytest.fixture
def sample_dataframe():
    """Créer un DataFrame de test avec des données de recettes"""
    data = {
        'name': ['Arriba Baked Winter Squash', 'A Bit Different Breakfast Pizza',
                 'All in the Kitchen Chili', 'Alouette Potatoes'],
        'id': [137739, 31490, 112140, 59389],
        'minutes': [55, 30, 130, 45],
        'contributor_id': [47892, 26278, 196586, 68585],
        'submitted': [
            datetime(2005, 9, 16),
            datetime(2002, 6, 17),
            datetime(2005, 2, 25),
            datetime(2003, 4, 14)
        ],
        'tags': [
            ['60-minutes-or-less', 'time-to-make', 'squash'],
            ['30-minutes-or-less'],
            ['time-to-make'],
            ['60-minutes-or-less']
        ],
        'nutrition': [
            [100, 10, 5, 200, 15, 3, 20],
            [150, 15, 8, 250, 20, 5, 25],
            [200, 20, 10, 300, 25, 7, 30],
            [120, 12, 6, 220, 18, 4, 22]
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def recipe_instance(sample_dataframe):
    """Créer une instance de Recipe avec un DataFrame de test"""
    with patch('streamlit.session_state', MagicMock()) as mock_session_state:
        mock_session_state.data = sample_dataframe
        recipe = Recipe(name="test_recipes",
                        date_start=datetime(2002, 1, 1),
                        date_end=datetime(2005, 12, 31))
    return recipe


def test_recipe_initialization(recipe_instance):
    """Test l'initialisation de la classe Recipe"""
    assert hasattr(recipe_instance, 'st')
    assert hasattr(recipe_instance, 'date_start')
    assert hasattr(recipe_instance, 'date_end')
    assert hasattr(recipe_instance, 'annomalis')
    assert hasattr(recipe_instance, 'columns')


def test_detect_dataframe_anomalies(recipe_instance):
    """Test la méthode de détection des anomalies"""
    anomalies = recipe_instance.annomalis
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies


def test_ensure_datetime():
    """Test la méthode _ensure_datetime"""
    recipe = Recipe()
    dt_obj = datetime(2023, 1, 1)
    date_obj = date(2023, 1, 1)

    assert recipe._ensure_datetime(dt_obj) == dt_obj
    assert recipe._ensure_datetime(date_obj) == datetime(2023, 1, 1, 0, 0)

    with pytest.raises(TypeError):
        recipe._ensure_datetime("invalid")


if __name__ == "__main__":
    pytest.main([__file__])
