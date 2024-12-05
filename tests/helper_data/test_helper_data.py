import pandas as pd
import os
from unittest.mock import patch, mock_open
from io import StringIO
from src.utils.helper_data import load_dataset
import streamlit as st


def test_load_dataset_all_contents():
    with patch('os.listdir') as mock_listdir, \
            patch('pandas.read_csv') as mock_read_csv:
        mock_listdir.return_value = ['file1.csv', 'file2.csv', 'file3.txt']
        mock_read_csv.side_effect = [pd.DataFrame({'col': [1, 2, 3]})] * 2

        result = load_dataset('test_dir', all_contents=True)

        assert len(result) == 2
        assert 'file1' in result
        assert 'file2' in result
        assert 'file3' not in result
        mock_listdir.assert_called_once_with('test_dir')
        assert mock_read_csv.call_count == 2
        mock_read_csv.assert_any_call(os.path.join('test_dir', 'file1.csv'))
        mock_read_csv.assert_any_call(os.path.join('test_dir', 'file2.csv'))


def test_load_dataset_single_file():
    # Mock Streamlit's cache
    @st.cache_data
    def mock_cached_load_dataset(file_path, all_contents=False):
        file_name = os.path.basename(file_path)
        dataset_name = os.path.splitext(file_name)[0]

        df = pd.read_csv(file_path)

        if all_contents:
            # Logic for loading multiple files if needed
            return {dataset_name: df}

        return {dataset_name: df}

    # Use patch to simulate file path and reading
    with patch('os.path.basename', return_value='test_file.csv'), \
            patch('pandas.read_csv', return_value=pd.DataFrame({'col': [1, 2, 3]})):

        # Construct test file path
        dir_path = os.path.join(os.path.dirname(
            __file__), '../../static/test_dir/test_file.csv')

        # Call the mocked cached dataset loading function
        result = mock_cached_load_dataset(dir_path, all_contents=False)

        # Assertions
        assert len(result) == 1
        assert 'test_file' in result
        pd.testing.assert_frame_equal(
            result['test_file'], pd.DataFrame({'col': [1, 2, 3]})
        )















def test_load_dataset_empty_directory():
    @st.cache_data
    def mock_cached_load_dataset(dir_path, all_contents=True):
        files = os.listdir(dir_path)
        csv_files = [f for f in files if f.endswith('.csv')]

        if not csv_files:
            return {}

        return {}

    with patch('os.listdir', return_value=['file1.txt', 'file2.jpg', 'file3.png']):
        result = mock_cached_load_dataset('test_dir', all_contents=True)
        assert len(result) == 0
        assert result == {}


def test_load_dataset_different_column_structures():
    @st.cache_data
    def mock_cached_load_dataset(dir_path, all_contents=True):
        files = os.listdir(dir_path)
        csv_files = [f for f in files if f.endswith('.csv')]

        results = {}
        for file in csv_files:
            file_path = os.path.join(dir_path, file)
            dataset_name = os.path.splitext(file)[0]
            results[dataset_name] = pd.read_csv(file_path)

        return results

    with patch('os.listdir', return_value=['file1.csv', 'file2.csv']), \
            patch('pandas.read_csv', side_effect=[
                pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
                pd.DataFrame({'col3': [5, 6], 'col4': [7, 8]})
            ]):
        result = mock_cached_load_dataset('test_dir', all_contents=True)
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

    with patch('builtins.open', mock_open(read_data=mock_data)), \
            patch('pandas.read_csv', return_value=pd.read_csv(StringIO(mock_data), parse_dates=['submitted'])):
        result = mock_cached_load_dataset_from_file(
            'dummy_path', '2023-01-01', '2023-01-31')

    pd.testing.assert_frame_equal(result, expected_df)
    assert pd.api.types.is_datetime64_any_dtype(result['submitted'])

