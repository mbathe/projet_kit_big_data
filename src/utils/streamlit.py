import streamlit as st
from src.config import Config
config = Config()
st.title(config.title)
st.sidebar.info(config.sidebar_info)


