import pytest
from unittest.mock import patch, MagicMock
# Remplacez 'src.pages.recipes' par le nom de votre module
from src.pages.recipes import DisplayManager, DataManager


@pytest.fixture
def display_manager():
    data_manager = DataManager()
    return DisplayManager(data_manager=data_manager)


def test_load_css(display_manager):
    with patch('src.pages.recipes.CSSLoader.load') as mock_load_css:
        display_manager.load_css()
        mock_load_css.assert_any_call('src/css_pages/analyse_user.css')
        mock_load_css.assert_any_call('src/css_pages/recipe.css')


def test_sidebar(display_manager):
    with patch('streamlit.sidebar') as mock_sidebar:
        display_manager.sidebar()
        mock_sidebar.assert_called_once()


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
    with patch('streamlit.title') as mock_title:
        display_manager.display_nutrition_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Données")


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
    with patch('streamlit.write') as mock_write:
        display_manager.analyze_ingredients()
        mock_write.assert_called_once_with(
            "10 ingrédients les plus frequents dans les recettes")


def test_display_tab(display_manager):
    with patch('streamlit.tabs') as mock_tabs:
        display_manager.display_tab()
        mock_tabs.assert_called_once_with(["Accueil", "Analyse", "Prediction"])
