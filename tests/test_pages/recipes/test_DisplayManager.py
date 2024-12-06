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
