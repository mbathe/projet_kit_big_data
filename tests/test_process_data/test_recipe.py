import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
import numpy as np
from datetime import date
from unittest.mock import patch, MagicMock

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
def sample_recipe_data() -> pd.DataFrame:
    """
    Create a sample recipe dataset for testing.

    Returns:
        pd.DataFrame: Sample recipe data
    """
    return pd.DataFrame({
        'submitted': pd.date_range(start='1/1/2010', periods=100),
        'nutrition': [str([100, 10, 5, 200, 15, 3, 20]) for _ in range(100)],
        'tags': [str(['quick', 'healthy']) for _ in range(100)],
        'contributor_id': np.random.randint(1, 11, 100),
        'n_steps': np.random.randint(1, 10, 100),
        'minutes': np.random.randint(10, 120, 100)
    })



@pytest.fixture
def recipe_analyzer(sample_recipe_data: pd.DataFrame) -> Recipe:
    """
    Create a Recipe instance with sample data.

    Args:
        sample_recipe_data: Sample recipe dataset

    Returns:
        Recipe: Configured Recipe instance
    """
    with patch.object(Recipe, 'initialize_session_state') as mock_init_state, \
        patch('src.process.recipes.st') as mock_st:
        
        # Mock de la méthode initialize_session_state pour qu'elle ne fasse rien
        mock_init_state.return_value = None
        
        # Configuration du mock de st.session_state avec l'attribut 'data'
        mock_st.session_state = MagicMock()
        mock_st.session_state.data = sample_recipe_data
        
        # Création de l'instance Recipe
        recipe = Recipe()
        
        # Initialisation des anomalies si nécessaire
        recipe.annomalis = recipe.detect_dataframe_anomalies()
        
        return recipe



def test_detect_dataframe_anomalies(recipe_analyzer: Recipe) -> None:
    """
    Test dataframe anomaly detection.
    
    Args:
        recipe_analyzer: Recipe analysis instance
    """
    anomalies = recipe_analyzer.detect_dataframe_anomalies()
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies



def test_analyze_nutrition(recipe_analyzer: Recipe) -> None:
    """
    Test nutritional analysis.
    
    Args:
        recipe_analyzer: Recipe analysis instance
    """
    nutrition_stats = recipe_analyzer.analyze_nutrition()
    expected_columns = [
        'calories', 'total_fat', 'sugar',
        'sodium', 'protein', 'saturated_fat', 'carbohydrates'
    ]
    for column in expected_columns:
        assert column in nutrition_stats
        stats = nutrition_stats[column]
        assert all(key in stats for key in [
                   'mean', 'median', 'min', 'max', 'quartiles'])



def test_analyze_temporal_distribution(recipe_analyzer: Recipe) -> None:
    """
    Test temporal distribution analysis.
    
    Args:
        recipe_analyzer: Recipe analysis instance
    """
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2010, 12, 31)
    temporal_stats = recipe_analyzer.analyze_temporal_distribution(
        start_date, end_date)
    assert 'date_min' in temporal_stats
    assert 'date_max' in temporal_stats
    assert 'total_days' in temporal_stats
    assert 'submissions_per_year' in temporal_stats
    assert 'submissions_per_month' in temporal_stats
    assert 'submissions_per_weekday' in temporal_stats


def test_analyze_tags(recipe_analyzer: Recipe) -> None:
    """
    Test tag analysis.
    
    Args:
        recipe_analyzer: Recipe analysis instance
    """
    tag_stats = recipe_analyzer.analyze_tags()
    assert 'total_unique_tags' in tag_stats
    assert 'most_common_tags' in tag_stats
    assert 'tags_per_recipe' in tag_stats
    tags_per_recipe = tag_stats['tags_per_recipe']
    assert all(key in tags_per_recipe for key in [
               'mean', 'median', 'min', 'max'])


def test_clean_dataframe(recipe_analyzer: Recipe) -> None:
    """
    Test dataframe cleaning method.
    
    Args:
        recipe_analyzer: Recipe analysis instance
    """
    initial_length = len(recipe_analyzer.st.session_state.data)
    anomalies = recipe_analyzer.detect_dataframe_anomalies()
    recipe_analyzer.clean_dataframe(anomalies)
    cleaned_length = len(recipe_analyzer.st.session_state.data)
    assert cleaned_length <= initial_length


def test_analyze_recipe_dataset(recipe_analyzer: Recipe) -> None:
    """
    Test comprehensive dataset analysis.
    
    Args:
        recipe_analyzer: Recipe analysis instance
    """
    analysis_results = recipe_analyzer.analyze_recipe_dataset()
    expected_keys = [
        'general_stats',
        'temporal_analysis',
        'complexity_analysis',
        'nutrition_analysis',
        'tag_analysis',
        'contributor_analysis'
    ]
    for key in expected_keys:
        assert key in analysis_results


def test_initialization() -> None:
    """
    Test Recipe class initialization.
    """
    with patch.object(Recipe, 'initialize_session_state') as mock_init_state, \
         patch('src.process.recipes.st') as mock_st:
        
        # Mock de la méthode initialize_session_state pour qu'elle ne fasse rien
        mock_init_state.return_value = None
        
        # Configuration du mock de st.session_state avec un DataFrame vide ou par défaut
        mock_st.session_state = MagicMock()
        mock_st.session_state.data = pd.DataFrame()  # Vous pouvez utiliser sample_recipe_data si nécessaire
        
        # Création de l'instance Recipe
        default_recipe = Recipe()
        
        # Vérifications
        assert default_recipe.name == "RAW_recipes"
        assert default_recipe.date_start == datetime(1999, 1, 1)
        assert default_recipe.date_end == datetime(2018, 12, 31)
    default_recipe = Recipe()

    assert default_recipe.name == "RAW_recipes"
    assert default_recipe.date_start == datetime(1999, 1, 1)
    assert default_recipe.date_end == datetime(2018, 12, 31)


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


def test_detect_dataframe_anomalies_2(recipe_instance):
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
