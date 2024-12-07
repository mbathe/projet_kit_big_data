import pytest
import streamlit as st
import base64
from unittest.mock import mock_open, patch, MagicMock
# Remplacez par le module où se trouve la classe Welcome
from src.pages.recipes.Welcom import Welcome


def test_get_img_as_base64_success():
    """Test de la méthode get_img_as_base64 avec un chargement d'image réussi"""
    mock_file_content = b'test image content'
    with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
        result = Welcome.get_img_as_base64('test_image.png')
        assert result == base64.b64encode(mock_file_content).decode()
        mock_file.assert_called_once_with('test_image.png', 'rb')


def test_get_img_as_base64_file_not_found():
    """Test de la méthode get_img_as_base64 avec un fichier inexistant"""
    with patch("streamlit.error") as mock_error, \
            patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        result = Welcome.get_img_as_base64('nonexistent_image.png')
        assert result is None
        mock_error.assert_called_once()


def test_load_data_from_local():
    """Test de la méthode load_data_from_local"""
    mock_loader = MagicMock(return_value=['data1', 'data2'])
    connection_string = 'test_connection'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    with patch('streamlit.spinner', return_value=MagicMock()), \
            patch('streamlit.markdown'):
        result = Welcome.load_data_from_local(
            mock_loader, connection_string, start_date, end_date)

        mock_loader.assert_called_once_with(
            connection_string, start_date, end_date)
        assert result == ['data1', 'data2']


def test_load_data_from_online():
    """Test de la méthode load_data_from_online"""
    mock_loader = MagicMock(return_value=['data1', 'data2'])
    connection_string = 'test_connection'
    database_name = 'test_db'
    collection_name = 'test_collection'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    with patch('streamlit.spinner', return_value=MagicMock()):
        result = Welcome.load_data_from_online(
            mock_loader, connection_string, database_name,
            collection_name, start_date, end_date
        )

        mock_loader.assert_called_once_with(
            connection_string, database_name, collection_name, start_date, end_date
        )
        assert result == ['data1', 'data2']


def test_show_welcom_local_deployment():
    """Test de la méthode show_welcom pour un déploiement local"""
    mock_loader = MagicMock(return_value=['local_data1', 'local_data2'])
    connection_string = 'local_connection'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    with patch('streamlit.empty', return_value=MagicMock()) as mock_empty, \
            patch('streamlit.markdown'), \
            patch('streamlit.spinner', return_value=MagicMock()):

        result = Welcome.show_welcom(
            "LOCAL", mock_loader, connection_string,
            'db_name', 'collection_name', start_date, end_date
        )

        mock_loader.assert_called_once_with(
            connection_string, start_date, end_date)
        assert result == ['local_data1', 'local_data2']
        mock_empty.return_value.empty.assert_called_once()


def test_show_welcom_online_deployment():
    """Test de la méthode show_welcom pour un déploiement en ligne"""
    mock_loader = MagicMock(return_value=['online_data1', 'online_data2'])
    connection_string = 'online_connection'
    database_name = 'online_db'
    collection_name = 'online_collection'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    with patch('streamlit.empty', return_value=MagicMock()) as mock_empty, \
            patch('streamlit.markdown'), \
            patch('streamlit.spinner', return_value=MagicMock()):

        result = Welcome.show_welcom(
            "ONLINE", mock_loader, connection_string,
            database_name, collection_name, start_date, end_date
        )

        mock_loader.assert_called_once_with(
            connection_string, database_name, collection_name, start_date, end_date
        )
        assert result == ['online_data1', 'online_data2']
        mock_empty.return_value.empty.assert_called_once()


# Configuration des tests
if __name__ == "__main__":
    pytest.main([__file__])
