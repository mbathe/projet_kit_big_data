import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class Heatmap(Graphique):
    """
    Classe pour créer et afficher une carte thermique (Heatmap) en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    une carte thermique basée sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données à visualiser.
        x (str): Le nom de la colonne pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne pour les valeurs de l'axe des y.
        z (str): Le nom de la colonne pour les valeurs de l'axe des z (représentant l'intensité des couleurs).
        height (int, optional): La hauteur de la carte thermique en pixels. Par défaut à 400.

    Attributes:
        data (pandas.DataFrame): Le jeu de données à visualiser.
        x (str): Le nom de la colonne pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne pour les valeurs de l'axe des y.
        z (str): Le nom de la colonne pour les valeurs de l'axe des z.
        height (int): La hauteur de la carte thermique en pixels.
    """

    def __init__(self, data, x, y, z, height=400):
        """
        Initialise un objet Heatmap.

        Args:
            data (pandas.DataFrame): Le jeu de données à visualiser.
            x (str): Le nom de la colonne pour les valeurs de l'axe des x.
            y (str): Le nom de la colonne pour les valeurs de l'axe des y.
            z (str): Le nom de la colonne pour les valeurs de l'axe des z (représentant l'intensité des couleurs).
            height (int, optional): La hauteur de la carte thermique en pixels. Par défaut à 400.

        Raises:
            ValueError: Si les colonnes spécifiées n'existent pas dans les données.
        """
        if not all(col in data.columns for col in [x, y, z]):
            raise ValueError("Les colonnes spécifiées n'existent pas dans les données")
        super().__init__(data)
        self.x = x
        self.y = y
        self.z = z
        self.height = height

    def afficher(self):
        """
        Affiche la carte thermique en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère la carte thermique avec Plotly Express en utilisant les attributs
        `x`, `y`, `z` et `height`, puis l'affiche dans l'application Streamlit avec une mise en page personnalisée.
        """
        fig = px.density_heatmap(
            self.data,
            x=self.x,
            y=self.y,
            z=self.z,
            nbinsx=20,
            nbinsy=20,
            height=self.height,
            color_continuous_scale='Viridis',
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=30, r=0, t=20, b=30),
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
            coloraxis_colorbar=dict(
                tickfont=dict(color='black'),
                titlefont=dict(color='black'),
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
