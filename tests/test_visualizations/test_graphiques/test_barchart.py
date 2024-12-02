import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import BarChart

@patch("src.visualizations.graphiques.st.plotly_chart")
def test_barchart_afficher(mock_plotly_chart):
    """Test la méthode afficher de la classe BarChart."""
    # Données d'exemple
    sample_data = pd.DataFrame({
        'Category': ['A', 'B', 'C'],
        'Values': [10, 20, 30]
    })

    # Création de l'objet BarChart 
    chart = BarChart(data=sample_data, x='Category', y='Values', height=500)

    # Appel de la méthode afficher
    chart.afficher()

    # Vérification que st.plotly_chart a été appelé une fois
    mock_plotly_chart.assert_called_once()

    # Vérifie que la figure contient les données attendues
    fig = mock_plotly_chart.call_args[0][0]
    assert fig.layout.height == 500, "La hauteur de la figure n'est pas définie correctement."
    assert fig.data[0].type == "bar", "La figure n'est pas un graphique en barres."

    # Vérification des mises à jour de mise en page
    layout = fig.layout
    assert layout.plot_bgcolor == 'white', "La couleur de fond du plot n'est pas 'white'."
    assert layout.paper_bgcolor == 'white', "La couleur de fond du papier n'est pas 'white'."
    assert layout.margin.l == 30, "La marge gauche n'est pas 30."
    assert layout.margin.r == 0, "La marge droite n'est pas 0."
    assert layout.margin.t == 20, "La marge supérieure n'est pas 20."
    assert layout.margin.b == 30, "La marge inférieure n'est pas 30."

    assert layout.xaxis.color == 'black', "La couleur de l'axe x n'est pas 'black'."
    assert layout.yaxis.color == 'black', "La couleur de l'axe y n'est pas 'black'."
