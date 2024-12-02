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
    collection_name = "test_collection"
    limit = 1000

    loader = DataLoaderMango(connection_string, database_name, collection_name, limit)

    assert loader.connection_string == connection_string
    assert loader.database_name == database_name
    assert loader.collection_name == collection_name
    assert loader.limit == limit


@patch('src.pages.analyse_user.MongoDBConnector')
def test_DataLoaderMango_load_dataframe(mock_MongoDBConnector):
    # Configurer le mock
    mock_connector_instance = MagicMock()
    mock_MongoDBConnector.return_value = mock_connector_instance
    sample_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_connector_instance.load_collection_as_dataframe.return_value = sample_data

    # Appeler la méthode
    connection_string = "mongodb://localhost:27017"
    database_name = "testdb"
    collection_name = "test_collection"
    limit = 1000

    data = DataLoaderMango.load_dataframe(connection_string, database_name, collection_name, limit)

    # Assertions
    mock_MongoDBConnector.assert_called_once_with(connection_string, database_name)
    mock_connector_instance.connect.assert_called_once()
    mock_connector_instance.load_collection_as_dataframe.assert_called_once_with(collection_name, limit=limit)
    mock_connector_instance.close.assert_called_once()
    pd.testing.assert_frame_equal(data, sample_data)


@patch('src.pages.analyse_user.DataLoaderMango.load_dataframe')
def test_DataLoaderMango_get_data(mock_load_dataframe):
    # Configurer le mock
    mock_load_dataframe.return_value = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

    # Instancier la classe
    loader = DataLoaderMango("mongodb://localhost:27017", "testdb", "test_collection", 1000)

    # Appeler la méthode
    data = loader.get_data()

    # Assertions
    mock_load_dataframe.assert_called_once_with(
        "mongodb://localhost:27017", "testdb", "test_collection", 1000
    )
    pd.testing.assert_frame_equal(data, mock_load_dataframe.return_value)


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
def test_display_histogram(mock_LineChart, mock_Grille, mock_subheader):
    data = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    mock_histogram = MagicMock()
    mock_LineChart.return_value = mock_histogram

    try:
        VisualizationManager.display_histogram(
            data=data,
            x="x",
            title="Test Histogram"
        )
    except Exception as e:
        pytest.fail(f"display_histogram raised an exception: {e}")

    mock_subheader.assert_called_once_with("Test Histogram")
    mock_Grille.assert_called_once_with(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
    mock_Grille.return_value.afficher.assert_called_once()


@patch('src.pages.analyse_user.st.subheader')
@patch('src.pages.analyse_user.Grille')
@patch('src.pages.analyse_user.Histogramme')
def test_display_ratings_frequencies(mock_Histogramme, mock_Grille, mock_subheader):
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
        "COLLECTION_RAW_INTERACTIONS": "raw_interaction"
    }.get(key, default)

    page = StreamlitPage()

    assert page.CONNECTION_STRING == "mongodb://localhost:27017"
    assert page.DATABASE_NAME == "testdb"
    assert page.COLLECTION_RAW_INTERACTIONS == "raw_interaction"
    assert page.data is None


@patch('src.pages.analyse_user.CSSLoader.load')
def test_StreamlitPage_load_css(mock_css_load):
    page = StreamlitPage()
    page.load_css()
    mock_css_load.assert_called_once_with('src/css_pages/analyse_user.css')


@patch.object(DataLoaderMango, 'get_data')
@patch('src.pages.analyse_user.st.write')
def test_StreamlitPage_load_data(mock_st_write, mock_get_data):
    mock_get_data.return_value = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    page = StreamlitPage()
    page.load_data()

    mock_get_data.assert_called_once()
    mock_st_write.assert_called_once()
    pd.testing.assert_frame_equal(page.data, mock_get_data.return_value)


