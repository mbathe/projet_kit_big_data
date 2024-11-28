import pandas as pd
import pytest
from src.pages.analyse_user import DataLoader

def test_load_large_csv(tmp_path):
    # Prépare un fichier CSV temporaire
    data = "col1,col2\n1,2\n3,4"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(data)
    
    # Charge les données
    loaded_data = DataLoader.load_large_csv(csv_file)
    
    # Vérifie que le DataFrame est correctement chargé
    expected_data = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
    pd.testing.assert_frame_equal(loaded_data, expected_data)
