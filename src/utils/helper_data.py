import logging
from src.visualizations import load_css
import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@st.cache_data
def load_dataset(dir_name: str, all_contents=True):
    """
    Load a dataset from a directory containing CSV files or a single CSV file.

    Parameters:
    dir_name (str): The directory path containing the CSV files or the path to a single CSV file.
    all_contents (bool, optional): If True, load all CSV files in the directory. If False, load only the specified file. Defaults to True.

    Returns:
    dict: A dictionary where the keys are the file names (without extensions) and the values are pandas DataFrames containing the loaded data.
    """
    dataframes = {}
    if all_contents:
        csv_files = [file for file in os.listdir(
            dir_name) if file.endswith('.csv')]
        for file in csv_files:
            dataframes[os.path.splitext(file)[0]] = pd.read_csv(
                os.path.join(dir_name, file))
        return dataframes

    else:
        file = os.path.basename(dir_name)
        dataframes[os.path.splitext(file)[0]] = pd.read_csv(dir_name)
        return dataframes



@st.cache_data
def load_dataset_from_file(dir_folder, date_start, date_end, is_interactional=False):
    if not is_interactional:
        df = pd.read_csv(dir_folder,
                         parse_dates=['submitted'],
                         chunksize=1000)
        df_filtered = pd.concat(chunk[(chunk['submitted'] >= date_start) &
                                      (chunk['submitted'] <= date_end)]
                                for chunk in df)
        df_filtered = df_filtered.reset_index(drop=True)
        return df_filtered
    else:
        df = pd.read_csv(dir_folder,
                         parse_dates=['date'],
                         chunksize=1000)
        df_filtered = pd.concat(chunk[(chunk['date'] >= date_start) &
                                      (chunk['date'] <= date_end)]
                                for chunk in df)
        df_filtered = df_filtered.reset_index(drop=True)
        return df_filtered


@st.cache_data
def load(css_file):
    try:
        load_css(css_file)
        logging.info(f"CSS loaded from {css_file}")
    except Exception as e:
        logging.error(f"Failed to load CSS from {css_file}: {e}")
        raise Exception(f"Failed to load CSS: {str(e)}")
