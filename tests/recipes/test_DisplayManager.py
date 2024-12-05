import pytest
from unittest.mock import patch, MagicMock
from src.pages.recipes.Analyse_recipes import DisplayManager, DataManager
import pandas as pd

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

# from src.process.recipes import Recipe

@pytest.fixture
def display_manager():
    with patch('src.utils.helper_data.load_dataset_from_file') as mock_load_dataset:
        mock_load_dataset.return_value = dummy_data
        with patch('src.pages.welcom.Welcom.Welcome.show_welcom') as mock_show_welcom:
            mock_show_welcom.return_value = dummy_data
            with patch('src.process.recipes.Recipe.detect_dataframe_anomalies') as mock_detect_anomalies:
                mock_detect_anomalies.return_value = {}
                with patch.object(DataManager, 'get_recipe_data') as mock_get_recipe_data:
                    # Créez un mock pour st.session_state.data
                    mock_session_state = MagicMock()
                    mock_session_state.data = dummy_data
                    # Assignez st.session_state au mock retourné par get_recipe_data
                    mock_get_recipe_data.return_value.st = MagicMock(session_state=mock_session_state)
                    
                    data_manager = DataManager()
                    display_manager = DisplayManager(data_manager=data_manager)
                    yield display_manager


def test_load_css(display_manager):
    with patch('src.pages.recipes.Analyse_recipes.CSSLoader.load') as mock_load_css:
        display_manager.load_css()
        mock_load_css.assert_any_call('src/css_pages/analyse_user.css')
        mock_load_css.assert_any_call('src/css_pages/recipe.css')


def test_home_tab(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.home_tab()
        mock_title.assert_called_once_with("🏠 Analyse de Recettes")


def test_analysis_tab(display_manager):
    with patch('streamlit.selectbox') as mock_selectbox:
        display_manager.analysis_tab()
        mock_selectbox.assert_called_once()


def test_display_contributors_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_contributors_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Contributions")


def test_display_tags_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_tags_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Tags de Recettes")


def test_display_submission_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_submission_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Soumissions")


def test_display_steps_and_time_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_steps_and_time_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Étapes et du Temps")



def test_display_nutrition_analysis(display_manager):
    with patch('streamlit.sidebar.header') as mock_title:
        display_manager.display_nutrition_analysis()
        mock_title.assert_called_once_with("Filtres Nutritionnels")

def test_display_data_structures(display_manager):
    with patch('streamlit.subheader') as mock_subheader:
        display_manager.display_data_structures()
        mock_subheader.assert_called_once_with(
            "Afficharger des 5 premiers elements du dataset")



def test_display_anomalies_values(display_manager):
    with patch('streamlit.checkbox') as mock_checkbox:
        display_manager.display_anomalies_values()
        mock_checkbox.assert_called_once_with("Afficher les valeurs abérantes")


def test_analyze_ingredients(display_manager):
    with patch('src.pages.recipes.Analyse_recipes.st.write') as mock_write, \
         patch('src.pages.recipes.Analyse_recipes.st.table') as mock_table, \
         patch('src.pages.recipes.Analyse_recipes.st.markdown') as mock_markdown, \
         patch('src.pages.recipes.Analyse_recipes.st_echarts') as mock_echarts:
        
        display_manager.analyze_ingredients()
        
        # Vérifiez que st.write a été appelé avec le bon message
        mock_write.assert_called_once_with("10 ingrédients les plus frequents dans les recettes")
        
        # Vérifiez que st.table a été appelé avec le DataFrame attendu
        mock_table.assert_called_once()
        
        # Vérifiez que st.markdown a été appelé avec le bon message
        mock_markdown.assert_called_once_with("### Nuage de mots")
        
        # Vérifiez que st_echarts a été appelé avec les options de nuage de mots
        mock_echarts.assert_called_once()
