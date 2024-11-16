import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class Donut(Graphique):
    def __init__(self, data, names, values, height=400):
        super().__init__(data)
        self.names = names
        self.values = values
        self.height = height

    def afficher(self):
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
