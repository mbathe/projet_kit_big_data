import streamlit as st

def load_css(path):
    try:
        with open(path) as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Le fichier CSS n'a pas été trouvé : {path}")