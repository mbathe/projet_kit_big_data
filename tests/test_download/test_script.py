from scripts import (
                    download_dataset_from_kaggle,
                    deplacer_fichiers,
                    download_dataset,
                    )
from unittest.mock import patch, MagicMock
import shutil

import pytest

@pytest.fixture
def temp_directories(tmp_path):
    """Crée des répertoires temporaires pour les tests."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"

    source.mkdir()
    destination.mkdir()

    # Crée des fichiers dans le répertoire source
    for i in range(3):
        (source / f"file_{i}.txt").write_text(f"Content of file {i}")

    return source, destination


@patch("scripts.script.kagglehub.dataset_download")
def test_download_dataset_from_kaggle(mock_dataset_download):
    """Teste la fonction download_dataset_from_kaggle."""
    mock_dataset_download.return_value = "/mock/path/to/dataset"

    path = download_dataset_from_kaggle()

    mock_dataset_download.assert_called_once_with(
        "shuyangli94/food-com-recipes-and-user-interactions")
    assert path == "/mock/path/to/dataset"


def test_deplacer_fichiers(temp_directories):
    """Teste la fonction deplacer_fichiers."""
    source, destination = temp_directories

    # Appelle la fonction pour déplacer les fichiers
    deplacer_fichiers(str(source), str(destination))

    # Vérifie que tous les fichiers ont été déplacés
    for i in range(3):
        assert not (source / f"file_{i}.txt").exists()
        assert (destination / f"file_{i}.txt").exists()


@patch("scripts.script.download_dataset_from_kaggle")
@patch("scripts.script.deplacer_fichiers")
@patch("scripts.script.os.path.exists")
@patch("scripts.script.os.rmdir")
def test_download_dataset(mock_rmdir, mock_exists, mock_deplacer_fichiers, mock_download_dataset_from_kaggle, tmp_path):
    """Teste la fonction download_dataset."""
    mock_exists.return_value = False
    mock_download_dataset_from_kaggle.return_value = str(tmp_path / "kaggle_data")
    mock_deplacer_fichiers.return_value = None

    # Crée le dossier simulé pour le dataset
    (tmp_path / "kaggle_data").mkdir()

    # Appelle la fonction
    download_dataset()

    # Vérifie que download_dataset_from_kaggle a été appelé
    mock_download_dataset_from_kaggle.assert_called_once()

    # Vérifie que deplacer_fichiers a été appelé
    mock_deplacer_fichiers.assert_called_once_with(
        mock_download_dataset_from_kaggle.return_value, "data"
    )

    # Vérifie que le dossier source a été supprimé
    mock_rmdir.assert_called_once_with(mock_download_dataset_from_kaggle.return_value)

    # Teste le cas où le dataset est déjà chargé
    mock_exists.return_value = True
    download_dataset()
    mock_download_dataset_from_kaggle.assert_called_once()  # Pas appelé à nouveau


@patch("scripts.script.os.makedirs")
def test_deplacer_fichiers_cree_dossier_si_non_existant(mock_makedirs, temp_directories):
    """Teste que la fonction deplacer_fichiers crée le dossier destination s'il n'existe pas."""
    source, destination = temp_directories

    # Supprime le dossier de destination
    shutil.rmtree(destination)

    # Appelle la fonction
    deplacer_fichiers(str(source), str(destination))

    # Vérifie que le dossier a été créé
    mock_makedirs.assert_called_once_with(str(destination))