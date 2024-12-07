
# fmt: off

import streamlit as st

import os
import logging
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from src.pages.recipes.Analyse_recipes import DataManager, DisplayManager
from src.process.recommandation import AdvancedRecipeRecommender
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:

        welcome_container = st.empty()
        data_manager = DataManager()
        recommender: AdvancedRecipeRecommender = AdvancedRecipeRecommender(
            recipes_df=data_manager.get_recipe_data().st.session_state.data)
        DisplayManager.load_css()
        welcome_container.empty()
        container = st.container()
        with container:
            manager = DisplayManager(data_manager=data_manager,recommander=recommender)
            manager.sidebar()
            manager.display_tab()
    except Exception as e:
        logging.error(f"Error in main: {e}")
