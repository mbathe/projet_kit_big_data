import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class BoxPlot(Graphique):
    """
    Classe pour créer et afficher un diagramme en boîte (Box Plot) en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    un diagramme en boîte basé sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le diagramme en boîte.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str, optional): Le nom de la colonne à utiliser pour les valeurs de l'axe des y. Par défaut est None.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

    Attributes:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le diagramme en boîte.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str or None): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int): La hauteur du graphique en pixels.
    """

    def __init__(self, data, x, y=None, height=400):
        """
        Initialise un objet BoxPlot.

        Args:
            data (pandas.DataFrame): Le jeu de données utilisé pour créer le diagramme en boîte.
            x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
            y (str, optional): Le nom de la colonne à utiliser pour les valeurs de l'axe des y. Par défaut est None.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
        """
        super().__init__(data)
        self.x = x
        self.y = y
        self.height = height

    def afficher(self):
        """
        Affiche le diagramme en boîte en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère le diagramme en boîte avec Plotly Express en utilisant les attributs
        `x`, `y` et `height`, puis l'affiche dans l'application Streamlit avec une mise en page personnalisée.
        """
        fig = px.box(
            self.data,
            x=self.x,
            y=self.y,
            height=self.height,
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=30, r=30, t=30, b=30),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                color='black',
                title='',
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                color='black',
                title='',
            ),
        )

        fig.update_xaxes(
            tickfont=dict(color='black'),
            title_font=dict(color='black'),
            automargin=False,
        )
        fig.update_yaxes(
            tickfont=dict(color='black'),
            title_font=dict(color='black'),
            automargin=False,
        )

        st.plotly_chart(fig, use_container_width=True)
