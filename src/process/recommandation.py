import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

class AdvancedRecipeRecommender:
    def __init__(self, recipes_df: pd.DataFrame):
        """
        Initialise le système de recommandation de recettes.
        
        Args:
            recipes_df (pd.DataFrame): DataFrame contenant les informations des recettes
        """
        self.recipes_df = recipes_df
        self._preprocess_data()

    def _preprocess_data(self) -> None:
        """
        Effectue un prétraitement avancé des données de recettes.
        
        Traitements réalisés :
        - Nettoyage et standardisation des ingrédients
        - Création d'une matrice TF-IDF des ingrédients
        - Normalisation des caractéristiques numériques
        """
        # Nettoie les ingrédients : convertit en chaîne de caractères lowercase
        self.recipes_df['ingredients_cleaned'] = self.recipes_df['ingredients'].apply(
            lambda x: ' '.join(eval(x)).lower()
        )

        # Vectorisation TF-IDF des ingrédients
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.ingredient_matrix = self.tfidf.fit_transform(
            self.recipes_df['ingredients_cleaned']
        )

        # Normalisation des caractéristiques numériques
        numeric_features = ['minutes', 'n_ingredients', 'n_steps']
        scaler = StandardScaler()
        self.numeric_features = scaler.fit_transform(
            self.recipes_df[numeric_features]
        )

    def content_based_recommendations(self, recipe_id: int, top_n: int = 5) -> pd.DataFrame:
        """
        Génère des recommandations basées sur la similarité de contenu.
        
        Args:
            recipe_id (int): Identifiant de la recette de référence
            top_n (int, optional): Nombre de recommandations à retourner. Défaut à 5.
        
        Returns:
            pd.DataFrame: DataFrame des recettes recommandées
        """
        # Trouve l'index de la recette de référence
        recipe_index = self.recipes_df[self.recipes_df['id']
                                       == recipe_id].index[0]

        # Calcule la similarité cosinus entre la recette et toutes les autres
        cosine_sim = cosine_similarity(
            self.ingredient_matrix[recipe_index],
            self.ingredient_matrix
        ).flatten()

        # Récupère les indices des top_n recettes les plus similaires
        similar_indices = cosine_sim.argsort()[::-1][1:top_n+1]
        return self.recipes_df.iloc[similar_indices]

    def recipe_clustering(self, n_clusters: int = 5) -> pd.DataFrame:
        """
        Réalise un clustering avancé des recettes.
        
        Args:
            n_clusters (int, optional): Nombre de clusters. Défaut à 5.
        
        Returns:
            pd.DataFrame: DataFrame avec les clusters et coordonnées 2D
        """
        # Combine les features de la matrice d'ingrédients et des caractéristiques numériques
        combined_features = np.hstack([
            self.ingredient_matrix.toarray(),
            self.numeric_features
        ])

        # Réduction de dimensionnalité avec PCA
        pca = PCA(n_components=2)
        features_2d = pca.fit_transform(combined_features)

        # Clustering K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(combined_features)

        # Création d'un DataFrame de résultats
        cluster_df = pd.DataFrame({
            'Recipe': self.recipes_df['name'],
            'Cluster': clusters,
            'X': features_2d[:, 0],
            'Y': features_2d[:, 1]
        })

        return cluster_df
