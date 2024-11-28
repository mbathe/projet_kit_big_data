import pytest
from unittest.mock import patch, MagicMock
# Remplacez 'src.pages.recipes' par le nom de votre module
from src.pages.recipes import DataManager, Recipe


@pytest.fixture
def data_manager():
    return DataManager()


def test_set_date_range(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value = MagicMock()
        data_manager.set_date_range('2020-01-01', '2020-12-31')
        mock_recipe.assert_called_once_with(
            date_start='2020-01-01', date_end='2020-12-31')


def test_get_recipe_data(data_manager):
    assert isinstance(data_manager.get_recipe_data(), Recipe)


def test_export_data_csv(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.st.session_state.data.to_csv.return_value = "csv_data"
        result = data_manager.export_data("CSV")
        assert result == "csv_data"


def test_export_data_json(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.st.session_state.data.to_json.return_value = "json_data"
        result = data_manager.export_data("JSON")
        assert result == "json_data"


def test_analyze_temporal_distribution(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_temporal_distribution.return_value = "temporal_data"
        result = data_manager.analyze_temporal_distribution(
            '2020-01-01', '2020-12-31')
        assert result == "temporal_data"


def test_analyze_recipe_complexity(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_recipe_complexity.return_value = "complexity_data"
        result = data_manager.analyze_recipe_complexity()
        assert result == "complexity_data"


def test_analyze_nutrition(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_nutrition.return_value = "nutrition_data"
        result = data_manager.analyze_nutrition()
        assert result == "nutrition_data"


def test_analyze_tags(data_manager):
    with patch('src.pages.recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_tags.return_value = "tags_data"
        result = data_manager.analyze_tags()
        assert result == "tags_data"
