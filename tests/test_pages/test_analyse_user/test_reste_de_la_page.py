from src.pages.analyse_user import (
    DataLoaderMango,
    DataAnalyzer,
    CSSLoader,
    VisualizationManager,
    StreamlitPage,
    main
)

import runpy
import sys
import numpy as np
from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

# -----------------------------
# Tests pour DataLoaderMango
# -----------------------------

def test_DataLoaderMango_init():
    connection_string = "mongodb://localhost:27017"
    database_name = "testdb"
    collection_names = ["test_collection"]
    limit = 1000

    loader = DataLoaderMango(connection_string, database_name, collection_names, limit)

    assert loader.connection_string == connection_string
    assert loader.database_name == database_name
    assert loader.collection_names == collection_names
    assert loader.limit == limit

@patch('src.pages.analyse_user.MongoDBConnector')
def test_DataLoaderMango_load_dataframe(mock_MongoDBConnector):
    # Configurer le mock
    mock_connector_instance = MagicMock()
    mock_MongoDBConnector.return_value = mock_connector_instance

    # Créer des DataFrames de test pour plusieurs collections
    sample_data1 = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    sample_data2 = pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})

    # Définir le comportement du mock en fonction du nom de la collection
    def load_collection_side_effect(collection_name, limit):
        if collection_name == "collection1":
            return sample_data1
        elif collection_name == "collection2":
            return sample_data2
        else:
            return pd.DataFrame()
    
    mock_connector_instance.load_collection_as_dataframe.side_effect = load_collection_side_effect

    # Appeler la méthode
    connection_string = "mongodb://localhost:27017"
    database_name = "testdb"
    collection_names = ["collection1", "collection2"]
    limit = 1000

    data = DataLoaderMango.load_dataframe(connection_string, database_name, collection_names, limit)

    # Assertions
    mock_MongoDBConnector.assert_called_once_with(connection_string, database_name)
    mock_connector_instance.connect.assert_called_once()
    assert mock_connector_instance.load_collection_as_dataframe.call_count == len(collection_names)
    mock_connector_instance.load_collection_as_dataframe.assert_any_call("collection1", limit=limit)
    mock_connector_instance.load_collection_as_dataframe.assert_any_call("collection2", limit=limit)
    mock_connector_instance.close.assert_called_once()

    expected_data = {
        "collection1": sample_data1,
        "collection2": sample_data2
    }
    pd.testing.assert_frame_equal(data["collection1"], sample_data1)
    pd.testing.assert_frame_equal(data["collection2"], sample_data2)

@patch('src.pages.analyse_user.DataLoaderMango.load_dataframe')
def test_DataLoaderMango_get_data(mock_load_dataframe):
    # Configurer le mock pour retourner un dictionnaire de DataFrames
    mock_load_dataframe.return_value = {
        "collection1": pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
        "collection2": pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
    }

    # Instancier la classe avec une liste de collections
    loader = DataLoaderMango("mongodb://localhost:27017", "testdb", ["collection1", "collection2"], 1000)

    # Appeler la méthode
    data = loader.get_data()

    # Assertions
    mock_load_dataframe.assert_called_once_with(
        "mongodb://localhost:27017", "testdb", ["collection1", "collection2"], 1000
    )
    assert data == mock_load_dataframe.return_value

# -----------------------------
# Tests pour DataAnalyzer
# -----------------------------

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "user_id": [1, 1, 2, 2],
        "rating": [5, 4, 3, 2],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])
    })

def test_analyze_user_no_data(sample_data):
    analyzer = DataAnalyzer(sample_data)
    analyzer.preprocess()
    
    # Utiliser un user_id qui n'existe pas
    result = analyzer.analyze_user(3)
    assert result is None

def test_analyze_user_ratings_frequencies_no_data(sample_data):
    analyzer = DataAnalyzer(sample_data)
    
    # Utiliser un user_id qui n'existe pas
    result = analyzer.analyze_user_ratings_frequencies(3)
    assert result is None

