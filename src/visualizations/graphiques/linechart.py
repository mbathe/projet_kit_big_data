import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class LineChart(Graphique):
    """
    Classe pour créer et afficher un graphique linéaire (Line Chart) en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    un graphique linéaire basé sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique linéaire.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
        line_color (str, optional): La couleur de la ligne du graphique. Par défaut est None.

    Attributes:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique linéaire.
        x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
        y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
        height (int): La hauteur du graphique en pixels.
        line_color (str or None): La couleur de la ligne du graphique.
    """

    def __init__(self, data, x, y, height=400, line_color=None):
        """
        Initialise un objet LineChart.

        Args:
            data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique linéaire.
            x (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des x.
            y (str): Le nom de la colonne à utiliser pour les valeurs de l'axe des y.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
            line_color (str, optional): La couleur de la ligne du graphique. Par défaut est None.

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
        self.line_color = line_color

    def afficher(self):
        """
        Affiche le graphique linéaire en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère le graphique linéaire avec Plotly Express en utilisant les attributs
        `x`, `y`, `height` et `line_color`, puis l'affiche dans l'application Streamlit avec une
        mise en page personnalisée.
        """
        fig = px.line(
            self.data,
            x=self.x,
            y=self.y,
            height=self.height,
        )
        # Appliquer la couleur de la ligne si elle est définie
        if self.line_color:
            fig.update_traces(line=dict(color=self.line_color))

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
