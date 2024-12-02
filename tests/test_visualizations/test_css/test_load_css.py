import pytest
from unittest.mock import patch, mock_open
from src.visualizations.load_css import load_css
import streamlit as st


# Teste le chargement réussi du fichier CSS
@patch("builtins.open", new_callable=mock_open, read_data="body { background-color: #fff; }")
@patch("src.visualizations.load_css.st.markdown")
def test_load_css_success(mock_markdown, mock_open_file):
    css_path = "src/css_pages/recipe.css"
    
    # Appelle la fonction
    load_css(css_path)
    
    # Vérifie que le fichier est ouvert correctement
    mock_open_file.assert_called_once_with(css_path)
    
    # Vérifie que le CSS est injecté dans Streamlit
    mock_markdown.assert_called_once_with(
        '<style>body { background-color: #fff; }</style>', unsafe_allow_html=True
    )


# Teste un cas où le fichier CSS est introuvable
@patch("builtins.open", side_effect=FileNotFoundError)
@patch("src.visualizations.load_css.st.error")
def test_load_css_file_not_found(mock_error, mock_open_file):
    css_path = "src/css_pages/recipe.css"
    
    # Appelle la fonction
    load_css(css_path)
    
    # Vérifie que le fichier est tenté d'être ouvert
    mock_open_file.assert_called_once_with(css_path)
    
    # Vérifie que l'erreur est affichée dans Streamlit
    mock_error.assert_called_once_with(f"Le fichier CSS n'a pas été trouvé : {css_path}")
