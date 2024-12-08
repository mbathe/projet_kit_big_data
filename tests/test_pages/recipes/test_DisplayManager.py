from unittest.mock import patch, MagicMock
import pytest
from unittest.mock import patch
from src.pages.recipes.Analyse_recipes import DisplayManager, DataManager
import pandas as pd
import plotly.express as px
import streamlit as st
from src.utils.static import constribution_data
import plotly.graph_objects as go


@pytest.fixture
def display_manager():
    data_manager = DataManager()
    return DisplayManager(data_manager=data_manager)


@pytest.fixture
def contributor_data():
    return constribution_data


@pytest.fixture
def contributor_df(contributor_data):
    return pd.DataFrame(
        list(contributor_data['top_contributors'].items()),
        columns=['ID Utilisateur', 'Nombre de contributions']
    )


@pytest.fixture
def color_theme(contributor_data):
    return st.sidebar.selectbox(
        "Thème de couleur",
        ["blues", "viridis", "magma", "plasma"]
    )


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
    with patch('streamlit.write') as mock_write:
        display_manager.analyze_ingredients()
        mock_write.assert_called_once_with(
            "10 ingrédients les plus frequents dans les recettes")


def test_display_recommandation(display_manager):
    with patch('streamlit.markdown') as mock_markdown:
        display_manager.recommandation_page()
        mock_markdown.assert_called()
        # mock_markdown.assert_called_once_with("Recommandations Personnalisées")


def test_display_tab_success(display_manager):
    with patch('streamlit.tabs') as mock_tabs:
        display_manager.display_tab()
        mock_tabs.assert_called_with(
            ['📈 Par Année', '📅 Par Mois', '📆 Par Jour de la Semaine'])


def test_display_slider(display_manager):
    with patch('streamlit.title') as mock_tabs:
        display_manager.sidebar()
        mock_tabs.assert_called_with("⚙️ Configuration")


def test_create_distribution_figure(display_manager, contributor_data):
    fig = display_manager._create_distribution_figure(contributor_data)
    assert isinstance(fig, go.Figure)

    # Vérifiez que le nombre de traces est correct
    assert len(fig.data) == 1

    # Vérifiez que les données de la trace sont correctes
    trace = fig.data[0]
    assert trace.name == 'Statistiques'

    # Vérifiez que la mise à jour de la mise en page s'est bien faite
    assert fig.layout.height == 400


def test_create_top_contributors_figure(display_manager, contributor_df, color_theme):

    with patch('streamlit.subheader') as mock_subheader:
        display_manager._display_top_contributors(
            contributor_df, color_theme)
        mock_subheader.assert_called_with(
            "Analyse des principaux contributeurs")
        #


def test__display_comparative_analysis(display_manager, contributor_df, contributor_data):

    with patch('streamlit.plotly_chart') as mock_st_plotly_chart:
        display_manager._display_comparative_analysis(
            contributor_df, contributor_data)
        assert mock_st_plotly_chart.called

        fig_radar = mock_st_plotly_chart.call_args[0][0]
        assert isinstance(fig_radar, go.Figure)
        assert len(fig_radar.data) == 3


def test_display_anomalie(display_manager):
    with patch('streamlit.checkbox') as mock_checkbox:
        display_manager.display_anomalies_values()
        mock_checkbox.assert_called_with("Afficher les valeurs abérantes")


## AJOUTE PAR SACHA ##
from datetime import date

@patch("streamlit.sidebar")
@patch("streamlit.date_input")
@patch("streamlit.button")
@patch("streamlit.success")
@patch("streamlit.error")
def test_sidebar_date_range(mock_error, mock_success, mock_button, mock_date_input, mock_sidebar, display_manager):
    # Test lignes 208-215
    # Simuler une sélection de date
    mock_date_input.return_value = (date(2020,1,2), date(2020,1,1))  # start > end
    mock_button.return_value = True
    display_manager.sidebar()
    mock_error.assert_called_with("La date de début doit être antérieure ou égale à la date de fin.")

    # Changer pour des dates valides
    mock_error.reset_mock()
    mock_success.reset_mock()
    mock_date_input.return_value = (date(2020,1,1), date(2020,1,2))
    display_manager.sidebar()
    mock_success.assert_called_with("Période d'analyse: 2020-01-01 à 2020-01-02")

@patch("streamlit.sidebar")
@patch("streamlit.radio")
@patch("streamlit.download_button")
@patch("streamlit.success")
@patch("logging.error")
def test_export_json(mock_log, mock_success, mock_download_button, mock_radio, mock_sidebar, display_manager):
    # Test lignes 227-233
    # Simuler le choix JSON et le bouton de téléchargement
    mock_radio.return_value = "JSON"
    mock_download_button.return_value = True
    display_manager.sidebar()
    mock_success.assert_called_with("Export en cours...")

