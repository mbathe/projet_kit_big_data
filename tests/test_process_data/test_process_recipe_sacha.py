import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import logging
from datetime import datetime, date
import numpy as np
import sys
import os
import streamlit as st

sys.path.append("..")  # si nécessaire, pour remonter d'un dossier
from src.process.recipes import Recipe, DEPLOIEMENT_SITE, YEAR_MIN, YEAR_MAX

@pytest.fixture
def mock_session_state():
    # Simuler un session_state Streamlit
    class MockSessionState(dict):
        def __getattr__(self, name):
            return self[name] if name in self else None
        def __setattr__(self, name, value):
            self[name] = value
    return MockSessionState()

@pytest.fixture
def recipe_instance(mock_session_state):
    # Créer une instance de Recipe avec un mock du session_state
    with patch("streamlit.session_state", new=mock_session_state):
        with patch("streamlit.empty"), patch("streamlit.spinner"):
            r = Recipe(date_start=datetime(2001,1,1), date_end=datetime(2002,1,1))
    return r

@patch("src.process.recipes.DEPLOIEMENT_SITE", "LOCAL")
@patch("src.process.recipes.os.getenv", return_value="/path/to/dataset")
@patch("src.process.recipes.load_dataset_from_file")
@patch("src.process.recipes.Welcome.show_welcom")
def test_initialize_session_state_local(mock_welcome, mock_load_dataset, mock_getenv, recipe_instance):
    # Simuler que show_welcom appelle vraiment load_dataset_from_file
    def show_welcom_side_effect(deploiement, loader_func, file_path, *args, **kwargs):
        return loader_func(file_path, *args, **kwargs)

    mock_welcome.side_effect = show_welcom_side_effect
    mock_load_dataset.return_value = pd.DataFrame({"col":[1,2,3]})

    start_date = date(2002, 1, 1)
    end_date = date(2002, 12, 31)
    recipe_instance.initialize_session_state(start_date, end_date)

    # Maintenant load_dataset_from_file devrait être appelé une fois
    mock_load_dataset.assert_called_once()


@patch("src.process.recipes.logging.error")
@patch("src.process.recipes.DEPLOIEMENT_SITE", "LOCAL")
def test_initialize_session_state_exception(mock_log_error, recipe_instance):
    # Test ligne 175 : déclenchement d'une exception dans initialize_session_state
    # On va simuler une erreur dans load_dataset_from_file
    with patch("src.process.recipes.load_dataset_from_file", side_effect=Exception("Test Error")):
        with pytest.raises(Exception, match="Test Error"):
            recipe_instance.initialize_session_state(date(2003,1,1), date(2003,12,31))
        mock_log_error.assert_any_call("Error in initialize_session_state: Test Error")

@patch("src.process.recipes.logging.error")
def test_clean_dataframe_std_method(mock_log_error, recipe_instance):
    df = pd.DataFrame({"value":[10, 10, 10, 1000]})
    recipe_instance.st.session_state.data = df
    recipe_instance.annomalis = {'missing_values': pd.DataFrame()}
    recipe_instance.clean_dataframe(cleaning_method='std', threshold=1.0)
    # Avec un threshold plus strict, 1000 sera considéré comme un outlier
    assert len(recipe_instance.st.session_state.data) < len(df)


@patch("src.process.recipes.logging.error")
def test_clean_dataframe_missing_values(mock_log_error, recipe_instance):
    # Test lignes 618-620 : gestion des valeurs manquantes
    # DataFrame avec des valeurs manquantes
    df = pd.DataFrame({"value":[1, np.nan, 3]})
    recipe_instance.st.session_state.data = df
    # On simule qu'il y a des missing_values détectées
    recipe_instance.annomalis = {
        'missing_values': pd.DataFrame({
            'Missing Count':[1],
            'Missing Percentage':[33.3]
        }, index=['value'])
    }

    recipe_instance.clean_dataframe(cleaning_method='std', threshold=3.0)
    # La ligne avec NaN doit être supprimée
    assert recipe_instance.st.session_state.data['value'].isnull().sum() == 0
    assert len(recipe_instance.st.session_state.data) == 2
    mock_log_error.assert_not_called()

