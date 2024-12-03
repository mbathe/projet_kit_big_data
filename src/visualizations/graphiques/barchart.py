import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class BarChart(Graphique):
    """
    Classe pour créer et afficher un graphique à barres en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    un graphique à barres basé sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique à barres.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

    Attributes:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique à barres.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int): La hauteur du graphique en pixels.
    """

    def __init__(self, data, x, y, height=400):
        """
        Initialise un objet BarChart.

        Args:
            data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique à barres.
            x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
            y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
        """
        super().__init__(data)
        self.x = x
        self.y = y
        self.height = height

    def afficher(self):
        """
        Affiche le graphique à barres en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère le graphique à barres avec Plotly Express en utilisant les attributs
        `x`, `y` et `height`, puis l'affiche dans l'application Streamlit avec une mise en page personnalisée.
        """
        fig = px.bar(self.data, x=self.x, y=self.y, height=self.height)

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=30, r=0, t=20, b=30),
            xaxis=dict(color='black'),
            yaxis=dict(color='black'),
        )

        st.plotly_chart(fig, use_container_width=True)
