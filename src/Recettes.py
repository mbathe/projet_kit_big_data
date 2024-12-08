
# fmt: off



"""
Cette page est le point d'entrée de l'application, 

Elle contient la méthode à appeler pour lancer l'application qui charge ensuite les différente page



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

"""
import streamlit as st
import os
import logging
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from src.pages.recipes.Analyse_recipes import DataManager, DisplayManager
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:
        welcome_container = st.empty()
        data_manager = DataManager()
        DisplayManager.load_css()
        welcome_container.empty()
        container = st.container()
        with container:
            manager = DisplayManager(data_manager=data_manager)
            manager.sidebar()
            manager.display_tab()
    except Exception as e:
        logging.error(f"Error in main: {e}")
