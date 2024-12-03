import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class Treemap(Graphique):
    """
    Classe pour créer et afficher une carte arborescente (Treemap) en utilisant Plotly Express.

    Cette classe hérite de la classe de base `Graphique` et utilise Plotly Express pour générer
    une carte arborescente basée sur les données fournies. Elle est conçue pour être affichée
    dans une application Streamlit.

    Args:
        data (pandas.DataFrame): Le jeu de données à visualiser.
        path (List[str]): Liste des noms de colonnes définissant la hiérarchie de la carte arborescente.
        values (str): Le nom de la colonne à utiliser pour les valeurs des segments.
        height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

    Attributes:
        data (pandas.DataFrame): Le jeu de données à visualiser.
        path (List[str]): Liste des noms de colonnes définissant la hiérarchie de la carte arborescente.
        values (str): Le nom de la colonne à utiliser pour les valeurs des segments.
        height (int): La hauteur du graphique en pixels.
    """

    def __init__(self, data, path, values, height=400):
        """
        Initialise un objet Treemap.

        Args:
            data (pandas.DataFrame): Le jeu de données à visualiser.
            path (List[str]): Liste des noms de colonnes définissant la hiérarchie de la carte arborescente.
            values (str): Le nom de la colonne à utiliser pour les valeurs des segments.
            height (int, optional): La hauteur du graphique en pixels. Par défaut à 400.

        Raises:
            KeyError: Si les colonnes spécifiées n'existent pas dans les données.
        """
        # Vérification que les colonnes existent dans le DataFrame
        missing_cols = [col for col in path + [values] if col not in data.columns]
        if missing_cols:
            raise KeyError(f"Les colonnes suivantes sont manquantes dans le DataFrame : {', '.join(missing_cols)}")

        super().__init__(data)
        self.path = path  # Liste des colonnes pour la hiérarchie
        self.values = values
        self.height = height

    def afficher(self):
        """
        Affiche la carte arborescente en utilisant la fonction plotly_chart de Streamlit.

        Cette méthode génère la carte arborescente avec Plotly Express en utilisant les attributs
        `path`, `values` et `height`, puis l'affiche dans l'application Streamlit avec une mise en page personnalisée.
        """
        fig = px.treemap(
            self.data,
            path=self.path,
            values=self.values,
            height=self.height,
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='white',
        )

        # Modification des couleurs des textes et des étiquettes
        fig.update_traces(
            textfont_color='black',
            hoverlabel=dict(font_color='black'),
        )

        st.plotly_chart(fig, use_container_width=True)
