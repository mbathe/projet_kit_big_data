import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import BoxPlot

@pytest.fixture
def sample_data():
    """Fixture pour fournir des données d'exemple."""
    data = pd.DataFrame({
        'Category': ['A', 'B', 'A', 'B'],
        'Value': [10, 20, 15, 25]
    })
    return data

def test_boxplot_initialization(sample_data):
    """Test l'initialisation de la classe BoxPlot."""
    box_plot = BoxPlot(data=sample_data, x='Category', y='Value', height=500)
    assert box_plot.data.equals(sample_data), "Les données ne sont pas correctement initialisées."
    assert box_plot.x == 'Category', "L'attribut x n'est pas correctement initialisé."
    assert box_plot.y == 'Value', "L'attribut y n'est pas correctement initialisé."
    assert box_plot.height == 500, "L'attribut height n'est pas correctement initialisé."

@patch('src.visualizations.graphiques.st.plotly_chart')
def test_boxplot_afficher(mock_plotly_chart, sample_data):
    """Test la méthode afficher de la classe BoxPlot."""
    box_plot = BoxPlot(data=sample_data, x='Category', y='Value', height=500)
    box_plot.afficher()

    # Vérifie que plotly_chart a été appelé une fois
    assert mock_plotly_chart.called, "plotly_chart n'a pas été appelé."
    assert mock_plotly_chart.call_count == 1, "plotly_chart a été appelé plus d'une fois."

    # Récupère la figure passée à plotly_chart
    fig = mock_plotly_chart.call_args[0][0]

    # Vérifie que fig est une instance de plotly.graph_objects.Figure
    assert hasattr(fig, 'data'), "La figure Plotly ne contient pas de données."
    assert fig.layout.height == 500, "La hauteur de la figure n'est pas correctement définie."

    # Vérifie les mises à jour du layout
    layout = fig.layout
    assert layout.plot_bgcolor == 'white', "La couleur de fond du plot n'est pas 'white'."
    assert layout.paper_bgcolor == 'white', "La couleur de fond du papier n'est pas 'white'."
    assert layout.margin.l == 30, "La marge gauche n'est pas 30."
    assert layout.margin.r == 30, "La marge droite n'est pas 30."
    assert layout.margin.t == 30, "La marge supérieure n'est pas 30."
    assert layout.margin.b == 30, "La marge inférieure n'est pas 30."

    # Vérifie les propriétés des axes x et y
    assert layout.xaxis.showgrid == False, "La grille de l'axe x est affichée."
    assert layout.xaxis.zeroline == False, "La ligne zéro de l'axe x est affichée."
    assert layout.xaxis.showticklabels == True, "Les étiquettes de l'axe x ne sont pas affichées."
    assert layout.xaxis.color == 'black', "La couleur de l'axe x n'est pas 'black'."

    assert layout.yaxis.showgrid == False, "La grille de l'axe y est affichée."
    assert layout.yaxis.zeroline == False, "La ligne zéro de l'axe y est affichée."
    assert layout.yaxis.showticklabels == True, "Les étiquettes de l'axe y ne sont pas affichées."
    assert layout.yaxis.color == 'black', "La couleur de l'axe y n'est pas 'black'."

    # Vérifie les mises à jour des axes
    xaxes = fig.layout.xaxis
    yaxes = fig.layout.yaxis

    assert xaxes.tickfont.color == 'black', "La couleur de la police des ticks de l'axe x n'est pas 'black'."
    assert xaxes.titlefont.color == 'black', "La couleur de la police du titre de l'axe x n'est pas 'black'."
    assert xaxes.automargin == False, "L'automargin de l'axe x est activé."

    assert yaxes.tickfont.color == 'black', "La couleur de la police des ticks de l'axe y n'est pas 'black'."
    assert yaxes.titlefont.color == 'black', "La couleur de la police du titre de l'axe y n'est pas 'black'."
    assert yaxes.automargin == False, "L'automargin de l'axe y est activé."