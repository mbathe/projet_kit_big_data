import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class ScatterPlot(Graphique):
    def __init__(self, data, x, y, height=400):
        super().__init__(data)
        
        # Vérification que les colonnes existent dans le DataFrame
        missing_cols = [col for col in [x, y] if col not in data.columns]
        if missing_cols:
            raise KeyError(f"Les colonnes suivantes sont manquantes dans le DataFrame : {', '.join(missing_cols)}")


        self.x = x
        self.y = y
        self.height = height

    def afficher(self):
        fig = px.scatter(
            self.data,
            x=self.x,
            y=self.y,
            height=self.height,
        )

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
