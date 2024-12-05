import pytest
from unittest.mock import patch, MagicMock
from src.pages.recipes.Analyse_recipes import CSSLoader

def test_load_css():
    with patch("src.pages.recipes.Analyse_recipes.load_css") as mock_load:
        CSSLoader.load("src/css_pages/recipe.css")
        mock_load.assert_called_once_with("src/css_pages/recipe.css")

def test_load_css_failure():
    with patch("src.pages.recipes.Analyse_recipes.load_css") as mock_load_css:
        mock_load_css.side_effect = Exception("CSS load error")
        with pytest.raises(Exception) as excinfo:
            CSSLoader.load("src/css_pages/recipe.css")
        assert str(excinfo.value) == "Failed to load CSS: CSS load error"
