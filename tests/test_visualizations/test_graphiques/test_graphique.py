import pytest
from src.visualizations.graphique import Graphique

def test_graphique_afficher():
    """Test que la méthode afficher est définie mais ne fait rien."""
    # Création d'une instance de Graphique avec des données fictives
    data = {"key": "value"}
    graphique = Graphique(data)

    # Vérifie que la méthode 'afficher' existe et peut être appelée sans erreur
    try:
        graphique.afficher()
    except Exception as e:
        pytest.fail(f"La méthode afficher ne devrait pas lever d'exception : {e}")
