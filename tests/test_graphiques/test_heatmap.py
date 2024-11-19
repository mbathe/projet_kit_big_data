import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import Heatmap

@pytest.fixture
def sample_data():
    """Fixture pour fournir des données d'exemple."""
    data = pd.DataFrame({
        'X': [1, 2, 3, 4, 5],
        'Y': [10, 20, 30, 40, 50],
        'Z': [100, 200, 300, 400, 500]
    })
    return data

def test_heatmap_initialization(sample_data):
    """Test l'initialisation de la classe Heatmap."""
    heatmap = Heatmap(data=sample_data, x='X', y='Y', z='Z', height=500)
    assert heatmap.data.equals(sample_data), "Les données ne sont pas correctement initialisées."
    assert heatmap.x == 'X', "L'attribut x n'est pas correctement initialisé."
    assert heatmap.y == 'Y', "L'attribut y n'est pas correctement initialisé."
    assert heatmap.z == 'Z', "L'attribut z n'est pas correctement initialisé."
    assert heatmap.height == 500, "L'attribut height n'est pas correctement initialisé."

@patch('src.visualizations.graphiques.st.plotly_chart')
def test_heatmap_afficher(mock_plotly_chart, sample_data):
    """Test la méthode afficher de la classe Heatmap."""
    heatmap = Heatmap(data=sample_data, x='X', y='Y', z='Z', height=500)
    heatmap.afficher()

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
    assert layout.margin.r == 0, "La marge droite n'est pas 0."
    assert layout.margin.t == 20, "La marge supérieure n'est pas 20."
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

    # Vérifie les propriétés de l'échelle de couleurs
    coloraxis = layout.coloraxis.colorbar
    assert coloraxis.tickfont.color == 'black', "La couleur de la police des ticks de la barre de couleur n'est pas 'black'."
    assert coloraxis.titlefont.color == 'black', "La couleur de la police du titre de la barre de couleur n'est pas 'black'."

    # Vérifie les mises à jour des axes
    xaxes = fig.layout.xaxis
    yaxes = fig.layout.yaxis

    assert xaxes.tickfont.color == 'black', "La couleur de la police des ticks de l'axe x n'est pas 'black'."
    assert xaxes.title.font.color == 'black', "La couleur de la police du titre de l'axe x n'est pas 'black'."
    assert xaxes.automargin == False, "L'automargin de l'axe x est activé."

    assert yaxes.tickfont.color == 'black', "La couleur de la police des ticks de l'axe y n'est pas 'black'."
    assert yaxes.title.font.color == 'black', "La couleur de la police du titre de l'axe y n'est pas 'black'."
    assert yaxes.automargin == False, "L'automargin de l'axe y est activé."