@patch('src.pages.analyse_user.DataAnalyzer')
@patch('src.pages.analyse_user.VisualizationManager')
@patch('src.pages.analyse_user.st.title')
@patch('src.pages.analyse_user.st.warning')
@patch('src.pages.analyse_user.st.error')
@patch('src.pages.analyse_user.st.number_input')
def test_StreamlitPage_run_analysis(
    mock_number_input,
    mock_error,
    mock_warning,
    mock_title,
    mock_VisualizationManager,
    mock_DataAnalyzer
):
    # Préparer les mocks
    sample_df = pd.DataFrame({
        "user_id": [1, 1, 2, 2],
        "rating": [5, 4, 3, 2],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])
    })
    page = StreamlitPage()
    page.data = sample_df

    # Configurer DataAnalyzer mock
    analyzer_instance = mock_DataAnalyzer.return_value
    analyzer_instance.preprocess.return_value = sample_df
    # Retourner des données non vides pour que display_ratings_frequencies soit appelé
    analyzer_instance.analyze_ratings_frequencies.return_value = [
        (5, pd.DataFrame({"year": [2024], "rating": [5]})),
        (4, pd.DataFrame({"year": [2024], "rating": [4]}))
    ]
    analyzer_instance.analyze_monthly_ratings.return_value = pd.DataFrame({
        "Mois": ["2024-01"],
        "Note moyenne": [4.5]
    })
    analyzer_instance.analyze_user_ratings_frequencies.return_value = [
        (5, pd.DataFrame({"year": [2024], "rating": [5]})),
        (4, pd.DataFrame({"year": [2024], "rating": [4]}))
    ]
    analyzer_instance.analyze_user.return_value = pd.DataFrame({
        "Mois": ["2024-01"],
        "Note moyenne": [4.5]
    })

    # Configurer les entrées utilisateur
    mock_number_input.side_effect = [1, 1]  # user_id pour les deux analyses

    # Appeler la méthode
    page.run_analysis()

    # Assertions
    mock_title.assert_any_call("Analyse de Fréquences")
    mock_title.assert_any_call("Fréquence des notes au fil du temps")
    mock_title.assert_any_call("Analyse des notes moyennes mensuelles")
    mock_title.assert_any_call("Fréquence des Notes par utilisateur au fil du temps")
    mock_title.assert_any_call("Analyse des notes par utilisateur")

    # Vérifier les appels à VisualizationManager
    assert mock_VisualizationManager.display_histogram.call_count == 1
    assert mock_VisualizationManager.display_ratings_frequencies.call_count == 2  # global et user
    assert mock_VisualizationManager.display_line_chart.call_count == 2  # monthly et user

    # Vérifier qu'aucune erreur ou warning n'a été appelé
    mock_error.assert_not_called()
    mock_warning.assert_not_called()


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
    page.data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

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
    page.data = sample_df
    
    with patch.object(DataAnalyzer, 'preprocess', return_value=sample_df):
        with patch.object(DataAnalyzer, 'analyze_ratings_frequencies', return_value=None):
            page.run_analysis()
    
    mock_st_warning.assert_called_with("La colonne 'rating' est absente du fichier.")



@patch('src.pages.analyse_user.st.error')
def test_run_analysis_missing_user_id_column(mock_st_error):
    # Préparer les données sans la colonne 'user_id'
    sample_df = pd.DataFrame({
        "rating": [5, 4],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"])
    })
    # Ajouter la colonne 'year' comme le ferait 'preprocess'
    sample_df['year'] = sample_df['date'].dt.year.astype(str)
    
    page = StreamlitPage()
    page.data = sample_df
    
    with patch.object(DataAnalyzer, 'preprocess', return_value=sample_df):
        page.run_analysis()
    
    mock_st_error.assert_called_with("La colonne 'user_id' est absente du fichier.")


@patch('src.pages.analyse_user.StreamlitPage.run_analysis')
@patch('src.pages.analyse_user.StreamlitPage.load_data')
@patch('src.pages.analyse_user.StreamlitPage.load_css')
@patch('src.pages.analyse_user.st.set_page_config')
def test_StreamlitPage_run_end_to_end(
    mock_set_page_config,
    mock_load_css,
    mock_load_data,
    mock_run_analysis,
    sample_data
):
    # Configurer les mocks
    mock_load_data.return_value = None
    mock_run_analysis.return_value = None
    
    page = StreamlitPage()
    page.data = sample_data
    
    try:
        page.run()
    except Exception as e:
        pytest.fail(f"StreamlitPage.run() raised an exception: {e}")
    
    mock_set_page_config.assert_called_once_with(layout="wide")
    mock_load_css.assert_called_once()
    mock_load_data.assert_called_once()
    mock_run_analysis.assert_called_once()



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