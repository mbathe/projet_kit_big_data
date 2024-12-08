"""
Page de l'application Streamlit pour l'analyse des données d'interactions utilisateurs.

Ce module configure le logging, charge les données depuis des sources variées (CSV, MongoDB),
analyse les données, et génère des visualisations interactives à l'aide de Streamlit.

Modules et Classes Principaux :
- setup_logging: Configure le système de logging de l'application.
- DataLoader: Classe pour charger des données à partir de fichiers CSV.
- DataLoaderMango: Classe pour charger des données depuis une base de données MongoDB.
- CSSLoader: Classe pour charger des feuilles de style CSS.
- DataAnalyzer: Classe pour analyser et prétraiter les données.
- VisualizationManager: Classe pour gérer les visualisations des données.
- StreamlitPage: Classe principale pour l'intégration avec Streamlit.
- main: Point d'entrée de l'application.

Dépendances :
- src.visualizations.graphiques: Module contenant les classes LineChart et Histogramme.
- src.visualizations: Module contenant la classe Grille et la fonction load_css.
- scripts.MongoDBConnector: Module pour la connexion à MongoDB.
- dotenv: Pour le chargement des variables d'environnement.
"""
from src.utils.helper_data import load_dataset_from_file
from src.visualizations.graphiques import LineChart, Histogramme
from src.visualizations import Grille, load_css
from scripts import MongoDBConnector
import os
import logging
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from src.pages.recipes.Welcom import Welcome
load_dotenv()


logger = logging.getLogger(__name__)
load_dotenv()
DEPLOIEMENT_SITE = os.getenv("DEPLOIEMENT_SITE")

def setup_logging():
    """
    Configure le système de logging de l'application.

    Cette fonction configure le logger de base en définissant :
    - Le niveau de logging à INFO.
    - Le format des messages de log incluant l'horodatage, le niveau, le nom du logger et le message.
    - Deux gestionnaires :
        - FileHandler pour écrire les logs dans le fichier "app.log".
        - StreamHandler pour afficher les logs dans la console.

    Cela permet de centraliser la gestion des logs et d'éviter des configurations multiples.
    """
    try:
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
        logger.info("Configuration du logging réussie")
    except Exception as e:
        logger.error(f"Erreur lors de la configuration du logging : {e}")

# OLD
class DataLoader:
    """
    Classe responsable du chargement des données à partir de fichiers CSV.

    Cette classe fournit des méthodes statiques pour charger des fichiers CSV volumineux
    en utilisant la mise en cache de Streamlit pour améliorer les performances.
    """

    @staticmethod
    @st.cache_data
    def load_large_csv(file_path):
        """
        Charge un fichier CSV volumineux et retourne un DataFrame pandas.

        Cette méthode utilise Streamlit's `cache_data` pour mettre en cache le résultat
        afin d'optimiser les performances lors des rechargements.

        Args:
            file_path (str): Chemin vers le fichier CSV à charger.

        Returns:
            pd.DataFrame: DataFrame contenant les données du fichier CSV.

        Logs :
            INFO: Indique le début du chargement du fichier CSV.
        """
        logger = logging.getLogger("DataLoader.load_large_csv")
        try:
            logger.info(f"Chargement du fichier CSV: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier CSV : {e}")
            raise

