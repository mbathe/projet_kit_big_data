import pytest
from unittest.mock import patch, MagicMock
from src.pages.recipes.Analyse_recipes import DataManager
import pandas as pd
import json
from io import StringIO
from src.utils.static import (
    expected_data_temporal_distribution,
    expected_tags_data,
    expected_nutrition_data,
    expected_data_complexity
)

# Créez un DataFrame factice pour les tests
dummy_data = pd.DataFrame({
    'name': ['Recipe1', 'Recipe2'],
    'submitted': [pd.Timestamp('2021-01-01'), pd.Timestamp('2021-02-01')],
    'nutrition': ["{'calories': 100}", "{'calories': 200}"],  
    'description': ['Delicious', 'Tasty'],
    'tags': [['vegan'], ['gluten-free']],
    'ingredients': ["['ingredient1', 'ingredient2']", "['ingredient3', 'ingredient4']"],  # Chaînes de caractères
    'n_steps': [3, 5],
    'minutes': [30, 45],
    'contributor_id': [1, 2]
})

@pytest.fixture
def data_manager_fixture():
    with patch('src.pages.recipes.Analyse_recipes.Recipe') as mock_recipe:
        # Configurez le mock de Recipe
        mock_recipe_instance = MagicMock()
        
        # Mock st et st.session_state.data
        mock_recipe_instance.st = MagicMock()
        mock_recipe_instance.st.session_state = MagicMock()
        mock_recipe_instance.st.session_state.data = MagicMock()
        
        # Configurez les méthodes de Recipe avec des retours prédéfinis
        mock_recipe_instance.analyze_temporal_distribution.return_value = expected_data_temporal_distribution
        mock_recipe_instance.analyze_recipe_complexity.return_value = expected_data_complexity
        mock_recipe_instance.analyze_nutrition.return_value = expected_nutrition_data
        mock_recipe_instance.analyze_tags.return_value = expected_tags_data
        
        # Assignez l'instance mockée au constructeur de Recipe
        mock_recipe.return_value = mock_recipe_instance
        
        # Instanciez DataManager (Recipe est moqué ici)
        data_manager = DataManager()
        
        yield data_manager, mock_recipe, mock_recipe_instance


