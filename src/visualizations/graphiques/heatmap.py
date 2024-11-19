import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class Heatmap(Graphique):
    def __init__(self, data, x, y, z, height=400):
        super().__init__(data)
        self.x = x
        self.y = y
        self.z = z
        self.height = height

    def __init__(self, data, x, y, z, height=400):
        """
        Initialize a Heatmap object with the given data and parameters.

        Parameters:
        - data (pandas.DataFrame): The dataset to visualize.
        - x (str): The column name for the x-axis values.
        - y (str): The column name for the y-axis values.
        - z (str): The column name for the z-axis values (representing the color intensity).
        - height (int, optional): The height of the heatmap in pixels. Default is 400.

        Returns:
        - None
        """
        super().__init__(data)
        self.x = x
        self.y = y
        self.z = z
        self.height = height

    def afficher(self):
        fig = px.density_heatmap(
            self.data,
            x=self.x,
            y=self.y,
            z=self.z,
            nbinsx=20,
            nbinsy=20,
            height=self.height,
            color_continuous_scale='Viridis',
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=30, r=0, t=20, b=30),
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
            
            coloraxis_colorbar=dict(
                tickfont=dict(color='black'),
                titlefont=dict(color='black'),
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
