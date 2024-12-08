import pytest
# Assurez-vous que le module est importé correctement
# Assurez-vous que le module est importé correctement
from src.process.recipes import Recipe,  NutritionStats, TemporalStats, ComplexityStats, ContributorStats, TagStats
import pandas as pd
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from pymongo.errors import ServerSelectionTimeoutError
import logging
import os
from typing import (
    Any, Dict, List, Union, TypedDict
)


# Fixture pour initialiser le DataFrame de recettes


@pytest.fixture
def recipes_df():
    data = {
        "name": [
            "arriba baked winter squash mexican style",
            "a bit different breakfast pizza",
            "all in the kitchen chili",
            "alouette potatoes",
            "amish tomato ketchup for canning"
        ],
        "id": [137739, 31490, 112140, 59389, 44061],
        "minutes": [55, 30, 130, 45, 190],
        "contributor_id": [47892, 26278, 196586, 68585, 41706],
        "submitted": [
            "2005-09-16T00:00:00.000",
            "2002-06-17T00:00:00.000",
            "2005-02-25T00:00:00.000",
            "2003-04-14T00:00:00.000",
            "2002-10-25T00:00:00.000"
        ],
        "tags": [
            "['60-minutes-or-less', 'time-to-make', 'course', 'main-ingredient', 'cuisine', 'preparation', 'occasion', 'north-american', 'side-dishes', 'vegetables', 'mexican', 'easy', 'fall', 'holiday-event', 'vegetarian', 'winter', 'dietary', 'christmas', 'seasonal', 'squash']",
            "['30-minutes-or-less', 'time-to-make', 'course', 'main-ingredient', 'cuisine', 'preparation', 'occasion', 'north-american', 'breakfast', 'main-dish', 'pork', 'american', 'oven', 'easy', 'kid-friendly', 'pizza', 'dietary', 'northeastern-united-states', 'meat', 'equipment']",
            "['time-to-make', 'course', 'preparation', 'main-dish', 'chili', 'crock-pot-slow-cooker', 'dietary', 'equipment', '4-hours-or-less']",
            "['60-minutes-or-less', 'time-to-make', 'course', 'main-ingredient', 'preparation', 'occasion', 'side-dishes', 'eggs-dairy', 'potatoes', 'vegetables', 'oven', 'easy', 'dinner-party', 'holiday-event', 'easter', 'cheese', 'stove-top', 'dietary', 'christmas', 'new-years', 'thanksgiving', 'independence-day', 'st-patricks-day', 'valentines-day', 'inexpensive', 'brunch', 'superbowl', 'equipment', 'presentation', 'served-hot']",
            "['weeknight', 'time-to-make', 'course', 'main-ingredient', 'cuisine', 'preparation', 'occasion', 'north-american', 'canning', 'condiments-etc', 'vegetables', 'american', 'heirloom-historical', 'holiday-event', 'vegetarian', 'dietary', 'amish-mennonite', 'northeastern-united-states', 'number-of-servings', 'technique', '4-hours-or-less']"
        ],
        "nutrition": [
            "[51.5, 0.0, 13.0, 0.0, 2.0, 0.0, 4.0]",
            "[173.4, 18.0, 0.0, 17.0, 22.0, 35.0, 1.0]",
            "[269.8, 22.0, 32.0, 48.0, 39.0, 27.0, 5.0]",
            "[368.1, 17.0, 10.0, 2.0, 14.0, 8.0, 20.0]",
            "[352.9, 1.0, 337.0, 23.0, 3.0, 0.0, 28.0]"
        ],
        "n_steps": [11, 9, 6, 11, 5],
        "steps": [
            "['make a choice and proceed with recipe', 'depending on size of squash , cut into half or fourths', 'remove seeds', 'for spicy squash , drizzle olive oil or melted butter over each cut squash piece', 'season with mexican seasoning mix ii', 'for sweet squash , drizzle melted honey , butter , grated piloncillo over each cut squash piece', 'season with sweet mexican spice mix', 'bake at 350 degrees , again depending on size , for 40 minutes up to an hour , until a fork can easily pierce the skin', 'be careful not to burn the squash especially if you opt to use sugar or butter', 'if you feel more comfortable , cover the squash with aluminum foil the first half hour , give or take , of baking', 'if desired , season with salt']",
            "['preheat oven to 425 degrees f', 'press dough into the bottom and sides of a 12 inch pizza pan', 'bake for 5 minutes until set but not browned', 'cut sausage into small pieces', 'whisk eggs and milk in a bowl until frothy', 'spoon sausage over baked crust and sprinkle with cheese', 'pour egg mixture slowly over sausage and cheese', 's& p to taste', 'bake 15-20 minutes or until eggs are set and crust is brown']",
            "['brown ground beef in large pot', 'add chopped onions to ground beef when almost brown and sautee until wilted', 'add all other ingredients', 'add kidney beans if you like beans in your chili', 'cook in slow cooker on high for 2-3 hours or 6-8 hours on low', 'serve with cold clean lettuce and shredded cheese']",
            "['place potatoes in a large pot of lightly salted water and bring to a gentle boil', 'cook until potatoes are just tender', 'drain', 'place potatoes in a large bowl and add all ingredients except the\"\"alouette\"\"', 'mix well and transfer to a buttered 8x8 inch glass baking dish with 2 inch sides', 'press the potatoes with a spatula to make top as flat as possible', 'set aside for 2 hours at room temperature', 'preheat oven to 350^f', 'spread\"\"alouette\"\" evenly over potatoes and bake 15 minutes', 'divide between plates', 'garnish with finely diced red and yellow bell peppers']",
            "['mix all ingredients& boil for 2 1 / 2 hours , or until thick', 'pour into jars', \"i use'old' glass ketchup bottles\", \"it is not necessary for these to'seal\", \"'my amish mother-in-law has been making this her entire life , and has never used a'sealed' jar for this recipe , and it's always been great !\"]"
        ],
        "description": [
            "autumn is my favorite time of year to cook! this recipe can be prepared either spicy or sweet, your choice! two of my posted mexican-inspired seasoning mix recipes are offered as suggestions.",
            "this recipe calls for the crust to be prebaked a bit before adding ingredients. feel free to change sausage to ham or bacon. this warms well in the microwave for those late risers.",
            "this ind this one in a cookbook. it is truly an original.",
            "this rything is done in advance. the times do not reflect the standing time of the potatoes.",
            "my dh's  but now my ds's also prefer this type of ketchup. enjoy!"
        ],
        "ingredients": [
            "['winter squash', 'mexican seasoning', 'olive oil', 'salt']",
            "['prepared pizza crust', 'sausage patty', 'eggs', 'milk']",
            "['ground beef', 'yellow onions', 'diced tomatoes' ]",
            "['spreadable cheese with garlic and herbs','data']",
            "['tomato juice', 'apple cider vinegar' ]"
        ],
        "n_ingredients": [7, 6, 13, 11, 8]
    }

    # Convertir les dates en objets datetime
    data["submitted"] = pd.to_datetime(data["submitted"])

    # Créer le DataFrame
    return pd.DataFrame(data)

