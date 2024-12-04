import os
from src.pages.recipes.recommandation import recommandation_page
from unittest.mock import MagicMock, patch
import streamlit as st
import pytest
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from src.process.recommandation import AdvancedRecipeRecommender

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from src.process.recommandation import AdvancedRecipeRecommender


sample_data = {
    'id': [1, 2, 3],
    'name': ['Recipe1', 'Recipe2', 'Recipe3'],
    'ingredients': ["['salt', 'pepper', 'chicken']", "['salt', 'pepper', 'beef']", "['salt', 'pepper', 'fish']"],
    'minutes': [30, 45, 60],
    'n_ingredients': [3, 3, 3],
    'n_steps': [5, 6, 7]
}


def create_sample_recipes_df():
    """Helper function to create a sample DataFrame for testing"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Pasta', 'Pizza', 'Salad', 'Burger', 'Soup'],
        'ingredients': [
            "['tomato', 'pasta', 'cheese']",
            "['cheese', 'tomato', 'dough']",
            "['lettuce', 'cucumber', 'tomato']",
            "['beef', 'bun', 'lettuce']",
            "['carrot', 'onion', 'potato']"
        ],
        'minutes': [20, 30, 15, 25, 40],
        'n_ingredients': [3, 3, 3, 3, 3],
        'n_steps': [4, 5, 3, 4, 5]
    })


@pytest.fixture
def sample_recipes_df_2():
    """
    Fixture pour créer un DataFrame de recettes de test
    """
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Pizza Margherita', 'Salade César', 'Poulet Rôti', 'Lasagne', 'Sushi'],
        'minutes': [30, 15, 60, 45, 20],
        'n_ingredients': [4, 5, 6, 7, 8],
        'n_steps': [5, 3, 7, 6, 4],
        'ingredients': [
            str(['farine', 'tomate', 'mozzarella', 'basilic']),
            str(['laitue', 'poulet', 'croûtons', 'parmesan', 'sauce']),
            str(['poulet', 'herbes', 'sel', 'poivre', 'huile', 'ail']),
            str(['pâtes', 'sauce tomate', 'bœuf',
                'fromage', 'oignon', 'ail', 'basilic']),
            str(['riz', 'poisson', 'algue', 'wasabi',
                'gingembre', 'sauce soja', 'vinaigre', 'sel'])
        ]
    })


@pytest.fixture
def recommender():
    """Fixture to create a recommender instance for each test"""
    return AdvancedRecipeRecommender(create_sample_recipes_df())


def test_initialization(recommender):
    """Test recommender initialization"""
    assert not recommender.recipes_df.empty
    assert 'ingredients_cleaned' in recommender.recipes_df.columns


def test_preprocess_data(recommender):
    """Test data preprocessing steps"""
    # Check TF-IDF matrix creation
    assert hasattr(recommender, 'ingredient_matrix')
    assert recommender.ingredient_matrix.shape[0] == len(
        recommender.recipes_df)

    # Check numeric feature scaling
    assert hasattr(recommender, 'numeric_features')
    assert recommender.numeric_features.shape[0] == len(recommender.recipes_df)


def test_content_based_recommendations(recommender):
    """Test content-based recommendations"""
    # Recommend for first recipe
    recommendations = recommender.content_based_recommendations(1, top_n=3)

    assert len(recommendations) == 3
    assert isinstance(recommendations, pd.DataFrame)

    # Check recommendations are different from original recipe
    original_recipe = recommender.recipes_df[recommender.recipes_df['id'] == 1]
    assert not recommendations.equals(original_recipe)


def test_recipe_clustering(recommender):
    """Test recipe clustering"""
    cluster_df = recommender.recipe_clustering(n_clusters=3)

    # Verify cluster DataFrame structure
    assert 'Recipe' in cluster_df.columns
    assert 'Cluster' in cluster_df.columns
    assert 'X' in cluster_df.columns
    assert 'Y' in cluster_df.columns

    # Check clustering results
    assert len(cluster_df) == len(recommender.recipes_df)
    assert cluster_df['Cluster'].nunique() == 3


def test_ingredient_cleaning(recommender):
    """Test ingredient cleaning process"""
    # Verify ingredients are cleaned and lowercased
    cleaned_ingredients = recommender.recipes_df['ingredients_cleaned']

    assert all(isinstance(ing, str) for ing in cleaned_ingredients)
    assert all(ing.islower() for ing in cleaned_ingredients)


def test_tfidf_vectorization(recommender):
    """Test TF-IDF vectorization"""
    # Verify TF-IDF vectorizer attributes
    assert isinstance(recommender.tfidf, TfidfVectorizer)

    # Check vectorization results
    tfidf_matrix = recommender.ingredient_matrix
    assert tfidf_matrix.shape[0] == len(recommender.recipes_df)
    assert tfidf_matrix.shape[1] > 0


@pytest.fixture
def recommender_instance():
    df = pd.DataFrame(sample_data)
    recommender = AdvancedRecipeRecommender(df)
    return recommender


def test_preprocess_data_2(recommender_instance):
    recommender_instance._preprocess_data()
    assert 'ingredients_cleaned' in recommender_instance.recipes_df.columns
    assert isinstance(recommender_instance.tfidf, TfidfVectorizer)


def test_content_based_recommendations_2(recommender_instance):
    recommendations = recommender_instance.content_based_recommendations(
        recipe_id=1, top_n=2)
    assert len(recommendations) == 2
    assert 'id' in recommendations.columns


def test_recipe_clustering_2(recommender_instance):
    cluster_df = recommender_instance.recipe_clustering(n_clusters=2)
    assert 'Recipe' in cluster_df.columns
    assert 'Cluster' in cluster_df.columns
    assert 'X' in cluster_df.columns
    assert 'Y' in cluster_df.columns
    assert len(cluster_df['Cluster'].unique()) == 2


def test_recommender_initialization(sample_recipes_df_2):
    """
    Test l'initialisation du recommandeur
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    assert hasattr(recommender, 'recipes_df')
    assert hasattr(recommender, 'ingredient_matrix')
    assert hasattr(recommender, 'numeric_features')

    # Vérifier le prétraitement
    assert recommender.ingredient_matrix is not None
    assert recommender.recipes_df['ingredients_cleaned'].iloc[0] is not None


