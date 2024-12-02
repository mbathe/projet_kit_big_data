import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from src.visualizations.grille import Grille

@patch("src.visualizations.grille.st.container")
@patch("src.visualizations.grille.st.columns")
@patch("src.visualizations.grille.st.markdown")
def test_grille_afficher_line_21(mock_markdown, mock_columns, mock_container):
    # Configuration des mocks
    mock_column = MagicMock()
    mock_columns.return_value = [mock_column] * 3  # Simule 3 colonnes

    # Création d'une instance de Grille
    grille = Grille(nb_lignes=1, nb_colonnes=3, largeurs_colonnes=[1, 1, 1])

    # Graphiques à afficher
    graphiques = [
        {"titre": "Graph 1", "graphique": MagicMock(afficher=MagicMock())},
    ]

    # Appelle la méthode afficher
    grille.afficher(graphiques)

    # Vérifie que le conteneur Markdown a été appelé
    mock_container().markdown.assert_called_once_with(
        '<div class="graph-container"></div>', unsafe_allow_html=True
    )
