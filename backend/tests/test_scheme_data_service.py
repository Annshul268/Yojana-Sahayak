"""Tests for frontend direct scheme data service."""

import pytest
from frontend.services.scheme_data import get_featured_schemes_db, get_live_db_statistics


def test_get_live_db_statistics():
    stats = get_live_db_statistics()
    assert stats["ok"] is True
    assert stats["total"] == 438
    assert stats["central"] == 109
    assert stats["state"] == 329
    assert stats["total"] == stats["central"] + stats["state"]

    cats = stats["categories"]
    expected_categories = [
        "Education & Scholarships",
        "Health",
        "Housing",
        "Agriculture",
        "Business & Loans",
        "Employment & Skills",
        "Pension",
        "Insurance",
        "Women & Child",
        "Disability Support",
    ]
    for cat in expected_categories:
        assert cat in cats
        assert isinstance(cats[cat], int)
        assert cats[cat] > 0

    assert len(stats["states"]) > 0


def test_get_featured_schemes_db():
    featured = get_featured_schemes_db(limit=5)
    assert len(featured) == 5
    for s in featured:
        assert "name" in s
        assert "slug" in s
        assert "official_url" in s
        assert s["is_featured"] is True
