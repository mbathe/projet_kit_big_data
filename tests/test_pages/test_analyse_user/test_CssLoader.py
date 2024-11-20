from src.pages.analyse_user import CSSLoader

from unittest.mock import patch

def test_load_css():
    with patch("src.pages.analyse_user.load_css") as mock_load_css:
        CSSLoader.load("path/to/style.css")
        mock_load_css.assert_called_once_with("path/to/style.css")
