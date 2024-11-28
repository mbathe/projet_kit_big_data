import pytest
from unittest.mock import patch
import pandas as pd
from src.visualizations.graphiques import Treemap

@pytest.fixture
def sample_data():
    """
    Fixture pour fournir un DataFrame d'exemple utilisé dans les tests.
    """
    return pd.DataFrame({
        'Category': ['A', 'A', 'B', 'B'],
        'Subcategory': ['X', 'Y', 'X', 'Y'],
        'Values': [100, 200, 150, 250]
    })

@patch('src.visualizations.graphiques.st.plotly_chart')
def test_treemap_initialization_and_display(mock_plotly_chart, sample_data):
    """
    Teste l'initialisation et l'affichage du Treemap.

    Paramètres
    ----------
    mock_plotly_chart : Mock
        Permet de vérifier si Streamlit affiche correctement le graphique.
    sample_data : pandas.DataFrame
        Jeu de données d'exemple fourni par la fixture.
    """
    # Initialisation du graphique
    treemap = Treemap(data=sample_data, path=['Category', 'Subcategory'], values='Values', height=400)

    # Vérification des attributs
    assert treemap.data.equals(sample_data), "Les données ne sont pas correctement initialisées."
    assert treemap.path == ['Category', 'Subcategory'], "L'attribut path n'est pas correctement initialisé."
    assert treemap.values == 'Values', "L'attribut values n'est pas correctement initialisé."
    assert treemap.height == 400, "L'attribut height n'est pas correctement initialisé."

    # Affichage du graphique
    treemap.afficher()

    # Vérifie que plotly_chart est appelé
    assert mock_plotly_chart.called, "La fonction plotly_chart de Streamlit n'a pas été appelée."
    assert mock_plotly_chart.call_count == 1, "La fonction plotly_chart a été appelée plus d'une fois."

    # Vérifie les propriétés du graphique
    fig = mock_plotly_chart.call_args[0][0]
    assert hasattr(fig, 'data'), "La figure Plotly ne contient pas de données."
    assert fig.layout.height == 400, "La hauteur du graphique n'est pas correctement définie."
    assert fig.layout.paper_bgcolor == 'white', "La couleur de fond du conteneur n'est pas 'white'."

@pytest.mark.parametrize("invalid_col", [
    (['Nonexistent'], 'Values'),                # Colonne inexistante dans path
    (['Category', 'Nonexistent'], 'Values'),   # Une colonne inexistante dans path
    (['Category', 'Subcategory'], 'Nonexistent')  # Colonne inexistante dans values
])
def test_treemap_invalid_columns(sample_data, invalid_col):
    """
    Teste que Treemap lève une erreur en cas de colonnes inexistantes.

    Paramètres
    ----------
    sample_data : pandas.DataFrame
        Jeu de données d'exemple fourni par la fixture.
    invalid_col : tuple
        Tuple contenant la liste des colonnes dans path et la colonne dans values.
    """
    invalid_path, invalid_values = invalid_col
    with pytest.raises(KeyError) as excinfo:
        Treemap(data=sample_data, path=invalid_path, values=invalid_values)
    for col in (invalid_path + [invalid_values]):
        if col not in sample_data.columns:
            assert col in str(excinfo.value), f"La colonne manquante {col} n'a pas été détectée."
