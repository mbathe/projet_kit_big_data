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

from src.visualizations.graphiques import LineChart, Histogramme
from src.visualizations import Grille, load_css
from scripts import MongoDBConnector

import os
import logging

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement à partir d'un fichier .env
load_dotenv()


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
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )


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
        logger.info(f"Chargement du fichier CSV: {file_path}")
        return pd.read_csv(file_path)


# NEW
class DataLoaderMango:
    """
    Classe responsable du chargement des données depuis MongoDB.

    Cette classe gère la connexion à une base de données MongoDB, le chargement des
    données d'une collection spécifique, et la gestion des limites de documents à
    charger. Elle utilise également la mise en cache de Streamlit pour optimiser les
    performances lors des chargements répétitifs.
    """

    def __init__(self, connection_string, database_name, collection_name, limit=2000):
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
        self.logger.info("Initialisation de DataLoaderMango")
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        self.limit = limit

    @staticmethod
    @st.cache_data
    def load_dataframe(connection_string, database_name, collection_name, limit):
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
        logger.info("Connexion à MongoDB")
        connector = MongoDBConnector(connection_string, database_name)
        try:
            connector.connect()
            logger.info("Connexion établie")
            data = connector.load_collection_as_dataframe(collection_name, limit=limit)
            logger.info(f"Données chargées depuis {collection_name} avec limite {limit}")
        except Exception as e:
            logger.error("Erreur lors du chargement des données depuis MongoDB", exc_info=True)
            raise
        finally:
            connector.close()
            logger.info("Connexion MongoDB fermée")
        return data

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
        return self.load_dataframe(
            self.connection_string,
            self.database_name,
            self.collection_name,
            self.limit
        )


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
        logger.info(f"Chargement du CSS depuis {path_to_css}")
        load_css(path_to_css)


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
        self.logger.info("Initialisation de DataAnalyzer")
        self.data = data

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
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data['year'] = self.data['date'].dt.year.astype(str)
            self.logger.debug(f"Données après prétraitement: {self.data.head()}")
        else:
            self.logger.warning("La colonne 'date' est absente des données")
        return self.data

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
        user_data = self.data[self.data['user_id'] == user_id].copy()
        if not user_data.empty:
            user_data['year_month'] = user_data['date'].dt.to_period('M')
            monthly_avg = user_data.groupby('year_month')['rating'].mean()
            monthly_avg.index = monthly_avg.index.astype(str)
            monthly_avg = monthly_avg.reset_index()
            monthly_avg.columns = ['Mois', 'Note moyenne']
            self.logger.info(f"Analyse utilisateur terminée pour ID: {user_id}")
            return monthly_avg
        self.logger.warning(f"Aucune donnée trouvée pour l'utilisateur ID: {user_id}")
        return None

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
        monthly_average_rating = self.data.set_index('date').resample('ME')['rating'].mean().reset_index()
        monthly_average_rating.columns = ['Mois', 'Note moyenne']
        self.logger.debug(f"Notes moyennes mensuelles: {monthly_average_rating.head()}")
        return monthly_average_rating

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
        unique_ratings = self.data['rating'].unique()
        frequency_data = []
        for rating in sorted(unique_ratings):
            rating_data = self.data[self.data['rating'] == rating]
            frequency_data.append((rating, rating_data))
            self.logger.debug(f"Fréquence pour la note {rating}: {len(rating_data)} occurrences")
        return frequency_data

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
        user_data = self.data[self.data['user_id'] == user_id]
        if not user_data.empty:
            unique_ratings_user = user_data['rating'].unique()
            frequency_data = []
            for rating in sorted(unique_ratings_user):
                rating_data = user_data[user_data['rating'] == rating]
                frequency_data.append((rating, rating_data))
                self.logger.debug(f"Fréquence pour la note {rating} de l'utilisateur {user_id}: {len(rating_data)} occurrences")
            return frequency_data
        self.logger.warning(f"Aucune donnée de fréquence trouvée pour l'utilisateur ID: {user_id}")
        return None


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
        logger.info(f"Affichage du graphique en ligne: {title}")
        st.subheader(title)
        line_chart = LineChart(data=data, x=x, y=y, height=400, line_color='rgb(26, 28, 35)')
        graphiques = [{"titre": "", "graphique": line_chart}]
        grille = Grille(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
        grille.afficher(graphiques)

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
        logger.info(f"Affichage de l'histogramme: {title}")
        st.subheader(title)
        histogram = Histogramme(data=data, x=x, bin_size=bin_size, height=400, bar_color='rgb(26, 28, 35)')
        graphiques = [{"titre": "", "graphique": histogram}]
        grille = Grille(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
        grille.afficher(graphiques)

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
        grille = Grille(nb_lignes=2, nb_colonnes=3, largeurs_colonnes=[1, 1, 1])
        grille.afficher(graphiques)


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
        self.logger.info("Initialisation de StreamlitPage")

        self.data = None
        self.CONNECTION_STRING = os.getenv("CONNECTION_STRING")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "testdb")
        self.COLLECTION_RAW_INTERACTIONS = os.getenv(
            "COLLECTION_RAW_INTERACTIONS", "raw_interaction")

        super().__init__(self.CONNECTION_STRING, self.DATABASE_NAME,
                         self.COLLECTION_RAW_INTERACTIONS, limit=2000)

    def load_css(self):
        """
        Charge la feuille de style CSS pour styliser la page Streamlit.

        Utilise la classe CSSLoader pour charger le fichier CSS spécifié.

        Logs :
            INFO: Indique le début du chargement du CSS.
        """
        self.logger.info("Chargement du CSS")
        path_to_css = 'src/css_pages/analyse_user.css'
        CSSLoader.load(path_to_css)

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
            self.logger.info(f"Données chargées avec succès, {len(self.data)} enregistrements")
            st.write("Aperçu des données :", self.data.head())
        except Exception as e:
            self.logger.error("Erreur lors du chargement des données", exc_info=True)
            st.error("Impossible de charger les données.")

    def run_analysis(self):
        """
        Exécute l'analyse des données et génère les visualisations correspondantes.

        Cette méthode effectue les étapes suivantes :
        - Prétraite les données.
        - Affiche les fréquences globales des notes sous forme d'histogramme.
        - Analyse les fréquences des notes au fil du temps.
        - Calcule et affiche les notes moyennes mensuelles.
        - Analyse les fréquences des notes pour un utilisateur spécifique.
        - Analyse les notes par utilisateur.

        Chaque étape inclut des vérifications pour s'assurer que les colonnes nécessaires
        sont présentes dans les données et enregistre des logs appropriés.

        Logs :
            INFO: Indique le début de l'analyse des données.
            INFO/WARNING: Indique l'état de présence des colonnes nécessaires.
        """
        self.logger.info("Démarrage de l'analyse des données")
        if self.data is not None:
            analyzer = DataAnalyzer(self.data)
            self.data = analyzer.preprocess()

            # Analyse des fréquences des notes
            st.title("Analyse de Fréquences")
            if 'rating' in self.data.columns:
                self.logger.info("Affichage de l'histogramme des notes globales")
                VisualizationManager.display_histogram(self.data, 'rating', "Fréquence globale des notes")
            else:
                self.logger.warning("La colonne 'rating' est absente du fichier.")
                st.warning("La colonne 'rating' est absente du fichier.")

            # Analyse des fréquences des notes au fil du temps
            st.title("Fréquence des notes au fil du temps")
            if 'date' in self.data.columns and 'rating' in self.data.columns:
                self.logger.info("Analyse des fréquences des notes au fil du temps")
                frequency_data = analyzer.analyze_ratings_frequencies()
                VisualizationManager.display_ratings_frequencies(
                    frequency_data, x='year', title="Fréquence des Notes au fil du temps")
            else:
                self.logger.warning("Les colonnes 'date' ou 'rating' sont absentes du fichier.")
                st.warning("Les colonnes 'date' ou 'rating' sont absentes du fichier.")

            # Analyse des notes moyennes mensuelles
            st.title("Analyse des notes moyennes mensuelles")
            if 'rating' in self.data.columns and 'date' in self.data.columns:
                self.logger.info("Analyse des notes moyennes mensuelles")
                monthly_ratings = analyzer.analyze_monthly_ratings()
                VisualizationManager.display_line_chart(
                    monthly_ratings, 'Mois', 'Note moyenne',
                    "Notation moyenne mensuelle au fil du temps"
                )
            else:
                self.logger.warning("Les colonnes 'rating' ou 'date' sont absentes du fichier.")
                st.warning("Les colonnes 'rating' ou 'date' sont absentes du fichier.")

            # Analyse des fréquences des notes par utilisateur
            st.title("Fréquence des Notes par utilisateur au fil du temps")
            if 'user_id' in self.data.columns:
                user_id = st.number_input("Entrez l'ID utilisateur à analyser :", min_value=0, key=2)
                self.logger.info(f"Analyse des fréquences des notes pour l'utilisateur ID: {user_id}")
                user_frequency_data = analyzer.analyze_user_ratings_frequencies(user_id)
                if user_frequency_data:
                    VisualizationManager.display_ratings_frequencies(
                        user_frequency_data, x='year', title=f"Fréquence des Notes pour l'utilisateur {user_id}"
                    )
                else:
                    self.logger.warning(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
                    st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
            else:
                self.logger.warning("La colonne 'user_id' est absente du fichier.")
                st.error("La colonne 'user_id' est absente du fichier.")

            # Analyse des notes par utilisateur
            st.title("Analyse des notes par utilisateur")
            if 'user_id' in self.data.columns:
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
        st.set_page_config(layout="wide")
        self.load_css()
        self.load_data()
        if self.data is not None:
            self.run_analysis()


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

    page_analyse_user = StreamlitPage()
    page_analyse_user.run()


if __name__ == "__main__":
    main()
