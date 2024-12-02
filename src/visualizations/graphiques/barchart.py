import streamlit as st
from src.visualizations.graphique import Graphique
import plotly.express as px

class BarChart(Graphique):
    """
    A class to create and display a bar chart using Plotly Express.

    Attributes
    ----------
    data : pandas.DataFrame
        The dataset to be used for creating the bar chart.
    x : str
        The column name to be used as the x-axis values.
    y : str
        The column name to be used as the y-axis values.
    height : int, optional
        The height of the bar chart in pixels. Default is 400.

    Methods
    -------
    afficher()
        Displays the bar chart using Streamlit's plotly_chart function.
    """
    def __init__(self, data, x, y, height=400):
        """
        Initializes a BarChart object.

        Parameters
        ----------
        data : pandas.DataFrame
            The dataset to be used for creating the bar chart.
        x : str
            The column name to be used as the x-axis values.
        y : str
            The column name to be used as the y-axis values.
        height : int, optional
            The height of the bar chart in pixels. Default is 400.
        """
        super().__init__(data)
        self.x = x
        self.y = y
        self.height = height
    
    def afficher(self):
        """
        Displays the bar chart using Streamlit's plotly_chart function.
        """
        fig = px.bar(self.data, x=self.x, y=self.y, height=self.height)

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=30, r=0, t=20, b=30),
            xaxis=dict(color='black'),
            yaxis=dict(color='black'),
        )

        st.plotly_chart(fig, use_container_width=True)

