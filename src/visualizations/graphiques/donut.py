import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class Donut(Graphique):
    """
    Classe pour créer et afficher un graphique en anneau (Donut Chart) en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    un graphique en anneau basé sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique en anneau.
        names (str): Le nom de la colonne à utiliser pour les labels des segments.
        values (str): Le nom de la colonne à utiliser pour les valeurs des segments.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

    Attributes:
        data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique en anneau.
        names (str): Le nom de la colonne à utiliser pour les labels des segments.
        values (str): Le nom de la colonne à utiliser pour les valeurs des segments.
        height (int): La hauteur du graphique en pixels.
    """

    def __init__(self, data, names, values, height=400):
        """
        Initialise un objet Donut.

        Args:
            data (pandas.DataFrame): Le jeu de données utilisé pour créer le graphique en anneau.
            names (str): Le nom de la colonne à utiliser pour les labels des segments.
            values (str): Le nom de la colonne à utiliser pour les valeurs des segments.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.
        """
        super().__init__(data)
        self.names = names
        self.values = values
        self.height = height

    def afficher(self):
        """
        Affiche le graphique en anneau en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère le graphique en anneau avec Plotly Express en utilisant les attributs
        `names`, `values` et `height`, puis l'affiche dans l'application Streamlit avec une mise en page personnalisée.
        """
        # Création du graphique en anneau sans légende et avec hover personnalisé
        fig = px.pie(
            self.data,
            names=self.names,
            values=self.values,
            hole=0.4,
            height=self.height,
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',  # Fond du graphique
            paper_bgcolor='white',  # Fond du conteneur
            margin=dict(l=20, r=20, t=20, b=20),
        )

        # Personnalisation du hover pour afficher le label et le pourcentage
        fig.update_traces(
            hovertemplate='%{percent}',
            textposition='inside',
            textinfo='label',
        )

        st.plotly_chart(fig, use_container_width=True)