# NEW
class DataLoaderMango:
    """
    Classe responsable du chargement des données depuis MongoDB.

    Cette classe gère la connexion à une base de données MongoDB, le chargement des
    données d'une collection spécifique, et la gestion des limites de documents à
    charger. Elle utilise également la mise en cache de Streamlit pour optimiser les
    performances lors des chargements répétitifs.
    """

    def __init__(self, connection_string, database_name, collection_names: list, limit: int = 50000):
        """
        Initialise les paramètres de connexion à MongoDB.

        Args:
            connection_string (str): URI de connexion à MongoDB.
            database_name (str): Nom de la base de données.
            collection_name (str): Nom de la collection à charger.
            limit (int, optional): Nombre maximum de documents à charger. Par défaut à 2000.

        Logs :
            INFO: Indique l'initialisation de DataLoaderMango avec les paramètres fournis.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.logger.info("Initialisation de DataLoaderMango")
            self.connection_string = connection_string
            self.database_name = database_name
            self.collection_names = collection_names
            self.limit = limit
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'initialisation de DataLoaderMango : {e}")
            raise

    @staticmethod
    @st.cache_data
    def load_dataframe(connection_string, database_name, collection_names, limit):
        """
        Charge les données depuis MongoDB et les retourne sous forme de DataFrame.

        Cette méthode établit une connexion à MongoDB, charge les données d'une
        collection spécifique avec une limite de documents, puis ferme la connexion.
        En cas d'erreur lors du chargement des données, une exception est levée.

        Args:
            connection_string (str): URI de connexion à MongoDB.
            database_name (str): Nom de la base de données.
            collection_name (str): Nom de la collection à charger.
            limit (int): Nombre maximum de documents à charger.

        Returns:
            pd.DataFrame: DataFrame contenant les données de la collection.

        Raises:
            Exception: En cas d'erreur lors du chargement des données depuis MongoDB.

        Logs :
            INFO: Indique le début de la connexion à MongoDB et le chargement des données.
            ERROR: Indique une erreur lors du chargement des données.
            INFO: Indique la fermeture de la connexion MongoDB.
        """
        logger = logging.getLogger("DataLoaderMango.load_dataframe")
        try:
            logger.info("Connexion à MongoDB")
            connector = MongoDBConnector(connection_string, database_name)
            data_frames = dict()
            for collection_name in collection_names:
                logger.info(f"Chargement des données depuis {collection_name} avec limite {limit}")
                data = None
                if DEPLOIEMENT_SITE == "ONLINE":
                    connector.connect()
                    logger.info("Connexion établie")
                    data = connector.load_collection_as_dataframe(
                        collection_name, limit=limit)
                else:
                    dataset_dir = os.getenv("DIR_DATASET")
                    data = Welcome.show_welcom(DEPLOIEMENT_SITE, load_dataset_from_file, os.path.join(
                        dataset_dir, "RAW_interactions.csv"), None, None, datetime(1999, 1, 1), datetime(2018, 12, 31), is_interactional=True)
                data['collection_name'] = collection_name  # Ajouter une colonne pour identifier la collection
                data_frames[collection_name] = data
                logger.info(f"Données chargées depuis {collection_name} avec limite {limit}")
            logger.info("Enregistrements terminé")
        except Exception as e:
            logger.error("Erreur lors du chargement des données depuis MongoDB", exc_info=True)
            raise
        finally:
            connector.close()
            logger.info("Connexion MongoDB fermée")
        return data_frames

    def get_data(self):
        """
        Récupère les données chargées depuis MongoDB.

        Utilise la méthode `load_dataframe` pour charger les données avec les paramètres
        d'initialisation de l'instance.

        Returns:
            pd.DataFrame: DataFrame contenant les données chargées.

        Logs :
            INFO: Indique le début de la récupération des données.
        """
        self.logger.info("Récupération des données")
        try:
            return self.load_dataframe(
                self.connection_string,
                self.database_name,
                self.collection_names,
                self.limit
            )
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la récupération des données : {e}")
            raise

class CSSLoader:
    """
    Classe responsable du chargement des feuilles de style CSS.

    Cette classe permet de charger des fichiers CSS pour styliser les pages Streamlit.
    """

    def __init__(self):
        """
        Initialise le CSSLoader en configurant un logger spécifique.

        Logs :
            INFO: Indique l'initialisation de CSSLoader.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initialisation de CSSLoader")

    @staticmethod
    def load(path_to_css):
        """
        Charge un fichier CSS et l'applique à la page Streamlit.

        Args:
            path_to_css (str): Chemin vers le fichier CSS à charger.

        Logs :
            INFO: Indique le début du chargement du fichier CSS.
        """
        logger = logging.getLogger("CSSLoader.load")
        try:
            logger.info(f"Chargement du CSS depuis {path_to_css}")
            load_css(path_to_css)
        except Exception as e:
            logger.error(f"Erreur lors du chargement du CSS : {e}")
            raise

