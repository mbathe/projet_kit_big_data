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
    assert mock_connector_instance.load_collection_as_dataframe.call_count == 0




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
