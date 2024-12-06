import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import logging

# Ajuster les imports selon votre structure de projet
from src.pages.analyse_user import DataLoaderMango, DataAnalyzer, VisualizationManager, StreamlitPage

@pytest.fixture
def dummy_data():
    return pd.DataFrame({
        'date': pd.date_range(start='2020-01-01', periods=5, freq='M'),
        'rating': [5,4,5,3,2],
        'user_id': [1,1,2,2,2],
        'submitted': pd.date_range(start='2020-01-01', periods=5, freq='M')
    })

@pytest.fixture
def mongo_data():
    # Simuler données provenant de Mongo
    return {
        'raw_interaction': pd.DataFrame({
            'date': pd.date_range('2001-01-01', periods=5, freq='Y'),
            'rating': [5,5,4,3,1],
            'user_id': [1,2,3,3,1]
        }),
        'recipes': pd.DataFrame({
            'submitted': pd.date_range('2001-01-01', periods=5, freq='Y')
        })
    }

@patch("src.pages.analyse_user.MongoDBConnector")
@patch("logging.getLogger")
def test_dataloader_mango_initialization(mock_logger, mock_connector):
    # Test lignes 162-164: Initialisation DataLoaderMango
    instance = DataLoaderMango("connection_string", "db_name", ["collection1", "collection2"], limit=1000)
    logger_instance = mock_logger.return_value
    logger_instance.info.assert_called_with("Initialisation de DataLoaderMango")

@patch("src.pages.analyse_user.MongoDBConnector")
@patch("logging.getLogger")
def test_dataloader_mango_get_data(mock_logger, mock_connector):
    # Test ligne 206 (appel load_dataframe) et 270 (return data_frames)
    mock_conn = MagicMock()
    mock_connector.return_value = mock_conn
    mock_conn.connect.return_value = None
    mock_conn.load_collection_as_dataframe.side_effect = [
        pd.DataFrame({"col":[1,2]}),
        pd.DataFrame({"col":[3,4]})
    ]
    mock_conn.close.return_value = None

    dl = DataLoaderMango("connection_string", "db_name", ["c1","c2"], limit=10)
    data = dl.get_data()

    assert "c1" in data
    assert "c2" in data
    # Vérifier le logging
    mock_logger.return_value.info.assert_any_call("Récupération des données")

@patch("logging.getLogger")
def test_data_analyzer_preprocessing_with_date(mock_logger, dummy_data):
    # Test 409-410 (preprocessing) et 430 (warning si pas de date)
    analyzer = DataAnalyzer(dummy_data)
    processed = analyzer.preprocess()
    assert 'year' in processed.columns
    # Vérifier logging
    mock_logger.return_value.info.assert_any_call("Prétraitement des données")

@patch("logging.getLogger")
def test_data_analyzer_preprocessing_no_date(mock_logger):
    # Si pas de colonne 'date', warning
    df_no_date = pd.DataFrame({'rating':[5,4,3]})
    analyzer = DataAnalyzer(df_no_date)
    analyzer.preprocess()
    mock_logger.return_value.warning.assert_called_with("La colonne 'date' est absente des données")

@patch("logging.getLogger")
def test_analyze_ratings_frequencies(mock_logger, dummy_data):
    # Test 576-578 Analyse frequence
    analyzer = DataAnalyzer(dummy_data)
    freq_data = analyzer.analyze_ratings_frequencies()
    assert len(freq_data) > 0
    mock_logger.return_value.info.assert_any_call("Analyse des fréquences des notes")

@patch("logging.getLogger")
def test_analyze_monthly_ratings_columns_missing(mock_logger):
    # Test 604-616: si 'date' ou 'rating' absentes -> warning
    df = pd.DataFrame({'user_id':[1,2]})
    analyzer = DataAnalyzer(df)
    # On appelle une méthode du run_analysis plus tard, simulons ici
    # Normalement, c'est dans run_analysis que la condition est vérifiée, on teste le DataAnalyzer directement.
    # Dans run_analysis, s'il manque date ou rating, st.warning est appelé et logger.warning. On ne peut pas tester st.warning facilement sans patch.
    # On se contente de tester la logique interne.
    # La logique interne est dans analyze_monthly_ratings (ligne 631-648)
    # On appelle analyze_monthly_ratings -> va échouer car pas date ni rating
    with pytest.raises(KeyError):
        analyzer.analyze_monthly_ratings()

@patch("logging.getLogger")
def test_analyze_user_ratings_frequencies_user_missing(mock_logger, dummy_data):
    # Test 662-684: Analyse user freq, si user_id non présent
    analyzer = DataAnalyzer(dummy_data)
    result = analyzer.analyze_user_ratings_frequencies(999)
    assert result is None
    mock_logger.return_value.warning.assert_any_call("Aucune donnée de fréquence trouvée pour l'utilisateur ID: 999")

@patch("logging.getLogger")
def test_analyze_user_missing_data(mock_logger, dummy_data):
    # Test 700-723: Analyse des notes utilisateur spécifique
    analyzer = DataAnalyzer(dummy_data)
    # user_id pas dans df
    res = analyzer.analyze_user(999)
    assert res is None
    mock_logger.return_value.warning.assert_called_with("Aucune donnée trouvée pour l'utilisateur ID: 999")

@patch("logging.getLogger")
def test_analyze_activity_missing_submitted(mock_logger):
    # Test 742-757, 760, 772: analyse_activity_on_mangetamain sans submitted
    df_no_submitted = pd.DataFrame({'rating':[5,4,3], 'date':pd.date_range('2021-01-01', periods=3)})
    analyzer = DataAnalyzer(df_no_submitted)
    res = analyzer.analyze_activity_on_mangetamain()
    assert res is None
    mock_logger.return_value.warning.assert_called_with("La colonne 'submitted' est absente des données")


@patch("logging.getLogger")
def test_end_of_code(mock_logger):
    # Ligne 866 est la fin du code
    # On teste simplement l'appel de main() sans erreur
    from src.pages.analyse_user import main
    with patch("streamlit.set_page_config"), \
         patch("streamlit.error"), \
         patch("streamlit.title"), \
         patch("streamlit.checkbox"), \
         patch("streamlit.write"), \
         patch("streamlit.subheader"), \
         patch("streamlit.markdown"), \
         patch("streamlit.divider"):
        main()
    mock_logger.return_value.info.assert_any_call("Démarrage de l'application Streamlit")
