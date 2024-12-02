import pytest
import pandas as pd
import os
from unittest.mock import patch, mock_open
from io import StringIO
from src.utils.helper_data import load_dataset, load_dataset_from_file


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
    with patch('os.path.basename') as mock_basename, \
            patch('pandas.read_csv') as mock_read_csv:
        mock_basename.return_value = 'test_file.csv'
        mock_read_csv.return_value = pd.DataFrame({'col': [1, 2, 3]})

        result = load_dataset('test_dir/test_file.csv', all_contents=False)

        assert len(result) == 1
        assert 'test_file' in result
        mock_basename.assert_called_once_with('test_dir/test_file.csv')
        mock_read_csv.assert_called_once_with('test_dir/test_file.csv')
        pd.testing.assert_frame_equal(
            result['test_file'], pd.DataFrame({'col': [1, 2, 3]}))


def test_load_dataset_empty_directory():
    with patch('os.listdir') as mock_listdir:
        mock_listdir.return_value = ['file1.txt', 'file2.jpg', 'file3.png']

        result = load_dataset('test_dir', all_contents=True)

        assert len(result) == 0
        assert result == {}
        mock_listdir.assert_called_once_with('test_dir')


def test_load_dataset_different_column_structures():
    with patch('os.listdir') as mock_listdir, \
            patch('pandas.read_csv') as mock_read_csv:
        mock_listdir.return_value = ['file1.csv', 'file2.csv']
        mock_read_csv.side_effect = [
            pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}),
            pd.DataFrame({'col3': [5, 6], 'col4': [7, 8]})
        ]

        result = load_dataset('test_dir', all_contents=True)

        assert len(result) == 2
        assert 'file1' in result
        assert 'file2' in result
        pd.testing.assert_frame_equal(
            result['file1'], pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}))
        pd.testing.assert_frame_equal(
            result['file2'], pd.DataFrame({'col3': [5, 6], 'col4': [7, 8]}))
        mock_listdir.assert_called_once_with('test_dir')
        assert mock_read_csv.call_count == 2
        mock_read_csv.assert_any_call(os.path.join('test_dir', 'file1.csv'))
        mock_read_csv.assert_any_call(os.path.join('test_dir', 'file2.csv'))


def test_load_dataset_from_file_date_parsing():
    mock_data = "id,submitted,title\n1,2023-01-01,Test1\n2,2023-01-15,Test2\n3,2023-02-01,Test3"
    expected_df = pd.DataFrame({
        'id': [1, 2],
        'submitted': pd.to_datetime(['2023-01-01', '2023-01-15']),
        'title': ['Test1', 'Test2']
    })

    with patch('builtins.open', mock_open(read_data=mock_data)):
        with patch('pandas.read_csv', return_value=pd.read_csv(StringIO(mock_data), parse_dates=['submitted'])):
            result = load_dataset_from_file(
                'dummy_path', '2023-01-01', '2023-01-31')

    pd.testing.assert_frame_equal(result, expected_df)
    assert pd.api.types.is_datetime64_any_dtype(result['submitted'])


def test_load_dataset_from_file_invalid_dates():
    mock_data = "id,submitted,title\n1,2023-01-01,Test1\n2,invalid_date,Test2\n3,,Test3"
    expected_df = pd.DataFrame({
        'id': [1],
        'submitted': pd.to_datetime(['2023-01-01']),
        'title': ['Test1']
    })

    with patch('builtins.open', mock_open(read_data=mock_data)):
        with patch('pandas.read_csv', return_value=pd.read_csv(StringIO(mock_data), parse_dates=['submitted'])):
            result = load_dataset_from_file(
                'dummy_path', '2023-01-01', '2023-01-31')

    pd.testing.assert_frame_equal(result, expected_df)
    assert pd.api.types.is_datetime64_any_dtype(result['submitted'])
    assert len(result) == 1  # Only one valid date should remain
