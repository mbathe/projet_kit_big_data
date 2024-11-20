from src.pages.analyse_user import DataAnalyzer

import pandas as pd
import numpy as np
import pytest


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "user_id": [1, 1, 2, 2],
        "rating": [5, 4, 3, 2],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])
    })


def test_preprocess(sample_data):
    analyzer = DataAnalyzer(sample_data)
    processed_data = analyzer.preprocess()
    assert "year" in processed_data.columns
    assert pd.api.types.is_string_dtype(processed_data["year"])


def test_analyze_user(sample_data):
    analyzer = DataAnalyzer(sample_data)
    analyzer.preprocess()  # Preprocess the data
    user_data = analyzer.analyze_user(1)
    assert user_data is not None
    assert "Mois" in user_data.columns
    assert "Note moyenne" in user_data.columns


def test_analyze_monthly_ratings(sample_data):
    sample_data["date"] = pd.to_datetime(sample_data["date"])
    analyzer = DataAnalyzer(sample_data)
    monthly_avg = analyzer.analyze_monthly_ratings()
    assert "Mois" in monthly_avg.columns
    assert "Note moyenne" in monthly_avg.columns

def test_analyze_ratings_frequencies(sample_data):
    analyzer = DataAnalyzer(sample_data)
    frequency_data = analyzer.analyze_ratings_frequencies()
    assert len(frequency_data) > 0
    for rating, rating_data in frequency_data:
        assert isinstance(rating, (int, float, np.integer))
        assert isinstance(rating_data, pd.DataFrame)
