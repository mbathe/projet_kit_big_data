import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px
import plotly.graph_objects as go

class Histogramme(Graphique):
    def __init__(self, data, x, height=400,  bin_size=None):
        super().__init__(data)
        self.x = x
        self.height = height
        self.bin_size = bin_size

    def afficher(self):
        # Création d'un histogramme avec espacement et coins arrondis
        fig = go.Figure()

        # Ajout de l'histogramme avec la taille des bins spécifiée
        fig.add_trace(go.Histogram(
            x=self.data[self.x],
            xbins=dict(
                size=self.bin_size  # Taille des bins
            ) if self.bin_size else None,
            marker=dict(
                color='rgb(100, 149, 237)',  # Couleur des barres
                line=dict(color='rgb(8,48,107)', width=1),
            ),
            hovertemplate='Intervalle: %{x}<br>Nombre: %{y}',
        ))

        # Mise à jour de la mise en page
        fig.update_layout(
            height=self.height,
            bargap=0.1,  # Espace entre les barres (0 à 1)
            plot_bgcolor='white',  # Fond du graphique
            paper_bgcolor='white',  # Fond du conteneur
            margin=dict(l=30, r=30, t=30, b=30),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                color='black',  # Couleur des labels de l'axe X
                title='',  # Suppression du titre de l'axe X
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showticklabels=True,
                color='black',  # Couleur des labels de l'axe Y
                title='',  # Suppression du titre de l'axe Y
            ),

        )

        # Assurer que les ticks sont noirs
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
