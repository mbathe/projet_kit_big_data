import streamlit as st
import numpy as np
import pandas as pd


# Ajouter un sélecteur pour naviguer entre les pages
option = st.selectbox("Sélectionnez une page", [
                      "Accueil", "Analyse", "Paramètres"])

# Afficher le contenu en fonction de l'option sélectionnée
if option == "Accueil":
    st.title("Page d'accueil")
    st.write("Bienvenue sur la page d'accueil.")

elif option == "Analyse":
    st.title("Page d'analyse")
    st.write("Analyse des données ici.")

elif option == "Paramètres":
    st.title("Paramètres")
    st.write("Options de configuration.")
