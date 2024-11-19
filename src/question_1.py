import numpy as np
import matplotlib.pylab as plt
from src.utils.helper_data import load_dataset
import os

dataframes = load_dataset(os.getenv("DIR_DATASET"), all_contents=True)
interactions_test = dataframes["interactions_test"]
interaction_train = dataframes["interactions_train"]
interactions_validation = dataframes["interactions_validation"]
pp_recipes = dataframes["PP_recipes"]
pp_users = dataframes["PP_users"]
raw_interactions = dataframes["RAW_interactions"]
raw_recipes = dataframes["RAW_recipes"]
