import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class ScatterPlot(Graphique):
    """
    Classe pour créer et afficher un nuage de points (Scatter Plot) en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    un nuage de points basé sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le nuage de points.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

    Attributes:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le nuage de points.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int): La hauteur du graphique en pixels.
    """

    def __init__(self, data, x, y, height=400):
        """
        Initialise un objet ScatterPlot.

        Args:
            data (pandas.DataFrame): Le jeu de données utilisé pour créer le nuage de points.
            x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
            y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

        Raises:
            KeyError: Si les colonnes spécifiées n'existent pas dans les données.
        """
        # Vérification que les colonnes existent dans le DataFrame
        missing_cols = [col for col in [x, y] if col not in data.columns]
        if missing_cols:
            raise KeyError(f"Les colonnes suivantes sont manquantes dans le DataFrame : {', '.join(missing_cols)}")

        super().__init__(data)
        self.x = x
        self.y = y
        self.height = height

    def afficher(self):
        """
        Affiche le nuage de points en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère le nuage de points avec Plotly Express en utilisant les attributs
        `x`, `y` et `height`, puis l'affiche dans l'application Streamlit avec une mise en page personnalisée.
        """
        fig = px.scatter(
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
                showgrid=True,
                zeroline=False,
                showticklabels=True,
                color='black',
                title='',
            ),
            yaxis=dict(
                showgrid=True,
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
