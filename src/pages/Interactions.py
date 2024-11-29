import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
from pygwalker.api.streamlit import StreamlitRenderer
import os

path = os.path.join('/home/paul/Cours/BGDIA700/dataset',
                    'RAW_interactions.csv')
st.set_page_config(
    page_title="INTERACTIONS_PAGE",
    layout="wide"
)
st.subheader("INTERACTIONS")


df = pd.read_csv(path)