@patch("logging.error")
def test_home_tab_error_handling(mock_log, display_manager):
    # Test lignes 279-292 (try/except dans home_tab)
    # Simuler une exception dans home_tab
    with patch.object(display_manager.data_manager, 'get_recipe_data', side_effect=Exception("HomeTab Error")):
        display_manager.home_tab()
        mock_log.assert_called_once_with("Erreur dans home_tab: HomeTab Error")

@patch("logging.error")
def test_analysis_tab_error_handling(mock_log, display_manager):
    # Test lignes 314-316
    with patch("streamlit.selectbox", side_effect=Exception("AnalysisTab Error")):
        display_manager.analysis_tab()
        mock_log.assert_called_once_with("Erreur dans analysis_tab: AnalysisTab Error")

@patch("logging.error")
def test_display_contributors_analysis_error(mock_log, display_manager):
    # Test lignes 415-416
    # Simuler une exception dans display_contributors_analysis
    with patch.object(display_manager, '_create_distribution_figure', side_effect=Exception("Contrib Error")):
        display_manager.display_contributors_analysis()
        mock_log.assert_called_once_with("Erreur dans display_contributors_analysis: Contrib Error")


@patch("logging.error")
def test_create_top_contributors_figure_error(mock_log, display_manager):
    # Lignes 473-474 : Erreur dans _create_top_contributors_figure
    with patch("plotly.express.bar", side_effect=Exception("TopContrib Error")):
        display_manager._create_top_contributors_figure(pd.DataFrame(), "blues")
        mock_log.assert_called_once_with("Erreur dans _create_top_contributors_figure: TopContrib Error")


@patch("logging.error")
def test_display_top_contributors_error(mock_log, display_manager):
    # Lignes 532-533 : Erreur dans _display_top_contributors
    with patch("streamlit.slider", side_effect=Exception("TopContributors Error")):
        display_manager._display_top_contributors(pd.DataFrame(), "blues")
        mock_log.assert_called_once_with("Erreur dans _display_top_contributors: TopContributors Error")


@patch("logging.error")
def test_display_tags_analysis_error(mock_log, display_manager):
    # Ligne 639 : Erreur dans display_tags_analysis
    with patch.object(display_manager.data_manager, 'analyze_tags', side_effect=Exception("TagsAnalysis Error")):
        display_manager.display_tags_analysis()
        mock_log.assert_called_once_with("Erreur dans display_tags_analysis: TagsAnalysis Error")

@patch("logging.error")
def test_display_submission_analysis_error(mock_log, display_manager):
    # Lignes 744-745 : Erreur dans display_submission_analysis
    with patch.object(display_manager.data_manager, 'analyze_temporal_distribution', side_effect=Exception("Submission Error")):
        display_manager.display_submission_analysis()
        mock_log.assert_called_once_with("Error in display_submission_analysis: Submission Error")

@patch("logging.error")
def test_display_steps_and_time_analysis_error(mock_log, display_manager):
    # Ligne 852 : Erreur dans display_steps_and_time_analysis
    with patch.object(display_manager.data_manager, 'analyze_recipe_complexity', side_effect=Exception("StepsTime Error")):
        display_manager.display_steps_and_time_analysis()
        mock_log.assert_called_once_with("Error in display_steps_and_time_analysis: StepsTime Error")

@patch("logging.error")
def test_display_nutrition_analysis_error(mock_log, display_manager):
    # Lignes 899-900 : Erreur dans display_nutrition_analysis
    with patch.object(display_manager.data_manager, 'analyze_nutrition', side_effect=Exception("Nutrition Error")):
        display_manager.display_nutrition_analysis()
        mock_log.assert_called_once_with("Error in display_nutrition_analysis: Nutrition Error")

@patch("logging.error")
def test_display_data_structures_error(mock_log, display_manager):
    # Lignes 953-954 : Erreur dans display_data_structures
    with patch.object(display_manager.data_manager, 'get_recipe_data', side_effect=Exception("DataStructures Error")):
        display_manager.display_data_structures()
        mock_log.assert_called_once_with("Error in display_data_structures: DataStructures Error")



@patch("logging.error")
def test_display_tab_error(mock_log, display_manager):
    # Lignes 1020-1021 : Erreur dans display_tab
    with patch("streamlit.tabs", side_effect=Exception("Tab Error")):
        display_manager.display_tab()
        mock_log.assert_called_once_with("Error in display_tab: Tab Error")

