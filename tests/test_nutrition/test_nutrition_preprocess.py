import unittest
from unittest.mock import patch
import pandas as pd
from src.process.nutrition_preprocess import load_data, clean_data


class TestDataProcessing(unittest.TestCase):

    @patch('pandas.read_csv')
    def test_load_data_file_error(self, mock_read_csv):
        # Simuler une erreur de fichier non trouvé
        mock_read_csv.side_effect = Exception("Fichier introuvable")

        # Appel de la fonction et vérification de l'exception levée
        with self.assertRaises(Exception):
            load_data()

    def test_clean_data_success(self):
        # Données d'exemple pour tester clean_data
        data = {
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'Nombre de notes': [10, 4, 15],
            'Calories': [250, 850, 500],
            'Graisses': [30, 120, 45],
            'Graisse_saturées': [5, 10, 6],
            'Sucre': [20, 80, 25],
            'Sodium': [50, 200, 60],
            'Protéines': [20, 30, 25],
            'Glucides': [40, 30, 60]
        }
        df = pd.DataFrame(data)

        # Appliquer la fonction de nettoyage
        cleaned_df = clean_data(df)

        # Vérifier que les lignes avec moins de 5 notes ont été supprimées
        # Recipe2 avec moins de 5 notes doit être supprimé
        self.assertEqual(len(cleaned_df), 2)
        self.assertTrue(all(cleaned_df['Calories'] <= 800))
        self.assertTrue(all(cleaned_df['Graisses'] <= 100))

    def test_clean_data_with_outliers(self):
        # Données d'exemple contenant des valeurs aberrantes
        data = {
            'name': ['Recipe1', 'Recipe2'],
            'Nombre de notes': [10, 6],
            'Calories': [250, 850],
            'Graisses': [30, 200],  # Valeur aberrante pour Graisses
            'Graisse_saturées': [5, 10],
            'Sucre': [20, 80],
            'Sodium': [50, 200],
            'Protéines': [20, 30],
            'Glucides': [40, 30]
        }
        df = pd.DataFrame(data)

        # Appliquer la fonction de nettoyage
        cleaned_df = clean_data(df)

        # Vérifier que la ligne avec Graisses > 100 a été supprimée
        self.assertEqual(len(cleaned_df), 1)  # Recipe2 doit être supprimé
        self.assertTrue(all(cleaned_df['Graisses'] <= 100))


if __name__ == '__main__':
    unittest.main()