@patch("src.process.recipes.MongoClient")
@patch("src.process.recipes.st.error")  # Mock pour st.error
def test_fetch_data_from_mongodb_exception(mock_st_error, mock_mongo_client, recipe_instance):
    # Créer un mock pour client
    mock_client = MagicMock()
    # Simuler une exception lors de l'appel à client.admin.command
    mock_client.admin.command.side_effect = Exception("Erreur simulée")
    mock_mongo_client.return_value = mock_client

    # Appel de la méthode avec des arguments fictifs
    result = recipe_instance.fetch_data_from_mongodb(
        connection_string="mongodb://fake_connection_string",
        database_name="fake_db",
        collection_name="fake_collection",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    # Vérifications
    assert result.empty  # Doit renvoyer un DataFrame vide
    mock_st_error.assert_called_once_with("Erreur lors de la récupération des données : Erreur simulée")
    mock_client.close.assert_called_once()  # Vérifie que client.close() a été appelé

@patch("src.process.recipes.MongoClient")
def test_fetch_data_from_mongodb_with_data(mock_mongo_client, recipe_instance):
    # Mock pour client et collection
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value = [
        {"submitted": "2024-01-01", "name": "Recipe 1"},
        {"submitted": "2024-01-02", "name": "Recipe 2"}
    ]
    mock_client.__getitem__.return_value = {"fake_collection": mock_collection}
    mock_mongo_client.return_value = mock_client

    # Appel de la méthode
    result = recipe_instance.fetch_data_from_mongodb(
        connection_string="mongodb://fake_connection_string",
        database_name="fake_db",
        collection_name="fake_collection",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )

    # Vérifications
    assert not result.empty  # Le DataFrame ne doit pas être vide
    assert len(result) == 2  # Vérifie que deux entrées ont été récupérées
    assert "name" in result.columns  # Vérifie que la colonne "name" est présente


@patch("src.process.recipes.MongoClient")
@patch("src.process.recipes.st.warning")  # Mock pour st.warning
def test_fetch_data_from_mongodb_no_data(mock_st_warning, mock_mongo_client, recipe_instance):
    # Mock pour client et collection
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value = []  # Aucune donnée retournée
    mock_client.__getitem__.return_value = {"fake_collection": mock_collection}
    mock_mongo_client.return_value = mock_client

    # Appel de la méthode
    result = recipe_instance.fetch_data_from_mongodb(
        connection_string="mongodb://fake_connection_string",
        database_name="fake_db",
        collection_name="fake_collection",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )

    # Vérifications
    assert result.empty  # Le DataFrame doit être vide
    mock_st_warning.assert_called_once_with(
        "Aucune donnée trouvée pour cet intervalle de dates."
    )  # Vérifie que le message d'avertissement est affiché

@patch("src.process.recipes.MongoClient")
@patch("src.process.recipes.st.error")  # Mock pour st.error
def test_fetch_data_from_mongodb_query_exception(mock_st_error, mock_mongo_client, recipe_instance):
    # Mock pour client et collection
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.side_effect = Exception("Erreur lors de la recherche")
    mock_client.__getitem__.return_value = {"fake_collection": mock_collection}
    mock_mongo_client.return_value = mock_client

    # Appel de la méthode
    result = recipe_instance.fetch_data_from_mongodb(
        connection_string="mongodb://fake_connection_string",
        database_name="fake_db",
        collection_name="fake_collection",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )

    # Vérifications
    assert result.empty  # Le DataFrame doit être vide
    mock_st_error.assert_called_once_with(
        "Erreur lors de la récupération des données : Erreur lors de la recherche"
    )  # Vérifie que le message d'erreur est affiché