def test_analyze_user_ratings_frequencies_with_data(sample_data):
    analyzer = DataAnalyzer(sample_data)
    analyzer.preprocess()
    
    # Utiliser un user_id qui existe
    result = analyzer.analyze_user_ratings_frequencies(1)
    
    expected = [
        (4, sample_data[sample_data['rating'] == 4]),
        (5, sample_data[sample_data['rating'] == 5])
    ]
    
    assert len(result) == 2
    for (expected_rating, expected_data), (result_rating, result_data) in zip(expected, result):
        assert result_rating == expected_rating
        pd.testing.assert_frame_equal(result_data.reset_index(drop=True), expected_data.reset_index(drop=True))

# -----------------------------
# Tests pour CSSLoader
# -----------------------------

@patch('src.pages.analyse_user.load_css')
def test_CSSLoader_load(mock_load_css):
    CSSLoader.load("path/to/style.css")
    mock_load_css.assert_called_once_with("path/to/style.css")

# -----------------------------
# Tests pour VisualizationManager
# -----------------------------

@patch('src.pages.analyse_user.st.subheader')
@patch('src.pages.analyse_user.Grille')
@patch('src.pages.analyse_user.LineChart')
def test_display_line_chart(mock_LineChart, mock_Grille, mock_subheader):
    data = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    mock_line_chart = MagicMock()
    mock_LineChart.return_value = mock_line_chart

    try:
        VisualizationManager.display_line_chart(
            data=data,
            x="x",
            y="y",
            title="Test Line Chart"
        )
    except Exception as e:
        pytest.fail(f"display_line_chart raised an exception: {e}")

    mock_subheader.assert_called_once_with("Test Line Chart")
    mock_Grille.assert_called_once_with(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
    mock_Grille.return_value.afficher.assert_called_once()

@patch('src.pages.analyse_user.st.subheader')
@patch('src.pages.analyse_user.Grille')
@patch('src.pages.analyse_user.Histogramme')
def test_display_histogram(mock_Histogramme, mock_Grille, mock_subheader):
    frequency_data = [
        (5, pd.DataFrame({"year": [2024], "rating": [5]})),
        (4, pd.DataFrame({"year": [2024], "rating": [4]}))
    ]

    try:
        VisualizationManager.display_ratings_frequencies(
            frequency_data=frequency_data,
            x="year",
            title="Test Ratings Frequencies"
        )
    except Exception as e:
        pytest.fail(f"display_ratings_frequencies raised an exception: {e}")

    mock_subheader.assert_called_once_with("Test Ratings Frequencies")
    assert mock_Histogramme.call_count == 2
    assert mock_Grille.call_args[1]['nb_lignes'] == 2
    assert mock_Grille.call_args[1]['nb_colonnes'] == 3
    mock_Grille.return_value.afficher.assert_called_once()

# -----------------------------
# Tests pour StreamlitPage
# -----------------------------

@patch('src.pages.analyse_user.os.getenv')
@patch.object(DataLoaderMango, '__init__', lambda x, y, z, w, limit=2000: None)
def test_StreamlitPage_init(mock_getenv):
    # Configurer les variables d'environnement mockées
    mock_getenv.side_effect = lambda key, default=None: {
        "CONNECTION_STRING": "mongodb://localhost:27017",
        "DATABASE_NAME": "testdb",
        "COLLECTION_RAW_INTERACTIONS": "raw_interaction",
        "COLLECTION_RECIPES_NAME": "recipes"
    }.get(key, default)

    page = StreamlitPage()

    assert page.CONNECTION_STRING == "mongodb://localhost:27017"
    assert page.DATABASE_NAME == "testdb"
    assert page.COLLECTION_RAW_INTERACTIONS == "raw_interaction"
    assert page.COLLECTION_RECIPES_NAME == "recipes"
    assert page.COLLECTION_NAMES == ["raw_interaction", "recipes"]
    assert page.data is None

@patch('src.pages.analyse_user.CSSLoader.load')
def test_StreamlitPage_load_css(mock_css_load):
    page = StreamlitPage()
    page.load_css()
    mock_css_load.assert_called_once_with('src/css_pages/analyse_user.css')

@patch.object(DataLoaderMango, 'get_data')
def test_StreamlitPage_load_data(mock_get_data):
    # Configurer le mock pour retourner un dictionnaire de DataFrames avec les colonnes nécessaires
    mock_get_data.return_value = {
        "raw_interaction": pd.DataFrame({
            'user_id': [1, 2],
            'rating': [5, 4],
            'date': pd.to_datetime(["2024-01-01", "2024-01-02"])
        }),
        "recipes": pd.DataFrame({'submitted': pd.to_datetime(["2024-01-05", "2024-02-06"])})
    }

    page = StreamlitPage()
    page.load_data()

    # Vérifier que get_data a été appelé une seule fois sans arguments
    mock_get_data.assert_called_once()
    assert page.data == mock_get_data.return_value


# @patch('src.pages.analyse_user.DataAnalyzer')
# @patch('src.pages.analyse_user.VisualizationManager.display_line_chart')
# @patch('src.pages.analyse_user.VisualizationManager.display_ratings_frequencies')
# @patch('src.pages.analyse_user.VisualizationManager.display_histogram')
# @patch('src.pages.analyse_user.st.title')
# @patch('src.pages.analyse_user.st.checkbox')
# @patch('src.pages.analyse_user.st.subheader')
# @patch('src.pages.analyse_user.st.markdown')
# @patch('src.pages.analyse_user.st.divider')
# @patch('src.pages.analyse_user.st.write')
# @patch('src.pages.analyse_user.st.warning')
# @patch('src.pages.analyse_user.st.error')
# @patch('src.pages.analyse_user.st.number_input')
# def test_StreamlitPage_run_analysis(
#     mock_number_input,
#     mock_error,
#     mock_warning,
#     mock_write,
#     mock_divider,
#     mock_markdown,
#     mock_subheader,
#     mock_checkbox,
#     mock_title,
#     mock_display_histogram,
#     mock_display_ratings_frequencies,
#     mock_display_line_chart,
#     mock_DataAnalyzer
# ):
#     # Préparer les mocks avec un utilisateur ayant suffisamment de notes
#     sample_df_raw = pd.DataFrame({
#         "user_id": [1]*10 + [2]*2,  # user_id=1 a 10 notes, user_id=2 a 2 notes
#         "rating": [5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 3, 2],
#         "date": pd.to_datetime(["2024-01-01"]*12)
#     })
#     preprocessed_df_raw = sample_df_raw.copy()
#     preprocessed_df_raw['year'] = preprocessed_df_raw['date'].dt.year.astype(str)

#     sample_df_recipes = pd.DataFrame({
#         "submitted": pd.to_datetime(["2024-01-05", "2024-02-06"]),
#         # Ajoutez d'autres colonnes si nécessaire
#     })
#     page = StreamlitPage()
#     page.data = {
#         "raw_interaction": sample_df_raw,
#         "recipes": sample_df_recipes
#     }

#     # Créer des mocks séparés pour chaque instance de DataAnalyzer
#     analyzer_mock1 = MagicMock()
#     analyzer_mock1.preprocess.return_value = preprocessed_df_raw
#     analyzer_mock1.analyze_ratings_frequencies.return_value = [
#         (5, pd.DataFrame({"year": [2024], "rating": [5]})),
#         (4, pd.DataFrame({"year": [2024], "rating": [4]}))
#     ]
#     analyzer_mock1.analyze_monthly_ratings.return_value = pd.DataFrame({
#         "Mois": ["2024-01"],
#         "Note moyenne": [4.5]
#     })
#     analyzer_mock1.analyze_user_ratings_frequencies.return_value = [
#         (5, pd.DataFrame({"year": [2024], "rating": [5]})),
#         (4, pd.DataFrame({"year": [2024], "rating": [4]}))
#     ]
#     analyzer_mock1.analyze_user.return_value = pd.DataFrame({
#         "Mois": ["2024-01"],
#         "Note moyenne": [4.5]
#     })

#     analyzer_mock2 = MagicMock()
#     analyzer_mock2.analyze_activity_on_mangetamain.return_value = pd.DataFrame({
#         "year_month": ["2024-01"],
#         "recipe_count": [2]
#     })

#     # Configurer le side_effect pour retourner les mocks séparés
#     mock_DataAnalyzer.side_effect = [analyzer_mock1, analyzer_mock2]

#     # Configurer les entrées utilisateur pour un utilisateur éligible
#     mock_number_input.side_effect = [1, 1]  # user_id=1 a 10 notes

#     # Configurer les checkboxes pour afficher les explications
#     mock_checkbox.side_effect = [True, True, True, True, True, True]  # 6 checkboxes

#     # Appeler la méthode
#     page.run_analysis()

#     # Assertions sur les titres
#     mock_title.assert_any_call("Analyse de Fréquences")
#     mock_title.assert_any_call("Fréquence des notes au fil du temps")
#     mock_title.assert_any_call("Analyse des notes moyennes mensuelles")
#     mock_title.assert_any_call("Fréquence des Notes par utilisateur au fil du temps")
#     mock_title.assert_any_call("Analyse des notes par utilisateur")
#     mock_title.assert_any_call("Evolution de l’activité sur l’application Mangetamain")

#     # Vérifier les appels à VisualizationManager sur les méthodes patchées
#     mock_display_histogram.assert_called_once_with(
#         preprocessed_df_raw, 'rating', "Fréquence globale des notes"
#     )

#     # Vérifier les appels à display_ratings_frequencies
#     assert mock_display_ratings_frequencies.call_count == 2
#     calls = mock_display_ratings_frequencies.call_args_list

#     # Premier appel: Fréquence globale des notes
#     call1 = calls[0]
#     frequency_data_actual1 = call1.args[0]
#     x_actual1 = call1.args[1]
#     title_actual1 = call1.args[2]

#     assert x_actual1 == 'year'
#     assert title_actual1 == "Fréquence des Notes au fil du temps"

#     expected_frequency_data1 = analyzer_mock1.analyze_ratings_frequencies.return_value
#     assert len(frequency_data_actual1) == len(expected_frequency_data1)
#     for (actual_rating, actual_df), (expected_rating, expected_df) in zip(frequency_data_actual1, expected_frequency_data1):
#         assert actual_rating == expected_rating
#         pd.testing.assert_frame_equal(actual_df.reset_index(drop=True), expected_df.reset_index(drop=True))

#     # Deuxième appel: Fréquence des notes pour l'utilisateur spécifique
#     call2 = calls[1]
#     frequency_data_actual2 = call2.args[0]
#     x_actual2 = call2.args[1]
#     title_actual2 = call2.args[2]

#     assert x_actual2 == 'year'
#     assert title_actual2 == "Fréquence des Notes pour l'utilisateur 1"

#     expected_frequency_data2 = analyzer_mock1.analyze_user_ratings_frequencies.return_value
#     assert len(frequency_data_actual2) == len(expected_frequency_data2)
#     for (actual_rating, actual_df), (expected_rating, expected_df) in zip(frequency_data_actual2, expected_frequency_data2):
#         assert actual_rating == expected_rating
#         pd.testing.assert_frame_equal(actual_df.reset_index(drop=True), expected_df.reset_index(drop=True))

#     # Vérifier les appels à display_line_chart
#     assert mock_display_line_chart.call_count == 2

#     # Vérifier les appels avec les bons arguments pour les deux appels
#     # Premier appel pour les notes mensuelles
#     mock_display_line_chart.assert_any_call(
#         analyzer_mock1.analyze_monthly_ratings.return_value,
#         'Mois',
#         'Note moyenne',
#         "Notation moyenne mensuelle au fil du temps"
#     )

#     # Deuxième appel pour l'activité des recettes
#     mock_display_line_chart.assert_any_call(
#         analyzer_mock2.analyze_activity_on_mangetamain.return_value,
#         'year_month',
#         'recipe_count',
#         title=""
#     )

#     # Vérifier qu'aucune erreur ou warning n'a été appelé
#     mock_error.assert_not_called()
#     mock_warning.assert_not_called()


@patch('src.pages.analyse_user.st.set_page_config')
@patch.object(StreamlitPage, 'load_css')
@patch.object(StreamlitPage, 'load_data')
@patch.object(StreamlitPage, 'run_analysis')
def test_StreamlitPage_run(
    mock_run_analysis,
    mock_load_data,
    mock_load_css,
    mock_set_page_config
):
    # Créer une instance avec data non None
    page = StreamlitPage()
    page.data = {
        "raw_interaction": pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'rating': [5, 4], 'date': pd.to_datetime(["2024-01-01", "2024-01-02"])}),
        "recipes": pd.DataFrame({'submitted': pd.to_datetime(["2024-01-05", "2024-02-06"])})
    }

    # Appeler run
    page.run()

    # Assertions
    mock_set_page_config.assert_called_once_with(layout="wide")
    mock_load_css.assert_called_once()
    mock_load_data.assert_called_once()
    mock_run_analysis.assert_called_once()

