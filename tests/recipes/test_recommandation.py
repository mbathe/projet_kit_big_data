import pytest
import pandas as pd
import numpy as np
from src.pages.recipes.recommandation import recommandation_page
from src.process.recommandation import AdvancedRecipeRecommender
from unittest.mock import patch, MagicMock
import os


# Sample data for testing
sample_data = {
    'id': [1, 2, 3],
    'name': ['Recipe1', 'Recipe2', 'Recipe3'],
    'ingredients': ["['salt', 'pepper', 'chicken']", "['salt', 'pepper', 'beef']", "['salt', 'pepper', 'fish']"],
    'minutes': [30, 45, 60],
    'n_ingredients': [3, 3, 3],
    'n_steps': [5, 6, 7]
}


@pytest.fixture
def sample_recipes_df():
    dir_path = os.path.join(os.path.dirname(
        __file__), '../../static/test_dir/recipe_exemple.csv')
    return pd.read_csv(dir_path)


@pytest.fixture
def recommender_instance():
    df = pd.DataFrame(sample_data)
    recommender = AdvancedRecipeRecommender(df)
    return recommender

# Test for the recommandation_page function


def test_recommandation_page(sample_recipes_df):
    recommender = AdvancedRecipeRecommender(sample_recipes_df)

    # Mocking Streamlit functions
    from unittest.mock import patch
    with patch('streamlit.selectbox', return_value="Recommandations de Recettes"):
        with patch('streamlit.selectbox', return_value=1):
            with patch('streamlit.title'):
                with patch('streamlit.subheader'):
                    with patch('streamlit.write'):
                        with patch('streamlit.expander'):
                            recommandation_page(sample_recipes_df)
