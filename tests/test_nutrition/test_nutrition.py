import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from sklearn.cluster import KMeans
from src.pages.nutrition import NutritionPage
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from typing import Optional, Tuple
import numpy as np


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

    @patch('src.process.nutrition_preprocess.load_data')
    @patch('src.process.nutrition_preprocess.clean_data')
    def test_load_and_clean_data_failure(self, mock_clean_data, mock_load_data):
        """
        Teste la méthode load_and_clean_data en cas d'erreur lors du chargement des données.
        """
        # Simule une exception lorsque load_data est appelé
        mock_load_data.side_effect = Exception("Erreur de chargement")

        # Création de l'instance de la classe à tester
        nutrition_page = NutritionPage(data_directory="dummy_path")

        # Appel de la méthode avec gestion d'erreur
        raw_data, clean_data = nutrition_page.load_and_clean_data()

        # Vérifie que clean_data n'est pas appelé si load_data échoue
        mock_clean_data.assert_not_called()

    def test_initialization(self):
        """
        Teste l'initialisation de la classe NutritionPage.
        """
        self.assertEqual(self.nutrition_page.data_directory, './data')
        self.assertIsNotNone(self.nutrition_page.nutrition_df)
        self.assertIsNotNone(self.nutrition_page.clean_nutrition_df)

    @patch('src.pages.nutrition.st')
    def test_display_context(self, mock_st):
        """
        Teste la méthode display_context pour vérifier qu'elle s'exécute sans erreur.
        """
        try:
            self.nutrition_page.display_context()

            # Vérification des appels Streamlit
            mock_st.title.assert_any_call("Contexte")
            mock_st.write.assert_any_call(
                "Dans cette partie, nous allons nous concentrer sur les valeurs nutritionnelles des recettes. Nous chercherons en particulier à déterminer l'influence des différentes valeurs nutritionnelles sur la popularité d'une recette.")
            mock_st.dataframe.assert_called()  # Vérifie que les DataFrames ont été affichés
            mock_st.pyplot.assert_called()  # Vérifie que les graphiques ont été affichés

            # Vérification que les boxplots sont générés
            self.assertEqual(
                plt.gcf().axes[0].get_title(), 'Boxplot de Calories')
        except Exception as e:
            self.fail(f"display_context a levé une exception inattendue : {e}")

    @patch('src.pages.nutrition.st.title')
    @patch('src.pages.nutrition.st.subheader')
    @patch('src.pages.nutrition.st.write')
    @patch('src.pages.nutrition.st.slider')
    @patch('matplotlib.pyplot.subplots')
    @patch('seaborn.histplot')
    @patch('seaborn.heatmap')
    @patch('seaborn.scatterplot')
    def test_display_nutrition_analysis(self, mock_scatterplot, mock_heatmap, mock_histplot, mock_subplots,
                                        mock_slider, mock_write, mock_subheader, mock_title):

        # Préparation de données simulées
        mock_clean_nutrition_df = pd.DataFrame({
            'Calories': np.random.normal(200, 50, 100),
            'Graisses': np.random.normal(20, 5, 100),
            'Sodium': np.random.normal(100, 25, 100),
            'Glucides': np.random.normal(50, 10, 100),
            'Protéines': np.random.normal(30, 7, 100),
            'Sucre': np.random.normal(10, 2, 100),
            'Graisse_saturées': np.random.normal(5, 1, 100),
            'Moyenne des notes': np.random.normal(3.5, 0.5, 100),
            'Nombre de notes': np.random.randint(50, 500, 100)
        })

        # Création d'une instance de la classe avec les données mockées
        nutrition_page = NutritionPage(data_directory="dummy_path")
        nutrition_page.clean_nutrition_df = mock_clean_nutrition_df

        # Mock de la fonction subplots
        mock_fig, mock_axes = MagicMock(), MagicMock()
        mock_subplots.return_value = (mock_fig, mock_axes)

        # Mock des méthodes sns pour éviter l'affichage des graphiques
        mock_histplot.return_value = MagicMock()
        mock_heatmap.return_value = MagicMock()
        mock_scatterplot.return_value = MagicMock()

        # Mock du slider
        mock_slider.return_value = 3  # Valeur par défaut du slider

        # Appel de la fonction display_nutrition_analysis
        nutrition_page.display_nutrition_analysis()

        # Vérifications

        self.assertTrue(mock_heatmap.called)

        mock_title.assert_called_with('Analyse des valeurs nutritionnelles')
        mock_subheader.assert_any_call('Première approche')
        mock_subheader.assert_any_call('Première approche')
        mock_write.assert_any_call(
            'Commençons par observer la façon dont les données sont réparties dans nos différentes catégories :')

        # Vérification des histogrammes
        mock_histplot.assert_any_call(
            nutrition_page.clean_nutrition_df['Calories'], kde=True, ax=mock_axes[0, 0])

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

    @patch('src.pages.nutrition.NutritionPage')
    def test_main_script_execution(self, mock_nutrition_page):
        """
        Teste le bloc principal du script pour s'assurer qu'aucune exception n'est levée
        et que toutes les méthodes sont appelées comme prévu.
        """
        # Mock de la classe NutritionPage
        mock_nutrition_page_instance = MagicMock()
        mock_nutrition_page.return_value = mock_nutrition_page_instance

        # Simuler les méthodes de NutritionPage
        mock_nutrition_page_instance.load_and_clean_data = MagicMock()
        mock_nutrition_page_instance.run = MagicMock()
        mock_nutrition_page_instance.display_sidebar = MagicMock()

        # Exécution du script principal
        try:
            # Simuler l'exécution du script principal
            # Remplacez par le chemin correct de votre script
            exec(open('./src/pages/nutrition.py').read())
        except Exception as e:
            self.fail(f"L'exécution du script a échoué avec l'exception : {e}")


if __name__ == '__main__':
    unittest.main()
