import pandas as pd
import os
from unittest.mock import patch, MagicMock
from io import StringIO
import importlib
from src.utils.helper_data import load_dataset
import streamlit as st
# 1. Désactiver le décorateur `@st.cache_data` avant d'importer les fonctions à tester
with patch('streamlit.cache_data', lambda func: func):
    # Importer le module après avoir patché `st.cache_data`
    import src.utils.helper_data
    importlib.reload(src.utils.helper_data)  # Recharger le module pour appliquer le patch
    from src.utils.helper_data import load_dataset, load_dataset_from_file


def test_load_dataset_all_contents():
    with patch('os.listdir') as mock_listdir, \
            patch('pandas.read_csv') as mock_read_csv:
        # Simuler la liste des fichiers dans le répertoire
        mock_listdir.return_value = ['file1.csv', 'file2.csv', 'file3.txt']
        # Simuler les DataFrames retournés par pandas.read_csv
        mock_read_csv.side_effect = [pd.DataFrame({'col': [1, 2, 3]})] * 2

        # Appel de la fonction à tester
        result = load_dataset('test_dir', all_contents=True)

        # Assertions
        assert len(result) == 2
        assert 'file1' in result
        assert 'file2' in result
        assert 'file3' not in result  # Non inclus car ce n'est pas un fichier CSV
        mock_listdir.assert_called_once_with('test_dir')
        assert mock_read_csv.call_count == 2
        mock_read_csv.assert_any_call(os.path.join('test_dir', 'file1.csv'))
        mock_read_csv.assert_any_call(os.path.join('test_dir', 'file2.csv'))


def test_load_dataset_single_file():
    with patch('os.path.basename') as mock_basename, \
            patch('pandas.read_csv') as mock_read_csv:
        # Simuler le nom de base du fichier
        mock_basename.return_value = 'test_file.csv'
        # Simuler le DataFrame retourné par pandas.read_csv
        mock_read_csv.return_value = pd.DataFrame({'col': [1, 2, 3]})

        # Appel de la fonction à tester
        result = load_dataset('test_dir/test_file.csv', all_contents=False)

        # Assertions
        assert len(result) == 1
        assert 'test_file' in result
        pd.testing.assert_frame_equal(
            result['test_file'], pd.DataFrame({'col': [1, 2, 3]})
        )















def test_load_dataset_empty_directory():
    with patch('os.listdir') as mock_listdir:
        # Simuler un répertoire sans fichiers CSV
        mock_listdir.return_value = ['file1.txt', 'file2.jpg', 'file3.png']

        # Appel de la fonction à tester
        result = load_dataset('test_dir', all_contents=True)

        # Assertions
        assert len(result) == 0
        assert result == {}


def test_load_dataset_different_column_structures():
    with patch('os.listdir') as mock_listdir, \
            patch('pandas.read_csv') as mock_read_csv:
        # Simuler la liste des fichiers CSV dans le répertoire
        mock_listdir.return_value = ['file1.csv', 'file2.csv']
        # Simuler des DataFrames avec différentes structures de colonnes
        mock_read_csv.side_effect = [
            pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            pd.DataFrame({'col3': [5, 6], 'col4': [7, 8]})
        ]

        # Appel de la fonction à tester
        result = load_dataset('test_dir', all_contents=True)

        # Assertions
        assert len(result) == 2
        assert 'file1' in result
        assert 'file2' in result
        pd.testing.assert_frame_equal(
            result['file1'], pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}))
        pd.testing.assert_frame_equal(
            result['file2'], pd.DataFrame({'col3': [5, 6], 'col4': [7, 8]}))

def test_load_dataset_from_file_date_parsing():
    @st.cache_data
    def mock_cached_load_dataset_from_file(file_path, start_date, end_date):
        df = pd.read_csv(file_path, parse_dates=['submitted'])
        filtered_df = df[
            (pd.to_datetime(df['submitted']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(df['submitted']) <= pd.to_datetime(end_date))
        ]
        return filtered_df

    mock_data = "id,submitted,title\n1,2023-01-01,Test1\n2,2023-01-15,Test2\n3,2023-02-01,Test3"
    expected_df = pd.DataFrame({
        'id': [1, 2],
        'submitted': pd.to_datetime(['2023-01-01', '2023-01-15']),
        'title': ['Test1', 'Test2']
    })

    # Créer un DataFrame pour simuler chaque chunk
    chunk_df = pd.read_csv(StringIO(mock_data), parse_dates=['submitted'])

    # Simuler que pandas.read_csv retourne un itérateur de DataFrames
    with patch('pandas.read_csv', return_value=iter([chunk_df])):
        # Appel de la fonction à tester
        result = load_dataset_from_file(
            'dummy_path', '2023-01-01', '2023-01-31'
        )

    # Assertions
    pd.testing.assert_frame_equal(result, expected_df)
    assert pd.api.types.is_datetime64_any_dtype(result['submitted'])
    assert len(result) == 2  # Deux dates valides


def test_load_dataset_from_file_invalid_dates():
    expected_df = pd.DataFrame({
        'id': [1],
        'submitted': [pd.Timestamp('2023-01-01')],
        'title': ['Test1']
    })

    # Créer un DataFrame avec 'submitted' comme datetime64[ns], avec NaT
    chunk_df = pd.DataFrame({
        'id': [1, 2, 3],
        'submitted': [pd.Timestamp('2023-01-01'), pd.NaT, pd.NaT],
        'title': ['Test1', 'Test2', 'Test3']
    })

    # Mock read_csv pour retourner un itérateur de chunk_df
    with patch('pandas.read_csv', return_value=iter([chunk_df])):
        # Appel de la fonction à tester
        result = load_dataset_from_file(
            'dummy_path', '2023-01-01', '2023-01-31'
        )

    # Assertions
    pd.testing.assert_frame_equal(result, expected_df)
    assert pd.api.types.is_datetime64_any_dtype(result['submitted'])
    assert len(result) == 1  # Une seule date valide
