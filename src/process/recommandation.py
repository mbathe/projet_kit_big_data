import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class AdvancedRecipeRecommender:
    def __init__(self, recipes_df):
        """
        Initialise le système de recommandation avec sophistication
        """
        # Chargement des données
        self.recipes_df = recipes_df
        # self.interactions_df = pd.read_csv(interactions_path)

        # Prétraitement
        self._preprocess_data()

    def _preprocess_data(self):
        """
        Prétraitement avancé des données
        """
        # Nettoyer et préparer les ingrédients
        self.recipes_df['ingredients_cleaned'] = self.recipes_df['ingredients'].apply(
            lambda x: ' '.join(eval(x)).lower()
        )

        # Vectorisation TF-IDF des ingrédients
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.ingredient_matrix = self.tfidf.fit_transform(
            self.recipes_df['ingredients_cleaned']
        )

        # Scalisation des features numériques
        numeric_features = ['minutes', 'n_ingredients', 'n_steps']
        scaler = StandardScaler()
        self.numeric_features = scaler.fit_transform(
            self.recipes_df[numeric_features]
        )

    def content_based_recommendations(self, recipe_id, top_n=5):
        """
        Recommandations basées sur la similarité de contenu
        """
        recipe_index = self.recipes_df[self.recipes_df['id']
                                       == recipe_id].index[0]

        # Calcul de similarité cosinus
        cosine_sim = cosine_similarity(
            self.ingredient_matrix[recipe_index],
            self.ingredient_matrix
        ).flatten()

        # Top N recommandations
        similar_indices = cosine_sim.argsort()[::-1][1:top_n+1]
        return self.recipes_df.iloc[similar_indices]

    def recipe_clustering(self, n_clusters=5):
        """
        Clustering avancé des recettes
        """
        # Combinaison des features
        combined_features = np.hstack([
            self.ingredient_matrix.toarray(),
            self.numeric_features
        ])

        # Réduction de dimensionnalité
        pca = PCA(n_components=2)
        features_2d = pca.fit_transform(combined_features)

        # Clustering K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(combined_features)

        # Préparation pour visualisation
        cluster_df = pd.DataFrame({
            'Recipe': self.recipes_df['name'],
            'Cluster': clusters,
            'X': features_2d[:, 0],
            'Y': features_2d[:, 1]
        })

        return cluster_df
