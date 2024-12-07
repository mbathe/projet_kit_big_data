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
    Charge un jeu de données à partir d'un répertoire contenant des fichiers CSV ou d'un seul fichier CSV.

    Paramètres :
    dir_name (str) : Le chemin d'accès au répertoire contenant les fichiers CSV ou le chemin d'accès à un seul fichier CSV.
    all_contents (bool, optionnel) : Si True, tous les fichiers CSV du répertoire sont chargés. Si False, seul le fichier spécifié est chargé. La valeur par défaut est True.

    Retourne :
    dict : Un dictionnaire dont les clés sont les noms de fichiers (sans les extensions) et les valeurs sont des DataFrames pandas contenant les données chargées.
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
