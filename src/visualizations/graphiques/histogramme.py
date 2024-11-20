from src.visualizations.graphique import Graphique
import plotly.graph_objects as go
import streamlit as st

class Histogramme(Graphique):
    def __init__(self, data, x, height=400, bin_size=None, bar_color='rgb(100, 149, 237)', line_color='rgb(8,48,107)'):
        """
        Classe pour afficher un histogramme avec Plotly.

        Paramètres :
        - data (pd.DataFrame) : Données source
        - x (str) : Colonne à analyser
        - height (int) : Hauteur du graphique
        - bin_size (float) : Taille des bins
        - bar_color (str) : Couleur des barres
        - line_color (str) : Couleur des lignes autour des barres
        """
        super().__init__(data)
        self.x = x
        self.height = height
        self.bin_size = bin_size
        self.bar_color = bar_color
        self.line_color = line_color

    def afficher(self,key=None):
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

        st.plotly_chart(fig, use_container_width=True,  key=key)
