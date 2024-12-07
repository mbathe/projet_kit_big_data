import os
import pytest
import tempfile
import shutil
import kagglehub
import gdown
import zipfile
import logging
from unittest.mock import patch, MagicMock

from scripts.download_dataset import (
    download_dataset_from_drive
)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_download_dataset_from_drive_success(temp_directory):
    """Test successful download and extraction from Google Drive."""
    file_id = "test_file_id"
    with patch('gdown.download') as mock_download, \
            patch('zipfile.ZipFile') as mock_zipfile:

        mock_download.return_value = os.path.join(
            temp_directory, 'dataset.zip')
        result = download_dataset_from_drive(file_id, temp_directory)

        assert result is None
        mock_download.assert_called_once()
        mock_zipfile.assert_called_once()


def test_download_dataset_from_drive_download_failure(temp_directory):
    """Test download failure scenario."""
    file_id = "invalid_file_id"
    with patch('gdown.download', side_effect=Exception("Download error")):
        result = download_dataset_from_drive(file_id, temp_directory)
        assert result is None


if __name__ == '__main__':
    pytest.main()
