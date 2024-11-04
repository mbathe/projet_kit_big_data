import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class BarChart(Graphique):
    def __init__(self, data, x, y, height=400):
        super().__init__(data)
        self.x = x
        self.y = y
        self.height = height

    def afficher(self):
        fig = px.bar(
            self.data,
            x=self.x,
            y=self.y,
            height=self.height,
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=30, r=30, t=30, b=30),
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
        )

        # Assurer que les ticks des axes sont noirs
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
