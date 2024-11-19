import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class Treemap(Graphique):
    def __init__(self, data, path, values, height=400):
        super().__init__(data)

        # Vérification que les colonnes existent dans le DataFrame
        missing_cols = [col for col in path + [values] if col not in data.columns]
        if missing_cols:
            raise KeyError(f"Les colonnes suivantes sont manquantes dans le DataFrame : {', '.join(missing_cols)}")


        self.path = path  # Liste des colonnes pour la hiérarchie
        self.values = values
        self.height = height

    def afficher(self):
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

