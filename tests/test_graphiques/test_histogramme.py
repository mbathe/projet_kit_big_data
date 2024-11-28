import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import Histogramme

@pytest.fixture
def sample_data():
    """Fixture pour fournir des données d'exemple."""
    data = pd.DataFrame({
        'Values': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
    })
    return data

def test_histogramme_initialization(sample_data):
    """Test l'initialisation de la classe Histogramme."""
    histogram = Histogramme(data=sample_data, x='Values', height=500, bin_size=1)
    assert histogram.data.equals(sample_data), "Les données ne sont pas correctement initialisées."
    assert histogram.x == 'Values', "L'attribut x n'est pas correctement initialisé."
    assert histogram.height == 500, "L'attribut height n'est pas correctement initialisé."
    assert histogram.bin_size == 1, "L'attribut bin_size n'est pas correctement initialisé."

@patch('src.visualizations.graphiques.st.plotly_chart')
def test_histogramme_afficher(mock_plotly_chart, sample_data):
    """Test la méthode afficher de la classe Histogramme."""
    histogram = Histogramme(data=sample_data, x='Values', height=500, bin_size=1)
    histogram.afficher()

    # Vérifie que plotly_chart a été appelé une fois
    assert mock_plotly_chart.called, "plotly_chart n'a pas été appelé."
    assert mock_plotly_chart.call_count == 1, "plotly_chart a été appelé plus d'une fois."

    # Récupère la figure passée à plotly_chart
    fig = mock_plotly_chart.call_args[0][0]

    # Vérifie que fig est une instance de plotly.graph_objects.Figure
    assert hasattr(fig, 'data'), "La figure Plotly ne contient pas de données."
    assert fig.layout.height == 500, "La hauteur de la figure n'est pas correctement définie."

    # Vérifie les propriétés du trace Histogram
    trace = fig.data[0]
    assert trace.type == 'histogram', "Le type de trace n'est pas 'histogram'."
    assert trace.x.tolist() == sample_data['Values'].tolist(), "Les données de l'axe x ne correspondent pas."
    assert trace.xbins.size == 1, "La taille des bins n'est pas correcte."
    assert trace.marker.color == 'rgb(100, 149, 237)', "La couleur des barres n'est pas correcte."
    assert trace.hovertemplate == 'Intervalle: %{x}<br>Nombre: %{y}', "Le modèle de hover n'est pas correct."

    # Vérifie les mises à jour du layout
    layout = fig.layout
    assert layout.plot_bgcolor == 'white', "La couleur de fond du plot n'est pas 'white'."
    assert layout.paper_bgcolor == 'white', "La couleur de fond du papier n'est pas 'white'."
    assert layout.margin.l == 40, "La marge gauche n'est pas 40."
    assert layout.margin.r == 30, "La marge droite n'est pas 30."
    assert layout.margin.t == 30, "La marge supérieure n'est pas 30."
    assert layout.margin.b == 30, "La marge inférieure n'est pas 30."

    # Vérifie les propriétés des axes
    xaxis = layout.xaxis
    yaxis = layout.yaxis

    assert xaxis.showgrid == False, "La grille de l'axe x est affichée."
    assert xaxis.zeroline == False, "La ligne zéro de l'axe x est affichée."
    assert xaxis.showticklabels == True, "Les étiquettes de l'axe x ne sont pas affichées."
    assert xaxis.color == 'black', "La couleur de l'axe x n'est pas 'black'."

    assert yaxis.showgrid == True, "La grille de l'axe y n'est pas affichée."
    assert yaxis.zeroline == False, "La ligne zéro de l'axe y est affichée."
    assert yaxis.showticklabels == True, "Les étiquettes de l'axe y ne sont pas affichées."
    assert yaxis.color == 'black', "La couleur de l'axe y n'est pas 'black'."

    # Vérifie les mises à jour des axes
    assert xaxis.tickfont.color == 'black', "La couleur de la police des ticks de l'axe x n'est pas 'black'."
    assert xaxis.titlefont.color == 'black', "La couleur de la police du titre de l'axe x n'est pas 'black'."
    assert yaxis.tickfont.color == 'black', "La couleur de la police des ticks de l'axe y n'est pas 'black'."
    assert yaxis.titlefont.color == 'black', "La couleur de la police du titre de l'axe y n'est pas 'black'."
