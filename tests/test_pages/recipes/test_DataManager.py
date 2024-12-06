import pytest
from unittest.mock import patch, MagicMock
# Remplacez 'src.pages.recipes' par le nom de votre module
from src.pages.recipes.Analyse_recipes import DataManager
from src.process.recipes import Recipe
import json
import csv
from io import StringIO
from src.utils.static import expected_data_temporal_distribution, expected_tags_data, expected_nutrition_data, expected_data_complexity
@pytest.fixture
def data_manager():
    return DataManager()


def test_set_date_range(data_manager):
    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value = MagicMock()
        data_manager.set_date_range('2020-01-01', '2020-12-31')
        mock_recipe.assert_called_once_with(
            date_start='2020-01-01', date_end='2020-12-31')


def test_get_recipe_data(data_manager):
    assert isinstance(data_manager.get_recipe_data(), Recipe)

def test_export_data_csv(data_manager):
    # Simuler des données au format CSV
    expected_csv_data = "column1,column2\nvalue1,value2\nvalue3,value4\n"

    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.st.session_state.data.to_csv.return_value = expected_csv_data
        result = data_manager.export_data("CSV")

        # Vérification que le résultat est bien du type str
        assert isinstance(result, str), "Result should be a string"

        # Vérification que le résultat peut être décodé comme un CSV valide
        try:
            # Utiliser StringIO pour simuler un fichier CSV
            csv.reader(StringIO(result))
        except Exception:
            assert False, "Result is not valid CSV"


def test_export_data_json(data_manager):
    # Simuler le retour d'une méthode qui renvoie des données au format JSON
    expected_json_data = json.dumps(
        {"key": "value"})  # Exemple de données JSON
    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.st.session_state.data.to_json.return_value = expected_json_data
        result = data_manager.export_data("JSON")
        assert isinstance(result, str), "Result should be a string"
        try:
            json.loads(result)
        except json.JSONDecodeError:
            assert False, "Result is not valid JSON"


def test_analyze_temporal_distribution(data_manager):
    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_temporal_distribution.return_value = "temporal_data"
        result = data_manager.analyze_temporal_distribution(
            '2020-01-01', '2020-12-31')
        for key in expected_data_temporal_distribution.keys():
            assert key in result, f"Missing key: {key}"



def test_analyze_recipe_complexity(data_manager):

    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_recipe_complexity.return_value = "complexity_data"
        result = data_manager.analyze_recipe_complexity()
        for key in expected_data_complexity.keys():
            assert key in result, f"Missing key: {key}"

        for key, value in expected_data_complexity['steps_stats'].items():
            assert key in result['steps_stats'], f"Missing key in steps_stats: {
                key}"

        for key, value in expected_data_complexity['time_stats'].items():
            assert key in result['time_stats'], f"Missing key in time_stats: {
                key}"

        assert result['steps_stats']['mean'] == expected_data_complexity['steps_stats']['mean'], "Mean steps does not match"
        assert result['steps_stats']['median'] == expected_data_complexity['steps_stats']['median'], "Median steps does not match"
        assert result['steps_stats']['min'] == expected_data_complexity['steps_stats']['min'], "Min steps does not match"
        assert result['steps_stats']['max'] == expected_data_complexity['steps_stats']['max'], "Max steps does not match"

        assert result['time_stats']['mean_minutes'] == expected_data_complexity['time_stats']['mean_minutes'], "Mean minutes does not match"
        assert result['time_stats']['median_minutes'] == expected_data_complexity[
            'time_stats']['median_minutes'], "Median minutes does not match"
        assert result['time_stats']['min_minutes'] == expected_data_complexity['time_stats']['min_minutes'], "Min minutes does not match"
        assert result['time_stats']['max_minutes'] == expected_data_complexity['time_stats']['max_minutes'], "Max minutes does not match"

def test_analyze_nutrition(data_manager):
    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_nutrition.return_value = "nutrition_data"
        result = data_manager.analyze_nutrition()
        for key in expected_nutrition_data.keys():
            assert key in result, f"Missing key: {key}"

        for key, value in expected_nutrition_data.items():
            for subkey in value.keys():
                assert subkey in result[key], f"Missing key in {key}: {subkey}"


def test_analyze_tags_old(data_manager):

    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        mock_recipe.return_value.analyze_tags.return_value = "tags_data"
        result = data_manager.analyze_tags()
        for key in expected_tags_data.keys():
            assert key in result, f"Missing key: {key}"
        for key in expected_tags_data['most_common_tags'].keys():
            assert key in result['most_common_tags'], f"Missing key in most_common_tags: {
                key}"

        for key in expected_tags_data['tags_per_recipe'].keys():
            assert key in result['tags_per_recipe'], f"Missing key in tags_per_recipe: {
                key}"


## TEST AJOUTE PAR SACHA ##
from datetime import date
import datetime

@patch("logging.error")
def test_set_date_range_error(mock_log, data_manager):
    # Test lignes 81-82
    # Forçons une exception dans set_date_range
    with patch.object(Recipe, "__init__", side_effect=Exception("Test Error")):
        data_manager.set_date_range(date(2020, 1, 1), date(2020, 1, 2))
        mock_log.assert_called_once_with("Échec de la définition de la plage de dates: Test Error")

@patch("logging.error")
def test_export_data_error(mock_log, data_manager):
    # Test lignes 111-112
    # Simuler une exception lors de l'export
    with patch.object(data_manager.recipe.st.session_state.data, "to_csv", side_effect=Exception("Export Error")):
        data_manager.export_data("CSV")
        mock_log.assert_called_once_with("Échec de l'exportation des données: Export Error")

@patch("logging.error")
def test_analyze_recipe_complexity_error(mock_log, data_manager):
    # Test lignes 146-147
    with patch.object(data_manager.recipe, "analyze_recipe_complexity", side_effect=Exception("Complexity Error")):
        data_manager.analyze_recipe_complexity()
        mock_log.assert_called_once_with("Échec de l'analyse de la complexité des recettes: Complexity Error")

@patch("logging.error")
def test_analyze_nutrition_error(mock_log, data_manager):
    # Test lignes 162-163
    with patch.object(data_manager.recipe, "analyze_nutrition", side_effect=Exception("Nutrition Error")):
        data_manager.analyze_nutrition()
        mock_log.assert_called_once_with("Échec de l'analyse des informations nutritionnelles: Nutrition Error")

@patch("logging.error")
def test_analyze_tags_error(mock_log, data_manager):
    # Test lignes 178-179
    with patch.object(data_manager.recipe, "analyze_tags", side_effect=Exception("Tags Error")):
        data_manager.analyze_tags()
        mock_log.assert_called_once_with("Échec de l'analyse des tags: Tags Error")