# Test pour vérifier l'initialisation de la session state


@pytest.fixture
def sample_dataframe():
    """Créer un DataFrame de test avec des données de recettes"""
    data = {
        'name': ['Arriba Baked Winter Squash', 'A Bit Different Breakfast Pizza',
                 'All in the Kitchen Chili', 'Alouette Potatoes'],
        'id': [137739, 31490, 112140, 59389],
        'minutes': [55, 30, 130, 45],
        'contributor_id': [47892, 26278, 196586, 68585],
        'submitted': [
            datetime(2005, 9, 16),
            datetime(2002, 6, 17),
            datetime(2005, 2, 25),
            datetime(2003, 4, 14)
        ],
        'tags': [
            ['60-minutes-or-less', 'time-to-make', 'squash'],
            ['30-minutes-or-less'],
            ['time-to-make'],
            ['60-minutes-or-less']
        ],
        'nutrition': [
            [100, 10, 5, 200, 15, 3, 20],
            [150, 15, 8, 250, 20, 5, 25],
            [200, 20, 10, 300, 25, 7, 30],
            [120, 12, 6, 220, 18, 4, 22]
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def recipe_instance(sample_dataframe):
    """Créer une instance de Recipe avec un DataFrame de test"""
    with patch('streamlit.session_state', MagicMock()) as mock_session_state:
        mock_session_state.data = sample_dataframe
        recipe = Recipe(name="test_recipes",
                        date_start=datetime(2002, 1, 1),
                        date_end=datetime(2005, 12, 31))
    return recipe


def test_recipe_initialization(recipe_instance):
    """Test l'initialisation de la classe Recipe"""
    assert hasattr(recipe_instance, 'st')
    assert hasattr(recipe_instance, 'date_start')
    assert hasattr(recipe_instance, 'date_end')
    assert hasattr(recipe_instance, 'annomalis')
    assert hasattr(recipe_instance, 'columns')


def test_detect_dataframe_anomalies(recipe_instance):
    """Test la méthode de détection des anomalies"""
    anomalies = recipe_instance.annomalis
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies


def test_ensure_datetime():
    """Test la méthode _ensure_datetime"""
    recipe = Recipe()
    dt_obj = datetime(2023, 1, 1)
    date_obj = date(2023, 1, 1)

    assert recipe._ensure_datetime(dt_obj) == dt_obj
    assert recipe._ensure_datetime(date_obj) == datetime(2023, 1, 1, 0, 0)

    with pytest.raises(TypeError):
        recipe._ensure_datetime("invalid")


def test_initialize_session_state_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    recipe.initialize_session_state(
        datetime(2000, 1, 1), datetime(2005, 12, 31))
    assert recipe.st.session_state.start_date == datetime(2000, 1, 1)
    assert recipe.st.session_state.end_date == datetime(2005, 12, 31)
    assert not recipe.st.session_state.data.empty

# Test pour vérifier la détection des anomalies


def test_detect_dataframe_anomalies_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    anomalies = recipe.detect_dataframe_anomalies()
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies

# Test pour vérifier le nettoyage du DataFrame


def test_clean_dataframe_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    recipe.clean_dataframe(cleaning_method='std', threshold=3.0)
    assert not recipe.st.session_state.data.empty

# Test pour vérifier l'analyse de la nutrition


def test_analyze_nutrition_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    nutrition_stats = recipe.analyze_nutrition()
    assert 'calories' in nutrition_stats
    assert 'total_fat' in nutrition_stats
    assert 'sugar' in nutrition_stats
    assert 'sodium' in nutrition_stats
    assert 'protein' in nutrition_stats
    assert 'saturated_fat' in nutrition_stats
    assert 'carbohydrates' in nutrition_stats

# Test pour vérifier l'analyse de la distribution temporelle


def test_analyze_temporal_distribution_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    temporal_stats = recipe.analyze_temporal_distribution(
        datetime(2000, 1, 1), datetime(2005, 12, 31))
    assert 'date_min' in temporal_stats
    assert 'date_max' in temporal_stats
    assert 'total_days' in temporal_stats
    assert 'submissions_per_year' in temporal_stats
    assert 'submissions_per_month' in temporal_stats
    assert 'submissions_per_weekday' in temporal_stats

# Test pour vérifier l'analyse des tags


def test_analyze_tags_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    tag_stats = recipe.analyze_tags()
    assert 'total_unique_tags' in tag_stats
    assert 'most_common_tags' in tag_stats
    assert 'tags_per_recipe' in tag_stats

# Test pour vérifier l'analyse des contributeurs


def test_analyze_contributors_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    contributor_stats = recipe.analyze_contributors()
    assert 'total_contributors' in contributor_stats
    assert 'contributions_per_user' in contributor_stats
    assert 'top_contributors' in contributor_stats

# Test pour vérifier l'analyse de la complexité des recettes


def test_analyze_recipe_complexity_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    complexity_stats = recipe.analyze_recipe_complexity()
    assert 'steps_stats' in complexity_stats
    assert 'time_stats' in complexity_stats

# Test pour vérifier l'analyse complète du jeu de données de recettes


def test_analyze_recipe_dataset_2(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    analysis = recipe.analyze_recipe_dataset()
    assert 'general_stats' in analysis
    assert 'temporal_analysis' in analysis
    assert 'complexity_analysis' in analysis
    assert 'nutrition_analysis' in analysis
    assert 'tag_analysis' in analysis
    assert 'contributor_analysis' in analysis


# Test pour vérifier la détection des anomalies
def test_detect_dataframe_anomalies(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    anomalies = recipe.detect_dataframe_anomalies()
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies

# Test pour vérifier le nettoyage du DataFrame


def test_clean_dataframe(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    recipe.clean_dataframe(cleaning_method='std', threshold=3.0)
    assert not recipe.st.session_state.data.empty

# Test pour vérifier l'analyse de la nutrition


def test_analyze_nutrition(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    nutrition_stats = recipe.analyze_nutrition()
    assert 'calories' in nutrition_stats
    assert 'total_fat' in nutrition_stats
    assert 'sugar' in nutrition_stats
    assert 'sodium' in nutrition_stats
    assert 'protein' in nutrition_stats
    assert 'saturated_fat' in nutrition_stats
    assert 'carbohydrates' in nutrition_stats

# Test pour vérifier l'analyse de la distribution temporelle


def test_analyze_temporal_distribution(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    temporal_stats = recipe.analyze_temporal_distribution(
        datetime(2000, 1, 1), datetime(2005, 12, 31))
    assert 'date_min' in temporal_stats
    assert 'date_max' in temporal_stats
    assert 'total_days' in temporal_stats
    assert 'submissions_per_year' in temporal_stats
    assert 'submissions_per_month' in temporal_stats
    assert 'submissions_per_weekday' in temporal_stats

# Test pour vérifier l'analyse des tags


def test_analyze_tags(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    tag_stats = recipe.analyze_tags()
    assert 'total_unique_tags' in tag_stats
    assert 'most_common_tags' in tag_stats
    assert 'tags_per_recipe' in tag_stats

# Test pour vérifier l'analyse des contributeurs


def test_analyze_contributors(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    contributor_stats = recipe.analyze_contributors()
    assert 'total_contributors' in contributor_stats
    assert 'contributions_per_user' in contributor_stats
    assert 'top_contributors' in contributor_stats

# Test pour vérifier l'analyse de la complexité des recettes


def test_analyze_recipe_complexity(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    complexity_stats = recipe.analyze_recipe_complexity()
    assert 'steps_stats' in complexity_stats
    assert 'time_stats' in complexity_stats

# Test pour vérifier l'analyse complète du jeu de données de recettes


def test_analyze_recipe_dataset(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    analysis = recipe.analyze_recipe_dataset()
    assert 'general_stats' in analysis
    assert 'temporal_analysis' in analysis
    assert 'complexity_analysis' in analysis
    assert 'nutrition_analysis' in analysis
    assert 'tag_analysis' in analysis
    assert 'contributor_analysis' in analysis

# Test pour vérifier la conversion en datetime


def test_ensure_datetime():
    recipe = Recipe()
    assert recipe._ensure_datetime(
        datetime(2000, 1, 1)) == datetime(2000, 1, 1)
    assert recipe._ensure_datetime(datetime.now().date()) == datetime.combine(
        datetime.now().date(), datetime.min.time())
    with pytest.raises(TypeError):
        recipe._ensure_datetime("invalid_date")

# Test pour vérifier la conversion en date


# Test pour vérifier la récupération des données depuis MongoDB


def test_fetch_data_from_mongodb(monkeypatch, recipes_df):
    recipe = Recipe()
    # Mock de la méthode fetch_data_from_mongodb

    def mock_fetch_data_from_mongodb(connection_string, database_name, collection_name, start_date, end_date):
        return recipes_df

    monkeypatch.setattr(recipe, 'fetch_data_from_mongodb',
                        mock_fetch_data_from_mongodb)
    data = recipe.fetch_data_from_mongodb(
        "mock_connection_string", "mock_database", "mock_collection", datetime(2000, 1, 1), datetime(2005, 12, 31))
    assert not data.empty
    assert data.equals(recipes_df)

# Test pour vérifier l'analyse complète du jeu de données de recettes avec des dates spécifiques


def test_analyze_recipe_dataset_with_specific_dates(recipes_df):
    recipe = Recipe(date_start=datetime(2000, 1, 1),
                    date_end=datetime(2005, 12, 31))
    recipe.st.session_state.data = recipes_df
    analysis = recipe.analyze_recipe_dataset()
    assert 'general_stats' in analysis
    assert 'temporal_analysis' in analysis
    assert 'complexity_analysis' in analysis
    assert 'nutrition_analysis' in analysis
    assert 'tag_analysis' in analysis
    assert 'contributor_analysis' in analysis

# Test pour vérifier l'initialisation avec des dates spécifiques


def test_initialize_with_specific_dates(recipes_df):
    recipe = Recipe(date_start=datetime(2000, 1, 1),
                    date_end=datetime(2005, 12, 31))
    recipe.st.session_state.data = recipes_df
    recipe.initialize_session_state(
        datetime(2000, 1, 1), datetime(2005, 12, 31))
    assert recipe.st.session_state.start_date == datetime(2000, 1, 1)
    assert recipe.st.session_state.end_date == datetime(2005, 12, 31)
    assert not recipe.st.session_state.data.empty

# Test pour vérifier la détection des anomalies avec des seuils spécifiques


def test_detect_dataframe_anomalies_with_specific_thresholds(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    anomalies = recipe.detect_dataframe_anomalies(
        std_threshold=2.0, z_score_threshold=2.0)
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies

# Test pour vérifier le nettoyage du DataFrame avec des seuils spécifiques


def test_clean_dataframe_with_specific_thresholds(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    recipe.clean_dataframe(cleaning_method='zscore', threshold=2.0)
    assert not recipe.st.session_state.data.empty


def test_ensure_datetime_invalid_values():
    recipe = Recipe()
    with pytest.raises(TypeError):
        recipe._ensure_datetime("invalid_date")
    with pytest.raises(TypeError):
        recipe._ensure_datetime(12345)

# Test pour vérifier la méthode `_ensure_date` avec des valeurs invalides


def test_ensure_date_invalid_values():
    recipe = Recipe()
    with pytest.raises(TypeError):
        recipe._ensure_date("invalid_date")
    with pytest.raises(TypeError):
        recipe._ensure_date(12345)

# Test pour vérifier la méthode `fetch_data_from_mongodb` avec des erreurs de connexion


def test_fetch_data_from_mongodb_connection_error(monkeypatch):
    recipe = Recipe()
    # Mock de la méthode fetch_data_from_mongodb pour simuler une erreur de connexion

    def mock_fetch_data_from_mongodb(connection_string, database_name, collection_name, start_date, end_date):
        raise ServerSelectionTimeoutError("Could not connect to MongoDB")

    monkeypatch.setattr(recipe, 'fetch_data_from_mongodb',
                        mock_fetch_data_from_mongodb)
    with pytest.raises(ServerSelectionTimeoutError):
        recipe.fetch_data_from_mongodb("mock_connection_string", "mock_database",
                                       "mock_collection", datetime(2000, 1, 1), datetime(2005, 12, 31))

# Test pour vérifier la méthode `analyze_nutrition` avec des données manquantes


def test_analyze_nutrition_missing_data(recipes_df):
    recipe = Recipe()
    recipes_df.loc[0, 'nutrition'] = None
    recipe.st.session_state.data = recipes_df
    with pytest.raises(Exception):
        recipe.analyze_nutrition()

# Test pour vérifier la méthode `analyze_temporal_distribution` avec des dates en dehors de la plage


def test_analyze_tags_malformed_tags(recipes_df):
    recipe = Recipe()
    recipes_df.loc[0, 'tags'] = "invalid_tag_format"
    recipe.st.session_state.data = recipes_df
    with pytest.raises(Exception):
        recipe.analyze_tags()

# Test pour vérifier la méthode `analyze_contributors` avec des contributeurs manquants


def test_initialize_session_state_invalid_dates():
    recipe = Recipe()
    with pytest.raises(TypeError):
        recipe.initialize_session_state(
            "invalid_start_date", datetime(2005, 12, 31))
    with pytest.raises(TypeError):
        recipe.initialize_session_state(
            datetime(2000, 1, 1), "invalid_end_date")

# Test pour vérifier la méthode `detect_dataframe_anomalies` avec des colonnes numériques manquantes


def test_detect_dataframe_anomalies_missing_numeric_columns(recipes_df):
    recipe = Recipe()
    recipes_df.drop(columns=['minutes'], inplace=True)
    recipe.st.session_state.data = recipes_df
    anomalies = recipe.detect_dataframe_anomalies()
    assert 'missing_values' in anomalies
    assert 'std_outliers' in anomalies
    assert 'z_score_outliers' in anomalies
    assert 'column_info' in anomalies
    assert 'data_types' in anomalies


def test_logging_configuration():
    # Configurer le logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

    # Vérifier que le fichier de log est créé
    assert os.path.exists("app.log")


def test_nutrition_stats_type_1(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    nutrition_stats = recipe.analyze_nutrition()
    for key, value in nutrition_stats.items():
        assert isinstance(value['mean'], float)
        assert isinstance(value['median'], float)
        assert isinstance(value['min'], float)
        assert isinstance(value['max'], float)
        assert isinstance(value['quartiles'], dict)
        for quartile_key, quartile_value in value['quartiles'].items():
            assert isinstance(quartile_key, float)
            assert isinstance(quartile_value, float)


def test_temporal_stats_type(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    temporal_stats = recipe.analyze_temporal_distribution(
        datetime(2000, 1, 1), datetime(2005, 12, 31))
    assert isinstance(temporal_stats['date_min'], datetime)
    assert isinstance(temporal_stats['date_max'], datetime)
    assert isinstance(temporal_stats['total_days'], int)
    assert isinstance(temporal_stats['submissions_per_year'], dict)
    assert isinstance(temporal_stats['submissions_per_month'], dict)
    assert isinstance(temporal_stats['submissions_per_weekday'], dict)


def test_contributor_stats_type(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    contributor_stats = recipe.analyze_contributors()
    assert isinstance(contributor_stats['total_contributors'], int)
    assert isinstance(contributor_stats['contributions_per_user'], dict)
    assert isinstance(contributor_stats['top_contributors'], dict)


def test_tag_stats_type(recipes_df):
    recipe = Recipe()
    recipe.st.session_state.data = recipes_df
    tag_stats = recipe.analyze_tags()
    assert isinstance(tag_stats['total_unique_tags'], int)
    assert isinstance(tag_stats['most_common_tags'], dict)
    assert isinstance(tag_stats['tags_per_recipe'], dict)