def test_set_date_range(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Appel de la méthode à tester
    data_manager.set_date_range('2020-01-01', '2020-12-31')
    
    # Vérifiez que Recipe a été instancié avec les bons arguments
    mock_recipe.assert_called_with(date_start='2020-01-01', date_end='2020-12-31')
    
    # Vérifiez que l'instance de Recipe dans DataManager a été mise à jour
    assert data_manager.recipe == mock_recipe_instance


def test_get_recipe_data(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Appel de la méthode à tester
    result = data_manager.get_recipe_data()
    
    # Vérifiez que la méthode retourne bien l'instance mockée de Recipe
    assert result == mock_recipe_instance


def test_export_data_csv(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Simuler des données au format CSV
    expected_csv_data = (
        "name,submitted,nutrition,description,tags,ingredients,n_steps,minutes,contributor_id\n"
        "Recipe1,2021-01-01 00:00:00,'{calories: 100}',Delicious,['vegan'],['ingredient1', 'ingredient2'],3,30,1\n"
        "Recipe2,2021-02-01 00:00:00,'{calories: 200}',Tasty,['gluten-free'],['ingredient3', 'ingredient4'],5,45,2\n"
    )
    mock_recipe_instance.st.session_state.data.to_csv.return_value = expected_csv_data
    
    # Appel de la méthode à tester
    result = data_manager.export_data("CSV")
    
    # Vérifiez que to_csv a été appelé avec les bons arguments
    mock_recipe_instance.st.session_state.data.to_csv.assert_called_once_with(index=False)
    
    # Vérifiez que le résultat est correct
    assert isinstance(result, str), "Result should be a string"
    assert result == expected_csv_data

def test_export_data_json(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Simuler le retour d'une méthode qui renvoie des données au format JSON
    expected_json_data = json.dumps([
        {
            "name": "Recipe1",
            "submitted": "2021-01-01 00:00:00",
            "nutrition": "{'calories': 100}",
            "description": "Delicious",
            "tags": ["vegan"],
            "ingredients": ["ingredient1", "ingredient2"],
            "n_steps": 3,
            "minutes": 30,
            "contributor_id": 1
        },
        {
            "name": "Recipe2",
            "submitted": "2021-02-01 00:00:00",
            "nutrition": "{'calories': 200}",
            "description": "Tasty",
            "tags": ["gluten-free"],
            "ingredients": ["ingredient3", "ingredient4"],
            "n_steps": 5,
            "minutes": 45,
            "contributor_id": 2
        }
    ])
    mock_recipe_instance.st.session_state.data.to_json.return_value = expected_json_data
    
    # Appel de la méthode à tester
    result = data_manager.export_data("JSON")
    
    # Vérifiez que to_json a été appelé avec les bons arguments
    mock_recipe_instance.st.session_state.data.to_json.assert_called_once_with(orient="records")
    
    # Vérifiez que le résultat est correct
    assert isinstance(result, str), "Result should be a string"
    try:
        json.loads(result)
    except json.JSONDecodeError:
        assert False, "Result is not valid JSON"
    assert result == expected_json_data

def test_analyze_temporal_distribution(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    start_datetime = '2020-01-01'
    end_datetime = '2020-12-31'
    
    # Configurez le retour de la méthode
    mock_recipe_instance.analyze_temporal_distribution.return_value = expected_data_temporal_distribution
    
    # Appel de la méthode à tester
    result = data_manager.analyze_temporal_distribution(start_datetime, end_datetime)
    
    # Vérifiez que Recipe.analyze_temporal_distribution a été appelé avec les bons arguments
    mock_recipe_instance.analyze_temporal_distribution.assert_called_once_with(start_datetime, end_datetime)
    
    # Vérifiez que le résultat est correct
    assert result == expected_data_temporal_distribution

def test_analyze_recipe_complexity(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Configurez le retour de la méthode
    mock_recipe_instance.analyze_recipe_complexity.return_value = expected_data_complexity
    
    # Appel de la méthode à tester
    result = data_manager.analyze_recipe_complexity()
    
    # Vérifiez que Recipe.analyze_recipe_complexity a été appelé
    mock_recipe_instance.analyze_recipe_complexity.assert_called_once()
    
    # Vérifiez que le résultat est correct
    assert result == expected_data_complexity

def test_analyze_nutrition(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Configurez le retour de la méthode
    mock_recipe_instance.analyze_nutrition.return_value = expected_nutrition_data
    
    # Appel de la méthode à tester
    result = data_manager.analyze_nutrition()
    
    # Vérifiez que Recipe.analyze_nutrition a été appelé
    mock_recipe_instance.analyze_nutrition.assert_called_once()
    
    # Vérifiez que le résultat est correct
    assert result == expected_nutrition_data

def test_analyze_tags_old(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Configurez le retour de la méthode
    mock_recipe_instance.analyze_tags.return_value = expected_tags_data
    
    # Appel de la méthode à tester
    result = data_manager.analyze_tags()
    
    # Vérifiez que Recipe.analyze_tags a été appelé
    mock_recipe_instance.analyze_tags.assert_called_once()
    
    # Vérifiez que le résultat est correct
    assert result == expected_tags_data

<<<<<<< HEAD:tests/recipes/test_DataManager.py
def test_export_data_csv_failure(data_manager_fixture):
    data_manager, mock_recipe, mock_recipe_instance = data_manager_fixture
    
    # Simuler une exception lors de l'appel à to_csv
    mock_recipe_instance.st.session_state.data.to_csv.side_effect = Exception("CSV export failed")
    
    # Capturer les logs pour vérifier l'erreur
    with patch('logging.error') as mock_logging_error:
        result = data_manager.export_data("CSV")
        
        # Vérifiez que to_csv a été appelé avec les bons arguments
        mock_recipe_instance.st.session_state.data.to_csv.assert_called_once_with(index=False)
        
        # Vérifiez que logging.error a été appelé avec le bon message
        mock_logging_error.assert_called_once_with("Failed to export data: CSV export failed")
        
        # Vérifiez que le résultat est None en cas d'erreur
        assert result is None
=======
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
>>>>>>> main:tests/test_pages/recipes/test_DataManager.py
