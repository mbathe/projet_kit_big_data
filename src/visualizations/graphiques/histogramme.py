from src.visualizations.graphique import Graphique
import plotly.graph_objects as go
import streamlit as st

class Histogramme(Graphique):
    """
    Classe pour créer et afficher un histogramme en utilisant Plotly.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Graph Objects pour générer
    un histogramme basé sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer l'histogramme.
        x (str): Le nom de la colonne à analyser pour l'axe des x.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
        bin_size (float, optional): La taille des bins pour l'histogramme. Par défaut est None.
        bar_color (str, optional): La couleur des barres de l'histogramme. Par défaut 'rgb(100, 149, 237)'.
        line_color (str, optional): La couleur des lignes autour des barres. Par défaut 'rgb(8,48,107)'.

    Attributes:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer l'histogramme.
        x (str): Le nom de la colonne à analyser pour l'axe des x.
        height (int): La hauteur du graphique en pixels.
        bin_size (float or None): La taille des bins pour l'histogramme.
        bar_color (str): La couleur des barres de l'histogramme.
        line_color (str): La couleur des lignes autour des barres.
    """

    def __init__(self, data, x, height=400, bin_size=None, bar_color='rgb(100, 149, 237)', line_color='rgb(8,48,107)'):
        """
        Initialise un objet Histogramme.

        Args:
            data (pandas.DataFrame): Le jeu de données utilisé pour créer l'histogramme.
            x (str): Le nom de la colonne à analyser pour l'axe des x.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
            bin_size (float, optional): La taille des bins pour l'histogramme. Par défaut est None.
            bar_color (str, optional): La couleur des barres de l'histogramme. Par défaut 'rgb(100, 149, 237)'.
            line_color (str, optional): La couleur des lignes autour des barres. Par défaut 'rgb(8,48,107)'.
        """
        super().__init__(data)
        self.x = x
        self.height = height
        self.bin_size = bin_size
        self.bar_color = bar_color
        self.line_color = line_color

    def afficher(self, key=None):
        """
        Affiche l'histogramme en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère l'histogramme avec Plotly Graph Objects en utilisant les attributs
        `x`, `height`, `bin_size`, `bar_color` et `line_color`, puis l'affiche dans l'application
        Streamlit avec une mise en page personnalisée.

        Args:
            key (str, optional): Clé unique pour le graphique dans Streamlit. Par défaut est None.
        """
        fig = go.Figure()

        # Ajout de l'histogramme
        fig.add_trace(go.Histogram(
            x=self.data[self.x],
            xbins=dict(size=self.bin_size) if self.bin_size else None,
            marker=dict(
                color=self.bar_color,
                line=dict(color=self.line_color, width=1),
            ),
            hovertemplate='Intervalle: %{x}<br>Nombre: %{y}',
        ))

        # Mise à jour de la mise en page
        fig.update_layout(
            height=self.height,
            bargap=0.1,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=30, t=30, b=30),
            xaxis=dict(
                showgrid=False,
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

        st.plotly_chart(fig, use_container_width=True, key=key)
