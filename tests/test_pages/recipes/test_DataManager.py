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
        mock_logging_error.assert_called_once_with(
            "Échec de l'exportation des données: CSV export failed")
        
        # Vérifiez que le résultat est None en cas d'erreur
        assert result is None
