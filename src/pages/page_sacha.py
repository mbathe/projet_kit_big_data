import streamlit as st
import plotly.express as px

from src.visualizations.graphiques import (
    Histogramme,
    BoxPlot,
    ScatterPlot,
    Donut,
    LineChart,
    Heatmap,
    )

from src.visualizations import Grille, load_css





if __name__ == "__main__":
    # Configuration de la page pour une largeur maximale
    st.set_page_config(layout="wide")

# Chargement du CSS personnalisé
path_to_css = 'src/css_pages/page_sacha.css'
load_css(path_to_css)

# Chargement des données exemple
df = px.data.tips()

# Importation du dataset gapminder
df_gapminder = px.data.gapminder()
df_france = df_gapminder[df_gapminder['country'] == 'France']

# Création des graphiques en dur avec des hauteurs spécifiques
graphique1 = Histogramme(df, x='total_bill', height=300, bin_size=5)
# graphique2 = Histogramme(df, x='tip', height=300)
graphique2 = BoxPlot(df, x='day', y='total_bill', height=300)
# graphique2 = BarChart(df, x='day', y='total_bill', height=300)

graphique3 = ScatterPlot(df, x='total_bill', y='tip', height=300)

graphique4 = Donut(df, names='day', values='total_bill', height=300)
graphique5 = LineChart(df_france, x='year', y='lifeExp', height=300)
# graphique6 = Donut(df, names='smoker', values='tip', height=300)
graphique6 = Heatmap(df, x='total_bill', y='tip', z='size', height=300)
# graphique6 = Treemap(df, path=['day', 'time'], values='total_bill', height=300)

# Liste des graphiques à afficher
graphiques = [
        {
            "titre": "",
            "graphique": graphique1,
        },
        {
            "titre": "",
            "graphique": graphique2,
        },
        {
            "titre": "",
            "graphique": graphique3,
        },
         {
            "titre": "",
            "graphique": graphique4,
        },
        {
            "titre": "",
            "graphique": graphique5,
        },
        {
            "titre": "",
            "graphique": graphique6,
        },
              ]

# Définition de la grille (2 lignes, 2 colonnes)
nb_lignes = 2
nb_colonnes = 3
largeurs_colonnes = [0.7, 1+0.3,1]  # Les poids relatifs des colonnes

grille = Grille(nb_lignes, nb_colonnes, largeurs_colonnes)
grille.afficher(graphiques)