class DataAnalyzer:
    """
    Classe pour l'analyse et le prétraitement des données.

    Cette classe fournit des méthodes pour prétraiter les données, analyser les
    notes des utilisateurs, calculer les moyennes mensuelles, et analyser les
    fréquences des notes.
    """

    def __init__(self, data):
        """
        Initialise l'analyseur de données avec un DataFrame.

        Args:
            data (pd.DataFrame): DataFrame contenant les données à analyser.

        Logs :
            INFO: Indique l'initialisation de DataAnalyzer avec les données fournies.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.logger.info("Initialisation de DataAnalyzer")
            self.data = data
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'initialisation de DataAnalyzer : {e}")
            raise

    def preprocess(self):
        """
        Prétraite les données en convertissant les dates et extrayant l'année.

        Cette méthode vérifie si la colonne 'date' existe dans les données. Si oui,
        elle convertit les valeurs en objets datetime, extrait l'année et l'ajoute
        en tant que nouvelle colonne 'year'. Si la colonne 'date' est absente,
        un avertissement est enregistré.

        Returns:
            pd.DataFrame: DataFrame prétraité.

        Logs :
            INFO: Indique le début du prétraitement des données.
            DEBUG: Affiche un aperçu des données après prétraitement.
            WARNING: Indique l'absence de la colonne 'date' dans les données.
        """
        self.logger.info("Prétraitement des données")
        try:
            if 'date' in self.data.columns:
                self.data['date'] = pd.to_datetime(self.data['date'])
                self.data['year'] = self.data['date'].dt.year.astype(str)
                self.logger.debug(f"Données après prétraitement: {
                                  self.data.head()}")
            else:
                self.logger.warning(
                    "La colonne 'date' est absente des données")
            return self.data
        except Exception as e:
            self.logger.error(
                f"Erreur lors du prétraitement des données : {e}")
            raise

    def analyze_user(self, user_id):
        """
        Analyse les notes moyennes mensuelles pour un utilisateur spécifique.

        Cette méthode filtre les données pour un utilisateur donné, calcule la
        moyenne des notes par mois, et retourne un DataFrame contenant les
        résultats. Si aucune donnée n'est trouvée pour l'utilisateur, None est
        retourné.

        Args:
            user_id (int): Identifiant de l'utilisateur à analyser.

        Returns:
            pd.DataFrame or None: DataFrame contenant les moyennes mensuelles des notes,
                                   ou None si aucune donnée n'est trouvée.

        Logs :
            INFO: Indique le début de l'analyse pour l'utilisateur spécifié.
            INFO: Indique la fin de l'analyse si des données sont trouvées.
            WARNING: Indique qu'aucune donnée n'a été trouvée pour l'utilisateur.
        """
        self.logger.info(f"Analyse des données pour l'utilisateur ID: {user_id}")
        try:
            user_data = self.data[self.data['user_id'] == user_id].copy()
            if not user_data.empty:
                user_data['year_month'] = user_data['date'].dt.to_period('M')
                monthly_avg = user_data.groupby('year_month')['rating'].mean()
                monthly_avg.index = monthly_avg.index.astype(str)
                monthly_avg = monthly_avg.reset_index()
                monthly_avg.columns = ['Mois', 'Note moyenne']
                self.logger.info(
                    f"Analyse utilisateur terminée pour ID: {user_id}")
                return monthly_avg
            self.logger.warning(
                f"Aucune donnée trouvée pour l'utilisateur ID: {user_id}")
            return None
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'analyse des données pour l'utilisateur ID: {user_id} : {e}")
            raise

    def analyze_monthly_ratings(self):
        """
        Calcule la moyenne des notes mensuelles.

        Cette méthode resample les données par mois en utilisant la date comme index,
        calcule la moyenne des notes pour chaque mois, et retourne un DataFrame
        contenant les résultats.

        Returns:
            pd.DataFrame: DataFrame contenant les moyennes mensuelles des notes.

        Logs :
            INFO: Indique le début de l'analyse des moyennes mensuelles.
            DEBUG: Affiche un aperçu des moyennes mensuelles calculées.
        """
        self.logger.info("Analyse des notes moyennes mensuelles")
        try:
            monthly_average_rating = self.data.set_index('date').resample('ME')[
                'rating'].mean().reset_index()
            monthly_average_rating.columns = ['Mois', 'Note moyenne']
            self.logger.debug(f"Notes moyennes mensuelles: {
                              monthly_average_rating.head()}")
            return monthly_average_rating
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'analyse des notes moyennes mensuelles : {e}")
            raise

    def analyze_ratings_frequencies(self):
        """
        Analyse les fréquences des différentes notes dans les données.

        Cette méthode identifie les notes uniques dans les données et calcule
        le nombre d'occurrences pour chaque note.

        Returns:
            list of tuples: Liste contenant des tuples de la forme (note, DataFrame des données correspondantes).

        Logs :
            INFO: Indique le début de l'analyse des fréquences des notes.
            DEBUG: Indique le nombre d'occurrences pour chaque note.
        """
        self.logger.info("Analyse des fréquences des notes")
        try:
            unique_ratings = self.data['rating'].unique()
            frequency_data = []
            for rating in sorted(unique_ratings):
                rating_data = self.data[self.data['rating'] == rating]
                frequency_data.append((rating, rating_data))
                self.logger.debug(f"Fréquence pour la note {rating}: {
                                  len(rating_data)} occurrences")
            return frequency_data
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'analyse des fréquences des notes : {e}")
            raise

    def analyze_user_ratings_frequencies(self, user_id):
        """
        Analyse les fréquences des notes pour un utilisateur spécifique.

        Cette méthode filtre les données pour un utilisateur donné et calcule
        le nombre d'occurrences pour chaque note attribuée par cet utilisateur.

        Args:
            user_id (int): Identifiant de l'utilisateur à analyser.

        Returns:
            list of tuples or None: Liste contenant des tuples de la forme (note, DataFrame des données correspondantes),
                                    ou None si aucune donnée n'est trouvée pour l'utilisateur.

        Logs :
            INFO: Indique le début de l'analyse des fréquences des notes pour l'utilisateur spécifié.
            DEBUG: Indique le nombre d'occurrences pour chaque note de l'utilisateur.
            WARNING: Indique qu'aucune donnée de fréquence n'a été trouvée pour l'utilisateur.
        """
        self.logger.info(f"Analyse des fréquences des notes pour l'utilisateur ID: {user_id}")
        try:
            user_data = self.data[self.data['user_id'] == user_id]
            if not user_data.empty:
                unique_ratings_user = user_data['rating'].unique()
                frequency_data = []
                for rating in sorted(unique_ratings_user):
                    rating_data = user_data[user_data['rating'] == rating]
                    frequency_data.append((rating, rating_data))
                    self.logger.debug(f"Fréquence pour la note {rating} de l'utilisateur {
                                      user_id}: {len(rating_data)} occurrences")
                return frequency_data
            self.logger.warning(
                f"Aucune donnée de fréquence trouvée pour l'utilisateur ID: {user_id}")
            return None
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'analyse des fréquences des notes pour l'utilisateur ID: {user_id} : {e}")
            raise

    def analyze_activity_on_mangetamain(self):
        """
        Analyse l'évolution de l'activité sur l'application Mangetamain.

        Cette méthode convertit les dates de soumission en objets datetime,
        extrait l'année et le mois, et calcule le nombre de recettes soumises
        chaque mois.

        Returns:
            pd.DataFrame or None: DataFrame contenant le nombre de recettes par mois,
                                   ou None si la colonne 'submitted' est absente.

        Logs :
            INFO: Indique le début de l'analyse de l'activité sur Mangetamain.
            DEBUG: Affiche un aperçu des comptes mensuels.
            WARNING: Indique l'absence de la colonne 'submitted' dans les données.
        """
        self.logger.info("Analyse de l'activité sur Mangetamain")
        try:
            if 'submitted' in self.data.columns:
                self.data['submitted'] = pd.to_datetime(self.data['submitted'])
                self.data['year_month'] = self.data['submitted'].dt.to_period(
                    'M')
                monthly_counts = self.data.groupby(
                    'year_month').size().reset_index(name='recipe_count')
                monthly_counts['year_month'] = monthly_counts['year_month'].astype(
                    str)
                self.logger.debug(f"Comptes mensuels: {monthly_counts.head()}")
                return monthly_counts
            else:
                self.logger.warning(
                    "La colonne 'submitted' est absente des données")
                return None
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'analyse de l'activité sur Mangetamain : {e}")
            raise

class VisualizationManager:
    """
    Classe pour gérer les visualisations des données.

    Cette classe fournit des méthodes statiques pour afficher différents types de
    graphiques (ligne, histogramme) et des fréquences de notes dans l'interface
    Streamlit.
    """

    def __init__(self):
        """
        Initialise le VisualizationManager en configurant un logger spécifique.

        Logs :
            INFO: Indique l'initialisation de VisualizationManager.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initialisation de VisualizationManager")

    @staticmethod
    def display_line_chart(data, x, y, title):
        """
        Affiche un graphique en ligne dans Streamlit.

        Args:
            data (pd.DataFrame): DataFrame contenant les données à visualiser.
            x (str): Nom de la colonne à utiliser pour l'axe des X.
            y (str): Nom de la colonne à utiliser pour l'axe des Y.
            title (str): Titre du graphique.

        Logs :
            INFO: Indique le début de l'affichage du graphique en ligne.
        """
        logger = logging.getLogger("VisualizationManager.display_line_chart")
        try:
            logger.info(f"Affichage du graphique en ligne: {title}")
            st.subheader(title)
            line_chart = LineChart(data=data, x=x, y=y,
                                   height=400, line_color='rgb(26, 28, 35)')
            graphiques = [{"titre": "", "graphique": line_chart}]
            grille = Grille(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
            grille.afficher(graphiques)
        except Exception as e:
            logger.error(
                f"Erreur lors de l'affichage du graphique en ligne : {e}")
            raise

    @staticmethod
    def display_histogram(data, x, title, bin_size=1):
        """
        Affiche un histogramme dans Streamlit.

        Args:
            data (pd.DataFrame): DataFrame contenant les données à visualiser.
            x (str): Nom de la colonne à utiliser pour l'axe des X.
            title (str): Titre de l'histogramme.
            bin_size (int, optional): Taille des bins de l'histogramme. Par défaut à 1.

        Logs :
            INFO: Indique le début de l'affichage de l'histogramme.
        """
        logger = logging.getLogger("VisualizationManager.display_histogram")
        try:
            logger.info(f"Affichage de l'histogramme: {title}")
            st.subheader(title)
            histogram = Histogramme(
                data=data, x=x, bin_size=bin_size, height=400, bar_color='rgb(26, 28, 35)')
            graphiques = [{"titre": "", "graphique": histogram}]
            grille = Grille(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
            grille.afficher(graphiques)
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de l'histogramme : {e}")
            raise

    @staticmethod
    def display_ratings_frequencies(frequency_data, x, title):
        """
        Affiche les fréquences des notes sous forme d'histogrammes dans Streamlit.

        Args:
            frequency_data (list of tuples): Liste de tuples contenant la note et le DataFrame correspondant.
            x (str): Nom de la colonne à utiliser pour l'axe des X.
            title (str): Titre de la section de visualisation.

        Logs :
            INFO: Indique le début de l'affichage des fréquences des notes.
            DEBUG: Indique l'ajout d'un graphique pour chaque note.
        """
        logger = logging.getLogger("VisualizationManager.display_ratings_frequencies")
        try:
            logger.info(f"Affichage des fréquences des notes: {title}")
            st.subheader(title)
            graphiques = []
            for rating, rating_data in frequency_data:
                histogram = Histogramme(
                    data=rating_data,
                    bin_size=1,
                    x=x,
                    height=300,
                    bar_color='rgb(26, 28, 35)',
                    line_color='rgb(8,48,107)'
                )
                graphiques.append({
                    "titre": f"Fréquence de la note {int(rating)}",
                    "graphique": histogram,
                })
                logger.debug(f"Graphique pour la note {rating} ajouté")
            grille = Grille(nb_lignes=2, nb_colonnes=3,
                            largeurs_colonnes=[1, 1, 1])
            grille.afficher(graphiques)
        except Exception as e:
            logger.error(
                f"Erreur lors de l'affichage des fréquences des notes : {e}")
            raise

class StreamlitPage(DataLoaderMango):
    """
    Classe principale pour l'intégration avec Streamlit.

    Cette classe hérite de DataLoaderMango pour charger les données depuis MongoDB
    et fournit des méthodes pour charger le CSS, les données, exécuter les analyses
    et afficher les résultats via Streamlit.
    """

    def __init__(self):
        """
        Initialise les paramètres de DataLoaderMango et configure les paramètres Streamlit.

        Charge les variables d'environnement nécessaires pour la connexion à MongoDB
        et initialise les attributs de l'instance.

        Logs :
            INFO: Indique l'initialisation de StreamlitPage et de DataLoaderMango.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.logger.info("Initialisation de StreamlitPage")
            self.data = None
            self.CONNECTION_STRING = os.getenv("CONNECTION_STRING")
            self.DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
            self.COLLECTION_RAW_INTERACTIONS = os.getenv(
                "COLLECTION_RAW_INTERACTIONS", "raw_interaction")
            self.COLLECTION_RECIPES_NAME = os.getenv(
                "COLLECTION_RECIPES_NAME", 'recipes')

            self.COLLECTION_NAMES = [
                self.COLLECTION_RAW_INTERACTIONS, self.COLLECTION_RECIPES_NAME]

            super().__init__(self.CONNECTION_STRING, self.DATABASE_NAME,
                             self.COLLECTION_NAMES, limit=50000)
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'initialisation de StreamlitPage : {e}")
            raise

    def load_css(self):
        """
        Charge la feuille de style CSS pour styliser la page Streamlit.

        Utilise la classe CSSLoader pour charger le fichier CSS spécifié.

        Logs :
            INFO: Indique le début du chargement du CSS.
        """
        self.logger.info("Chargement du CSS")
        try:
            path_to_css = 'src/css_pages/analyse_user.css'
            CSSLoader.load(path_to_css)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du CSS : {e}")
            raise

    def load_data(self):
        """
        Charge les données depuis MongoDB et les affiche dans Streamlit.

        Utilise la méthode `get_data` héritée de DataLoaderMango pour charger les données.
        En cas de succès, affiche un aperçu des données. En cas d'échec, affiche une erreur
        dans l'interface Streamlit.

        Logs :
            INFO: Indique le début du chargement des données.
            INFO: Indique le succès du chargement des données avec le nombre d'enregistrements.
            ERROR: Indique une erreur lors du chargement des données.
        """
        self.logger.info("Chargement des données depuis MongoDB")
        try:
            self.data = self.get_data()
            self.logger.info(f"Données chargées avec succès, {len(self.data[self.COLLECTION_RAW_INTERACTIONS])} enregistrements")
        except Exception as e:
            self.logger.error("Erreur lors du chargement des données", exc_info=True)
            st.error("Impossible de charger les données.")

    def run_analysis(self):
        """
        Exécute l'analyse des données et génère les visualisations correspondantes.

        Cette méthode effectue les étapes suivantes :
        - Affiche un texte introductif.
        - Prétraite les données.
        - Affiche les fréquences globales des notes sous forme d'histogramme avec un texte explicatif.
        - Analyse les fréquences des notes au fil du temps avec un texte explicatif.
        - Calcule et affiche les notes moyennes mensuelles avec un texte explicatif.
        - Analyse les fréquences des notes pour un utilisateur spécifique avec un texte explicatif.
        - Analyse les notes par utilisateur.

        Chaque étape inclut des vérifications pour s'assurer que les colonnes nécessaires
        sont présentes dans les données et enregistre des logs appropriés.

        Logs :
            INFO: Indique le début de l'analyse des données.
            INFO/WARNING: Indique l'état de présence des colonnes nécessaires.
        """
        st.title("Analyse sur la perte de popularité de l'application Mangetamain")

        # Texte introductif
        if st.checkbox("Afficher l'objectif de cette Analyse"):
            st.subheader("Objectif de l'Analyse")
            introduction = """
            Cette analyse vise à explorer **les raisons de la perte de popularité de l'application Mangetamain** en examinant :

            - Les fréquences de notation des utilisateurs au fil du temps.
            - Les tendances des évaluations.
            - L'activité des utilisateurs.

            **Objectif** :
            Comprendre comment la popularité a évolué et identifier les facteurs ayant conduit à une diminution de l'intérêt pour la plateforme.
            """
            st.markdown(introduction)
            st.divider()

        st.write("Aperçu des données :", self.data[self.COLLECTION_RAW_INTERACTIONS].head())

        self.logger.info("Démarrage de l'analyse des données")
        if self.data[self.COLLECTION_RAW_INTERACTIONS] is not None:
            analyzer = DataAnalyzer(self.data[self.COLLECTION_RAW_INTERACTIONS])
            self.data[self.COLLECTION_RAW_INTERACTIONS] = analyzer.preprocess()

            # Analyse des fréquences des notes
            st.title("Analyse de Fréquences")
            if 'rating' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns:
                self.logger.info("Affichage de l'histogramme des notes globales")
                VisualizationManager.display_histogram(self.data[self.COLLECTION_RAW_INTERACTIONS], 'rating', "Fréquence globale des notes")
                if st.checkbox("Afficher l'explication"):
                    st.subheader("Analyse de la Fréquence des Notes")

                    # Diviser l'explication en paragraphes
                    st.markdown("""
                    La visualisation de la **fréquence des évaluations** met en évidence une répartition inégale des notes attribuées par les utilisateurs sur l’application.

                    ### Points Clés :
                    - La majorité des évaluations se concentrent sur la **note maximale (5)**, ce qui reflète une forte appréciation globale des recettes par les utilisateurs.
                    - La **faible fréquence des notes intermédiaires (1 à 3)** suggère que les utilisateurs ne s’expriment que lorsqu’ils ont une expérience particulièrement positive.

                    ### Interprétations :
                    Ce comportement pourrait indiquer que :
                    1. Les utilisateurs sont **moins enclins à noter les recettes moins marquantes**, réduisant ainsi la diversité des retours disponibles.
                    2. Cela soulève la question de **l’engagement des utilisateurs** et de l’impact des évaluations sur l’amélioration des recettes proposées.
                    """)

                    # Ajout d'un séparateur ou d'un espace pour l'esthétique
                    st.divider()
            else:
                self.logger.warning("La colonne 'rating' est absente du fichier.")
                st.warning("La colonne 'rating' est absente du fichier.")

            # Analyse des fréquences des notes au fil du temps
            st.title("Fréquence des notes au fil du temps")
            if 'date' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns and 'rating' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns:
                self.logger.info("Analyse des fréquences des notes au fil du temps")
                frequency_data = analyzer.analyze_ratings_frequencies()
                VisualizationManager.display_ratings_frequencies(
                    frequency_data, x='year', title="Fréquence des Notes au fil du temps")
                # Texte explicatif sous le graphique
                if st.checkbox("Afficher l'explication des fréquences au fil du temps"):
                    st.subheader("Analyse des Fréquences des Notes au Fil du Temps")

                    # Diviser le texte en sections et ajouter des points clés
                    st.markdown("""
                    Cette visualisation illustre **l'évolution des fréquences des notes attribuées par les utilisateurs** sur l'application au fil des années.

                    ### Observations Principales :
                    - Les notes **2, 3, 4 et 5**, représentant des appréciations positives ou moyennes :
                    - Atteignent leur **pic de fréquence autour de 2007-2009**.
                    - Présentent une **baisse constante après cette période**, suggérant une diminution globale de l'activité des utilisateurs.
                    - Les notes basses **0 et 1** :
                    - Affichent également une tendance à la baisse après leur propre pic.
                    - Restent globalement moins fréquentes que les notes positives.

                    ### Interprétations :
                    - **Désintérêt progressif des utilisateurs** :
                    La diminution des notes, positives ou négatives, pourrait indiquer un désintérêt global pour l'application.
                    - **Impact du contenu attractif** :
                    Une baisse potentielle du nombre de recettes ou d'autres contenus attractifs peut expliquer ce phénomène.
                    """)

                    # Ajout d'un séparateur visuel pour une meilleure structuration
                    st.divider()
            else:
                self.logger.warning("Les colonnes 'date' ou 'rating' sont absentes du fichier.")
                st.warning("Les colonnes 'date' ou 'rating' sont absentes du fichier.")

            # Analyse des notes moyennes mensuelles
            st.title("Analyse des notes moyennes mensuelles")
            if 'rating' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns and 'date' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns:
                self.logger.info("Analyse des notes moyennes mensuelles")
                monthly_ratings = analyzer.analyze_monthly_ratings()
                VisualizationManager.display_line_chart(
                    monthly_ratings, 'Mois', 'Note moyenne',
                    "Notation moyenne mensuelle au fil du temps"
                )
                # Case à cocher pour afficher l'explication
                if st.checkbox("Afficher l'explication des notes moyennes mensuelles"):
                    st.subheader("Explication des Notes Moyennes Mensuelles")

                    # Structuration en sections
                    st.markdown("""
                    Cette courbe met en lumière **l'évolution de la note moyenne hebdomadaire** attribuée par les utilisateurs au fil du temps.

                    ### Observations Principales :
                    - **2001 à 2010** :
                    - Les notes moyennes sont **stables autour de 4**, reflétant une forte satisfaction des utilisateurs vis-à-vis des recettes proposées.
                    - **Après 2009** :
                    - Une **baisse progressive des notes moyennes** est observée, atteignant un **point bas significatif vers 2016-2017**, suivi d’un léger redressement.

                    ### Interprétations :
                    - Cette diminution des notes moyennes peut s’expliquer par :
                    - Une **baisse des notes élevées (4 et 5)**.
                    - Une **augmentation des notes faibles (1 et 2)**.
                    - Ces tendances suggèrent :
                    - Un possible **déclin de la satisfaction des utilisateurs** concernant les recettes proposées.
                    - Une **évolution des attentes des utilisateurs** au fil du temps.

                    """)

                    # Ajouter un séparateur pour une présentation plus nette
                    st.divider()
            else:
                self.logger.warning("Les colonnes 'rating' ou 'date' sont absentes du fichier.")
                st.warning("Les colonnes 'rating' ou 'date' sont absentes du fichier.")

            # Analyse des fréquences des notes par utilisateur
            st.title("Fréquence des Notes par utilisateur au fil du temps")
            if 'user_id' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns:
                # Définir le nombre minimal de notes pour une analyse détaillée
                min_notes = 10  # Exemple: minimum 10 notes par utilisateur
                # Filtrer les utilisateurs ayant au moins min_notes
                user_counts = self.data[self.COLLECTION_RAW_INTERACTIONS]['user_id'].value_counts()
                eligible_users = user_counts[user_counts >= min_notes].index.tolist()

                user_id = st.number_input(
                    "Entrez l'ID utilisateur à analyser :", min_value=0, key=2)

                # Vérifier si l'utilisateur a suffisamment de notes
                if user_id in eligible_users:
                    self.logger.info(f"Analyse des fréquences des notes pour l'utilisateur ID: {user_id}")
                    user_frequency_data = analyzer.analyze_user_ratings_frequencies(user_id)
                    if user_frequency_data:
                        VisualizationManager.display_ratings_frequencies(
                            user_frequency_data, x='year', title=f"Fréquence des Notes pour l'utilisateur {user_id}"
                        )
                        # Texte explicatif sous le graphique
                        user_freq_explanation = """
                        *Ici on étudie la fréquence des notes en fonction de l'utilisateur. Cela permet de savoir si l'utilisateur au fil des années devient plus difficile ou pas.*

                        *On va fixer une variable pour déterminer le nombre de notes minimal que l'utilisateur a mis pour avoir suffisamment de notes pour faire une analyse détaillée.*
                        """
                        st.markdown(user_freq_explanation)
                    else:
                        self.logger.warning(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
                        st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
                else:
                    if user_id != 0:
                        st.warning(f"L'utilisateur {user_id} n'a pas suffisamment de notes pour une analyse détaillée (minimum {min_notes} notes requises).")
            else:
                self.logger.warning("La colonne 'user_id' est absente du fichier.")
                st.error("La colonne 'user_id' est absente du fichier.")

            # Analyse des notes par utilisateur
            st.title("Analyse des notes par utilisateur")
            if 'user_id' in self.data[self.COLLECTION_RAW_INTERACTIONS].columns:
                user_id = st.number_input("Entrez l'ID utilisateur à analyser :", min_value=0)
                self.logger.info(f"Analyse des notes pour l'utilisateur ID: {user_id}")
                user_analysis = analyzer.analyze_user(user_id)
                if user_analysis is not None:
                    VisualizationManager.display_line_chart(
                        user_analysis, 'Mois', 'Note moyenne',
                        "Aperçu des notes utilisateur au fil du temps"
                    )
                else:
                    self.logger.warning(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
                    st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
            else:
                self.logger.warning("La colonne 'user_id' est absente du fichier.")
                st.error("La colonne 'user_id' est absente du fichier.")

            # Evolution de l’activité sur l’application Mangetamain
            st.title("Evolution de l’activité sur l’application Mangetamain")
            if 'submitted' in self.data[self.COLLECTION_RECIPES_NAME].columns:
                analyzer_recipe = DataAnalyzer(
                    self.data[self.COLLECTION_RECIPES_NAME])
                monthly_counts = analyzer_recipe.analyze_activity_on_mangetamain()
                if monthly_counts is not None:
                    VisualizationManager.display_line_chart(
                        monthly_counts, 'year_month', 'recipe_count', title=""
                    )
                    # Texte explicatif sous le graphique
                    if st.checkbox("Afficher l'explication de l'évolution de l'activité"):
                        st.subheader("Évolution de l'Activité sur l'Application")

                        # Structuration en sections avec Markdown
                        st.markdown("""
                        L’analyse des données met en évidence plusieurs tendances marquantes concernant l’**évolution de l’activité** sur l’application Mangetamain.

                        ### Observations Principales :
                        - **Diminution des notes élevées (4 et 5)** :
                        - Une baisse notable après **2009**, reflétant une satisfaction décroissante des utilisateurs.
                        - **Augmentation légère des notes basses (1 et 2)** :
                        - Indique une **insatisfaction croissante** parmi certains utilisateurs.

                        ### Facteurs Contributifs :
                        - **Réduction du contenu attractif** :
                        - Diminution progressive du nombre de recettes mises en ligne après un **pic d’activité entre 2007 et 2009**.
                        - Moins d’opportunités d’interaction pour les utilisateurs, créant un cercle vicieux de baisse d’engagement.
                        - **Concurrence accrue** :
                        - Apparition de **plateformes concurrentes** proposant des expériences plus riches et interactives.

                        ### Suggestions pour Inverser la Tendance :
                        - **Stimuler la création de nouvelles recettes** pour renouveler le contenu.
                        - **Diversifier les types de contenu** proposés sur la plateforme.
                        - **Renforcer l’expérience utilisateur** par des fonctionnalités interactives et engageantes.

                        """)

                        # Ajouter un séparateur pour une meilleure structuration visuelle
                        st.divider()
            else:
                self.logger.warning("La colonne 'submitted' est absente du fichier.")
                st.error("La colonne 'submitted' est absente du fichier.")

    def run(self):
        """
        Configure la page Streamlit, charge le CSS et les données, puis exécute l'analyse.

        Cette méthode configure la disposition de la page Streamlit, charge le CSS,
        charge les données depuis MongoDB, et si les données sont disponibles, exécute
        l'analyse des données.

        Logs :
            INFO: Indique la configuration de la page Streamlit.
        """
        self.logger.info("Configuration de la page Streamlit")
        try:
            st.set_page_config(layout="wide")
            self.load_css()
            self.load_data()
            if self.data is not None:
                self.run_analysis()
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la configuration de la page Streamlit : {e}")
            raise

def main():
    """
    Point d'entrée principal de l'application Streamlit.

    Cette fonction configure le logging, initialise la page Streamlit, et exécute
    la méthode `run` pour démarrer l'application.

    Logs :
        INFO: Indique le démarrage de l'application Streamlit.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Démarrage de l'application Streamlit")

    try:
        page_analyse_user = StreamlitPage()
        page_analyse_user.run()
    except Exception as e:
        logger.error(
            f"Erreur lors du démarrage de l'application Streamlit : {e}")
        raise

if __name__ == "__main__":
    main()
