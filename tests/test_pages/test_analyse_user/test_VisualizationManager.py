from src.pages.analyse_user import VisualizationManager

import pytest
import pandas as pd


def test_display_line_chart():
    try:
        data = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        VisualizationManager.display_line_chart(
            data=data,
            x="x",
            y="y",
            title="Test Chart"
        )
    except Exception as e:
        pytest.fail(f"Visualization failed: {e}")