# -----------------------------
# Autres
# -----------------------------

@patch('src.pages.analyse_user.st.warning')
def test_run_analysis_missing_rating_column(mock_st_warning):
    # Préparer les données sans la colonne 'rating'
    sample_df = pd.DataFrame({
        "user_id": [1, 2],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"])
    })
    
    page = StreamlitPage()
    page.data = {
        "raw_interaction": sample_df,
        "recipes": pd.DataFrame({'submitted': pd.to_datetime(["2024-01-05", "2024-02-06"])})
    }
    
    with patch.object(DataAnalyzer, 'preprocess', return_value=sample_df):
        with patch.object(DataAnalyzer, 'analyze_ratings_frequencies', return_value=None):
            page.run_analysis()
    
    # Utiliser assert_any_call pour s'assurer que le warning a été appelé au moins une fois avec le message spécifique
    mock_st_warning.assert_any_call("La colonne 'rating' est absente du fichier.")

@patch('src.pages.analyse_user.st.error')
def test_run_analysis_missing_user_id_column(mock_st_error):
    # Préparer les données sans la colonne 'user_id'
    sample_df = pd.DataFrame({
        "rating": [5, 4],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"])
    })
    # 'year' serait ajouté par preprocess, mais c'est mocké
    sample_df['year'] = sample_df['date'].dt.year.astype(str)
    
    page = StreamlitPage()
    page.data = {
        "raw_interaction": sample_df,
        "recipes": pd.DataFrame({'submitted': pd.to_datetime(["2024-01-05", "2024-02-06"])})
    }
    
    with patch.object(DataAnalyzer, 'preprocess', return_value=sample_df):
        page.run_analysis()
    
    # Utiliser assert_any_call pour s'assurer que l'erreur a été appelée avec le message spécifique
    mock_st_error.assert_any_call("La colonne 'user_id' est absente du fichier.")

@patch('src.pages.analyse_user.StreamlitPage')
def test_main_run(mock_StreamlitPage):
    """
    Teste l'exécution de la fonction main pour s'assurer que StreamlitPage.run() est appelé.
    """
    # Arrange : Préparer le mock
    mock_instance = mock_StreamlitPage.return_value
    mock_instance.run.return_value = None

    # Act : Appeler main
    main()

    # Assert : Vérifier que StreamlitPage a été instancié et que run() a été appelé
    mock_StreamlitPage.assert_called_once()
    mock_instance.run.assert_called_once()
