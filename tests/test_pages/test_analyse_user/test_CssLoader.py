import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))

sys.path.append(parent_parent_dir)

from src.pages.pages import CSSLoader

from unittest.mock import patch

def test_load_css():
    with patch("src.pages.analyse_user.load_css") as mock_load_css:
        CSSLoader.load("path/to/style.css")
        mock_load_css.assert_called_once_with("path/to/style.css")
