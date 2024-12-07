import unittest
from unittest.mock import patch
import pandas as pd
from sklearn.cluster import KMeans
from src.pages.Nutrition import NutritionPage


class TestNutritionPage(unittest.TestCase):

    # Fixture pour créer un DataFrame avec des données nutritionnelles simulées
    def setUp(self):
        self.nutrition_data = pd.DataFrame({
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'Calories': [250, 500, 400],
            'Graisses': [10, 20, 15],
            'Protéines': [5, 10, 8],
            'Glucides': [30, 60, 45],
            'Sucre': [10, 15, 12],
            'Sodium': [50, 100, 75],
            'Graisse_saturées': [3, 5, 4],
            'Moyenne des notes': [4.5, 3.8, 4.2],
            'Nombre de notes': [50, 30, 60],
        })

        self.nutrition_page = NutritionPage(data_directory='./data')
        self.nutrition_page.nutrition_df = self.nutrition_data
        self.nutrition_page.clean_nutrition_df = self.nutrition_data

    # Test de la méthode load_and_clean_data
    @patch.object(NutritionPage, 'load_data')
    @patch.object(NutritionPage, 'clean_data')
    def test_load_and_clean_data(self, mock_clean_data, mock_load_data):
        mock_load_data.return_value = self.nutrition_data
        mock_clean_data.return_value = self.nutrition_data

        self.nutrition_page.load_and_clean_data()

        # Vérification que les données sont chargées et nettoyées
        self.assertIsNotNone(self.nutrition_page.nutrition_df)
        self.assertIsNotNone(self.nutrition_page.clean_nutrition_df)

    # Test de la méthode filter_recipes pour le régime Low-Carb
    def test_filter_recipes_low_carb(self):
        self.nutrition_page.clean_nutrition_df = pd.DataFrame({
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'Glucides': [5, 2, 4],
            'Protéines': [10, 20, 15],
            'Graisses': [5, 10, 7],
        })
        filtered_recipes = self.nutrition_page.filter_recipes('Low-Carb')

        # Vérifier qu'il n'y a qu'une recette qui respecte ce régime
        self.assertEqual(len(filtered_recipes), 1)
        self.assertEqual(filtered_recipes.iloc[0]['name'], 'Recipe 2')

    # Test de la méthode filter_recipes pour le régime High-Protein
    def test_filter_recipes_high_protein(self):
        self.nutrition_page.clean_nutrition_df = pd.DataFrame({
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'Protéines': [50, 10, 5],
            'Graisses': [5, 10, 7],
        })
        filtered_recipes = self.nutrition_page.filter_recipes('High-Protein')

        self.assertEqual(len(filtered_recipes), 1)
        self.assertEqual(filtered_recipes.iloc[0]['name'], 'Recipe 1')

    # Test de la méthode filter_recipes pour le régime Low-Fat
    def test_filter_recipes_low_fat(self):
        self.nutrition_page.clean_nutrition_df = pd.DataFrame({
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'Graisses': [1, 20, 3],
        })
        filtered_recipes = self.nutrition_page.filter_recipes('Low-Fat')

        self.assertEqual(len(filtered_recipes), 2)
        self.assertIn('Recipe 1', filtered_recipes['name'].values)
        self.assertIn('Recipe 3', filtered_recipes['name'].values)

    # Test de la méthode KMeans pour vérifier les clusters
    def test_kmeans_clustering(self):
        features = ['Moyenne des notes', 'Calories', 'Graisses', 'Protéines']
        df_clustering = self.nutrition_page.clean_nutrition_df[features]

        # Appliquer le clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        self.nutrition_page.clean_nutrition_df['Cluster'] = kmeans.fit_predict(
            df_clustering)

        # Vérifier le nombre de clusters
        self.assertEqual(
            len(self.nutrition_page.clean_nutrition_df['Cluster'].unique()), 3)

    # Test de la matrice de corrélation
    def test_correlation_matrix(self):
        # Calculer la matrice de corrélation
        correlation_matrix = self.nutrition_page.clean_nutrition_df[['Moyenne des notes', 'Nombre de notes', 'Calories', 'Graisses',
                                                                     'Protéines', 'Glucides', 'Sucre', 'Sodium']].corr()

        # La matrice doit être de taille 8x8
        self.assertEqual(correlation_matrix.shape, (8, 8))


if __name__ == '__main__':
    unittest.main()
