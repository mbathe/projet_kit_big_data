import os
# from src.zone_sacha.app import *
from dotenv import load_dotenv
import sys

# import streamlit as st
# from PIL import Image
# import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    print('APPLICATION STARTED...')
    # st.set_page_config(page_title="Big Data", page_icon=":bar_chart:", layout="wide")

# path_to_css = 'src/css_pages/main.css'

# def load_css(path_to_css):
#     with open(path_to_css) as f:
#         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# load_css(path_to_css)

# # Préparation de l'image en base64
# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# image_base64 = get_base64_of_bin_file('src/zone_sacha/logo_telecom.png')

# # Affichage du contenu centré
# st.markdown(f"""
# <div class="center-content">
#     <h1>Projet Big Data</h1>
# </div>

# <img src="data:image/png;base64,{image_base64}" class="bottom-right-image">
# <div class="footer"><p>© 2023 Big Data. Tous droits réservés.</p></div>

# """, unsafe_allow_html=True)

