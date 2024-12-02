import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import Donut

@pytest.fixture
def sample_data():
    """Fixture pour fournir des données d'exemple."""
    data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D'],
        'Value': [30, 20, 25, 25]
    })
    return data

def test_donut_initialization(sample_data):
    """Test l'initialisation de la classe Donut."""
    donut = Donut(data=sample_data, names='Category', values='Value', height=400)
    assert donut.data.equals(sample_data), "Les données ne sont pas correctement initialisées."
    assert donut.names == 'Category', "L'attribut names n'est pas correctement initialisé."
    assert donut.values == 'Value', "L'attribut values n'est pas correctement initialisé."
    assert donut.height == 400, "L'attribut height n'est pas correctement initialisé."

@patch('src.visualizations.graphiques.st.plotly_chart')
def test_donut_afficher(mock_plotly_chart, sample_data):
    """Test la méthode afficher de la classe Donut."""
    donut = Donut(data=sample_data, names='Category', values='Value', height=400)
    donut.afficher()

    # Vérifie que plotly_chart a été appelé une fois
    assert mock_plotly_chart.called, "plotly_chart n'a pas été appelé."
    assert mock_plotly_chart.call_count == 1, "plotly_chart a été appelé plus d'une fois."

    # Récupère la figure passée à plotly_chart
    fig = mock_plotly_chart.call_args[0][0]

    # Vérifie que fig est une instance de plotly.graph_objects.Figure
    assert hasattr(fig, 'data'), "La figure Plotly ne contient pas de données."
    assert fig.layout.height == 400, "La hauteur de la figure n'est pas correctement définie."

    # Vérifie les mises à jour du layout
    layout = fig.layout
    assert layout.plot_bgcolor == 'white', "La couleur de fond du plot n'est pas 'white'."
    assert layout.paper_bgcolor == 'white', "La couleur de fond du papier n'est pas 'white'."
    assert layout.margin.l == 20, "La marge gauche n'est pas 20."
    assert layout.margin.r == 20, "La marge droite n'est pas 20."
    assert layout.margin.t == 20, "La marge supérieure n'est pas 20."
    assert layout.margin.b == 20, "La marge inférieure n'est pas 20."

    # Vérifie les propriétés des traces
    traces = fig.data[0]
    assert traces.hole == 0.4, "Le trou de l'anneau (hole) n'est pas correctement défini."
    assert traces.hovertemplate == '%{percent}', "Le modèle de hover n'est pas correct."
    assert traces.textinfo == 'label', "Les informations de texte ne sont pas correctement définies."
    assert traces.textposition == 'inside', "La position du texte n'est pas 'inside'."
