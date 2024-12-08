import pandas as pd
import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.join(
            os.path.dirname(__file__), '../..'), "app.log")),
        logging.StreamHandler()
    ]
)


error_handler = logging.FileHandler(os.path.join(os.path.join(
    os.path.dirname(__file__), '../..'), "error.log"))
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))


logging.getLogger().addHandler(error_handler)


DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE")


class AdvancedRecipeRecommender:
    def __init__(self, recipes_df: pd.DataFrame):
        """
        Initialise le système de recommandation de recettes.

        Args:
            recipes_df (pd.DataFrame): DataFrame contenant les informations des recettes
        """
        try:
            self.recipes_df = recipes_df
            self._preprocess_data()
        except Exception as e:
            logging.error(f"Error in __init__: {e}")
            raise

    def _preprocess_data(self) -> None:
        """
        Effectue un prétraitement avancé des données de recettes.

        Traitements réalisés :
        - Nettoyage et standardisation des ingrédients
        - Création d'une matrice TF-IDF des ingrédients
        - Normalisation des caractéristiques numériques
        """
        try:
            # Nettoie les ingrédients : convertit en chaîne de caractères lowercase
            if DEPLOIEMENT_SITE != "ONLINE":
                self.recipes_df['ingredients_cleaned'] = self.recipes_df['ingredients'].apply(
                    lambda x: ' '.join(eval(x)).lower())
            else:
                self.recipes_df['ingredients_cleaned'] = self.recipes_df['ingredients'].apply(
                    lambda x: ' '.join(x).lower())
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
        except Exception as e:
            logging.error(f"Error in _preprocess_data: {e}")

    def content_based_recommendations(self, recipe_id: int, top_n: int = 5) -> pd.DataFrame:
        """
        Génère des recommandations basées sur la similarité de contenu.

        Args:
            recipe_id (int): Identifiant de la recette de référence
            top_n (int, optional): Nombre de recommandations à retourner. Défaut à 5.

        Returns:
            pd.DataFrame: DataFrame des recettes recommandées
        """
        try:
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
        except Exception as e:
            logging.error(f"Error in content_based_recommendations: {e}")
            raise
            return pd.DataFrame()

    def recipe_clustering(self, n_clusters: int = 5) -> pd.DataFrame:
        """
        Réalise un clustering avancé des recettes.

        Args:
            n_clusters (int, optional): Nombre de clusters. Défaut à 5.

        Returns:
            pd.DataFrame: DataFrame avec les clusters et coordonnées 2D
        """
        try:
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
        except Exception as e:
            logging.error(f"Error in recipe_clustering: {e}")
            return pd.DataFrame()
