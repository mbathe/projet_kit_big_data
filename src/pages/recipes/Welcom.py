import streamlit as st
import base64
from scripts import MongoDBConnector

class Welcome:
    def __init__(self):
        pass

    @staticmethod
    def get_img_as_base64(file_path):
        """Convertit une image en base64"""
        try:
            with open(file_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception as e:
            st.error(f"Erreur de chargement de l'image : {e}")
            return None

    @staticmethod
    def load_data_from_local(loader, CONNECTION_STRING, start_date, end_date, is_interactional=False):
        if is_interactional:
            st.markdown('<div class="spinner-container">',
                        unsafe_allow_html=True)
            """Chargement des données avec spinner et progression"""
            with st.spinner("⏳ **Chargement des données en cours...**"):
                # Simuler un temps de chargement (ajustez selon vos besoins)
                # Remplacez par votre logique de chargement de données réelle.
                return loader(CONNECTION_STRING, start_date, end_date, is_interactional)
        else:
            st.markdown('<div class="spinner-container">',
                        unsafe_allow_html=True)
            """Chargement des données avec spinner et progression"""
            with st.spinner("⏳ **Chargement des données en cours...**"):
                # Simuler un temps de chargement (ajustez selon vos besoins)
                # Remplacez par votre logique de chargement de données réelle.
                return loader(CONNECTION_STRING, start_date, end_date)


    @staticmethod
    def load_data_from_online(loader, CONNECTION_STRING, DATABASE_NAME, COLLECTION_RECIPES_NAME, start_date, end_date, is_interactional=False, limit=500000):
        """Chargement des données avec spinner et progression"""

        with st.spinner("⏳ **Chargement des données en cours...**"):
            # Simuler un temps de chargement (ajustez selon vos besoins)
            # Remplacez par votre logique de chargement de données réelle.
            if not is_interactional:
                return loader(CONNECTION_STRING, DATABASE_NAME,
                              COLLECTION_RECIPES_NAME, start_date, end_date)
            else:
                print(CONNECTION_STRING)
                connector = MongoDBConnector(CONNECTION_STRING, DATABASE_NAME)
                connector.connect()
                data = connector.load_collection_as_dataframe(
                    COLLECTION_RECIPES_NAME, limit=limit)
                return data

    @staticmethod
    def show_welcom(DEPLOIEMENT_SITE, loader, CONNECTION_STRING, DATABASE_NAME, COLLECTION_RECIPES_NAME, start_date, end_date, is_interactional=None, limit=500000):
        """Méthode principale pour exécuter l'application"""

        # Créez un espace vide pour le contenu initial
        welcome_placeholder = st.empty()

        if is_interactional is None:
            welcome_placeholder.markdown("""
            👨‍🍳 Food.com Recipes Explorer
            🍽️ Analyse Approfondie des Recettes
            ### 📊 Chargement des Données Culinaires
            
            *Votre voyage gastronomique commence...*

            #### 🔍 Ce que vous allez découvrir :
            - 🥗 **Statistiques détaillées des recettes**
            - 📈 Analyses nutritionnelles avancées
            - 🌍 Exploration des tendances culinaires
            - ⭐ Système de recommandation personnalisé
            
            """)
        else:
            welcome_placeholder.markdown("""
            👨‍🍳 Food.com Recipes Explorer
            🍽️ Analyse Approfondie des Nutritions
            ### 📊 Chargement des Données Nutritionnelles
            
            *Votre voyage gastronomique commence...*

            #### 🔍 Ce que vous allez découvrir :
            - 📈 **Statistiques de la popularité des différentes valeurs nutritionnelles**
            - 🌍 **Recette adaptée à son regime**
            
            """)
        data = None
        if DEPLOIEMENT_SITE == "ONLINE":
            data = Welcome.load_data_from_online(
                loader, CONNECTION_STRING, DATABASE_NAME, COLLECTION_RECIPES_NAME, start_date, end_date, is_interactional=is_interactional, limit=limit)
        else:
            data = Welcome.load_data_from_local(
                loader, CONNECTION_STRING, start_date, end_date, is_interactional=is_interactional)
        welcome_placeholder.empty()

        return data
