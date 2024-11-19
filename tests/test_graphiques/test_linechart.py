import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import LineChart

@pytest.fixture
def sample_data():
    """
    Fixture pour fournir un DataFrame d'exemple utilisé dans les tests.
    """
    return pd.DataFrame({
        'Time': ['2021-01', '2021-02', '2021-03'],
        'Values': [100, 200, 300]
    })

@patch('src.visualizations.graphiques.st.plotly_chart')
def test_linechart_initialization_and_display(mock_plotly_chart, sample_data):
    """
    Teste l'initialisation et l'affichage du LineChart.

    Paramètres
    ----------
    mock_plotly_chart : Mock
        Permet de vérifier si Streamlit affiche correctement le graphique.
    sample_data : pandas.DataFrame
        Jeu de données d'exemple fourni par la fixture.
    """
    # Initialisation du graphique
    line_chart = LineChart(data=sample_data, x='Time', y='Values', height=400)

    # Vérification des attributs
    assert line_chart.data.equals(sample_data), "Les données ne sont pas correctement initialisées."
    assert line_chart.x == 'Time', "L'attribut x n'est pas correctement initialisé."
    assert line_chart.y == 'Values', "L'attribut y n'est pas correctement initialisé."
    assert line_chart.height == 400, "L'attribut height n'est pas correctement initialisé."

    # Affichage du graphique
    line_chart.afficher()

    # Vérifie que plotly_chart est appelé
    assert mock_plotly_chart.called, "La fonction plotly_chart de Streamlit n'a pas été appelée."
    assert mock_plotly_chart.call_count == 1, "La fonction plotly_chart a été appelée plus d'une fois."

    # Vérifie les propriétés du graphique
    fig = mock_plotly_chart.call_args[0][0]
    assert hasattr(fig, 'data'), "La figure Plotly ne contient pas de données."
    assert fig.layout.height == 400, "La hauteur du graphique n'est pas correctement définie."
    assert fig.layout.plot_bgcolor == 'white', "La couleur de fond du graphique n'est pas 'white'."
    assert fig.layout.paper_bgcolor == 'white', "La couleur de fond du conteneur n'est pas 'white'."

    # Vérifie les propriétés des axes
    xaxis = fig.layout.xaxis
    yaxis = fig.layout.yaxis
    assert xaxis.showgrid, "La grille de l'axe x n'est pas activée."
    assert not xaxis.zeroline, "La ligne zéro de l'axe x est affichée."
    assert xaxis.color == 'black', "La couleur de l'axe x n'est pas 'black'."
    assert yaxis.showgrid, "La grille de l'axe y n'est pas activée."
    assert not yaxis.zeroline, "La ligne zéro de l'axe y est affichée."
    assert yaxis.color == 'black', "La couleur de l'axe y n'est pas 'black'."

@pytest.mark.parametrize("invalid_col", ['Nonexistent'])
def test_linechart_invalid_columns(sample_data, invalid_col):
    """
    Teste que LineChart lève une erreur en cas de colonnes inexistantes.

    Paramètres
    ----------
    sample_data : pandas.DataFrame
        Jeu de données d'exemple fourni par la fixture.
    invalid_col : str
        Nom de la colonne inexistante.
    """
    with pytest.raises(KeyError) as excinfo:
        LineChart(data=sample_data, x=invalid_col, y='Values')
    assert invalid_col in str(excinfo.value), f"La colonne manquante {invalid_col} n'a pas été détectée."

    with pytest.raises(KeyError) as excinfo:
        LineChart(data=sample_data, x='Time', y=invalid_col)
    assert invalid_col in str(excinfo.value), f"La colonne manquante {invalid_col} n'a pas été détectée."
