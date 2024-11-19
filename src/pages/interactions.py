import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
from pygwalker.api.streamlit import StreamlitRenderer

path = Path(__file__).parent / "../../data/dataset/RAW_interactions.csv"
st.set_page_config(
    page_title="INTERACTIONS_PAGE",
    layout="wide"
)
st.subheader("INTERACTIONS")


df = pd.read_csv(path)

# Cleaning

# df.columns[df.isnull().any()]

# Visualisation

# pyg_app = StreamlitRenderer(df)

# pyg_app.explorer()

# Inspect Nutrition ratings