def test_preprocess_data_exemple_2(sample_recipes_df_2):
    """
    Test le prétraitement des données
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    # Vérifier les ingrédients nettoyés
    assert recommender.recipes_df['ingredients_cleaned'].iloc[0] == 'farine tomate mozzarella basilic'

    # Vérifier la matrice TF-IDF
    assert recommender.ingredient_matrix.shape[0] == len(sample_recipes_df_2)


def test_content_based_recommendations_exemple_2(sample_recipes_df_2):
    """
    Test les recommandations basées sur le contenu
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    # Tester les recommandations pour la première recette
    recommendations = recommender.content_based_recommendations(
        recipe_id=1, top_n=2)

    assert len(recommendations) == 2
    assert all(rec_id != 1 for rec_id in recommendations['id'])


def test_content_based_recommendations_error_handling(sample_recipes_df_2):
    """
    Test la gestion des erreurs pour les recommandations
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    # Tester avec un ID de recette invalide
    with pytest.raises(IndexError):
        recommender.content_based_recommendations(recipe_id=999, top_n=2)


def test_recipe_clustering_exemple_2(sample_recipes_df_2):
    """
    Test le clustering des recettes
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    # Tester le clustering avec différents nombres de clusters
    cluster_df_5 = recommender.recipe_clustering(n_clusters=5)
    cluster_df_3 = recommender.recipe_clustering(n_clusters=3)

    assert len(cluster_df_5) == len(sample_recipes_df_2)
    assert len(cluster_df_3) == len(sample_recipes_df_2)

    # Vérifier les colonnes du DataFrame de clustering
    assert set(cluster_df_5.columns) == {'Recipe', 'Cluster', 'X', 'Y'}

    # Vérifier la distribution des clusters
    unique_clusters_5 = cluster_df_5['Cluster'].nunique()
    unique_clusters_3 = cluster_df_3['Cluster'].nunique()

    assert unique_clusters_5 == 5
    assert unique_clusters_3 == 3


def test_numeric_feature_scaling_exemple2(sample_recipes_df_2):
    """
    Test la mise à l'échelle des features numériques
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    # Vérifier que les features numériques sont bien standardisées
    # minutes, n_ingredients, n_steps
    assert recommender.numeric_features.shape[1] == 3

    # Vérifier que la moyenne est proche de 0 et l'écart-type proche de 1
    assert np.allclose(recommender.numeric_features.mean(axis=0), 0, atol=1e-7)
    assert np.allclose(recommender.numeric_features.std(axis=0), 1, atol=1e-7)


def test_tfidf_vectorization_exemple2(sample_recipes_df_2):
    """
    Test la vectorisation TF-IDF des ingrédients
    """
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_2)

    # Vérifier que la matrice TF-IDF est bien formée
    assert recommender.ingredient_matrix is not None
    assert recommender.ingredient_matrix.shape[0] == len(sample_recipes_df_2)

    # Vérifier que tous les ingrédients sont vectorisés
    for ingredients in sample_recipes_df_2['ingredients_cleaned']:
        assert len(recommender.tfidf.transform([ingredients]).toarray()[0]) > 0


# Fixture pour créer un DataFrame de recettes de test


@pytest.fixture
def sample_recipes_df_3():
    dir_path = os.path.join(os.path.dirname(
        __file__), '../../static/test_dir/recipe_exemple.csv')
    return pd.read_csv(dir_path)

# Test pour vérifier la création du recommandeur


def test_recommandation_page_recommender_creation(sample_recipes_df_3):
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_3)
    assert isinstance(recommender, AdvancedRecipeRecommender)
    assert len(recommender.recipes_df) == 5

# Test de la page Streamlit avec simulation


def test_content_based_recommendations_exemple(sample_recipes_df_3):
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_3)

    # Test avec la première recette
    recommendations = recommender.content_based_recommendations(
        137739, top_n=2)

    assert len(recommendations) == 2

# Test de gestion des erreurs


def test_recommandation_page_error_handling():
    # Simulation d'un DataFrame vide
    empty_df = pd.DataFrame(
        columns=['id', 'name', 'minutes', 'n_steps', 'ingredients'])

    with pytest.raises(ValueError):
        AdvancedRecipeRecommender(recipes_df=empty_df)

# Test de la sélection de recette


def test_recipe_selection(sample_recipes_df_3):
    recommender = AdvancedRecipeRecommender(recipes_df=sample_recipes_df_3)

    # Vérifier que les ID de recette sont correctement extraits
    recipe_ids = recommender.recipes_df['id'].tolist()

    assert recipe_ids == [137739, 31490, 112140, 59389, 44061]


# Exécution des tests
# Exécution des tests
if __name__ == '__main__':
    pytest.main([__file__])
