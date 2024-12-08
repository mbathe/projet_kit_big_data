import streamlit as st
import base64
from scripts import MongoDBConnector
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.join(
            os.path.dirname(__file__), '../../..'), "app.log")),
        logging.StreamHandler()
    ]
)


error_handler = logging.FileHandler(os.path.join(os.path.join(
    os.path.dirname(__file__), '../../..'), "error.log"))
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(error_handler)
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
            logging.error(f"Erreur de chargement de l'image : {e}")
            st.error(f"Erreur de chargement de l'image : {e}")
            return None

    @staticmethod
    def load_data_from_local(loader, CONNECTION_STRING, start_date, end_date, is_interactional=False):
        """
        Load data from a local source using the provided loader function.

        Parameters:
        loader (function): A function that takes CONNECTION_STRING, start_date, end_date, and is_interactional as parameters and returns the loaded data.
        CONNECTION_STRING (str): The connection string to connect to the local data source.
        start_date (str): The start date for filtering the data.
        end_date (str): The end date for filtering the data.
        is_interactional (bool, optional): A flag indicating whether the loading process should be interactive. Defaults to False.

        Returns:
        data (any): The loaded data or None if an error occurs.
        """
        try:
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
        except Exception as e:
            logging.error(
                f"Erreur lors du chargement des données locales : {e}")
            st.error(f"Erreur lors du chargement des données locales : {e}")
            return None

    @staticmethod
    def load_data_from_online(loader, CONNECTION_STRING, DATABASE_NAME, COLLECTION_RECIPES_NAME, start_date, end_date, is_interactional=False, limit=500000):
        """
        Load data from an online MongoDB database with a progress spinner.

        This method attempts to load data from a MongoDB database, either using a provided loader function
        or by directly connecting to the database if the interaction is set to be interactive.

        Parameters:
        loader (function): A function to load data when not in interactive mode.
        CONNECTION_STRING (str): The MongoDB connection string.
        DATABASE_NAME (str): The name of the MongoDB database.
        COLLECTION_RECIPES_NAME (str): The name of the collection containing the recipes.
        start_date (str): The start date for filtering the data.
        end_date (str): The end date for filtering the data.
        is_interactional (bool, optional): Whether to use interactive loading. Defaults to False.
        limit (int, optional): The maximum number of documents to retrieve. Defaults to 500000.

        Returns:
        pandas.DataFrame or None: The loaded data as a DataFrame if successful, None otherwise.

        Raises:
        Exception: If there's an error during the data loading process.
        """
        try:
            with st.spinner("⏳ **Chargement des données en cours...**"):
                if not is_interactional:
                    return loader(CONNECTION_STRING, DATABASE_NAME,
                                  COLLECTION_RECIPES_NAME, start_date, end_date)
                else:
                    logging.info(f"Connexion à MongoDB avec CONNECTION_STRING: {
                                 CONNECTION_STRING}")
                    connector = MongoDBConnector(
                        CONNECTION_STRING, DATABASE_NAME)
                    connector.connect()
                    data = connector.load_collection_as_dataframe(
                        COLLECTION_RECIPES_NAME, limit=limit)
                    return data
        except Exception as e:
            logging.error(
                f"Erreur lors du chargement des données en ligne : {e}")
            st.error(f"Erreur lors du chargement des données en ligne : {e}")
            return None

    @staticmethod
    def show_welcom(DEPLOIEMENT_SITE, loader, CONNECTION_STRING, DATABASE_NAME, COLLECTION_RECIPES_NAME, start_date, end_date, is_interactional=None, limit=500000):
        """Méthode principale pour exécuter l'application"""
        try:
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
        except Exception as e:
            logging.error(f"Erreur dans la méthode show_welcom : {e}")
            st.error(f"Erreur dans la méthode show_welcom : {e}")
            return None
