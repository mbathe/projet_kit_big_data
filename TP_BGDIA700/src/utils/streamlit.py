import streamlit as st
from TP_BGDIA700.src.config import Config
import pandas as pd

config = Config()
st.title(config.title)
st.sidebar.info(config.sidebar_info)

"""
# My first app
Here's our first attempt at using data to create a table:
"""


df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
})

df
