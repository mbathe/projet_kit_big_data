import pytest
from unittest.mock import patch, MagicMock
import os
import shutil
from scripts.script import download_dataset, deplacer_fichiers


@patch('src.utils.kagglehub.dataset_download')
@patch('builtins.print')
def test_download_dataset(mock_print, mock_dataset_download):
    """Test de la fonction download_dataset."""
    # Configurer le mock pour dataset_download
    mock_dataset_download.return_value = "/chemin/vers/dataset"

    # Appeler la fonction
    path = download_dataset()

    # Vérifier que kagglehub.dataset_download a été appelé avec le bon argument
    mock_dataset_download.assert_called_once_with("shuyangli94/food-com-recipes-and-user-interactions")

    # Vérifier que la fonction retourne le bon chemin
    assert path == "/chemin/vers/dataset", "Le chemin retourné n'est pas celui attendu."

    # Vérifier que les messages ont été imprimés
    mock_print.assert_any_call("Downloading dataset...")
    mock_print.assert_any_call("Path to dataset files:", "/chemin/vers/dataset")

