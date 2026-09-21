"""Tests for Government Data Pipeline components."""

import pytest
from backend.app.ingestion.cleaner import SchemeCleaner
from backend.app.ingestion.sources.curated import CuratedSource
from backend.app.ingestion.validator import SchemeValidator


def test_scheme_cleaner():
    cleaner = SchemeCleaner()
    raw = {
        "slug": " PM-TEST ",
        "name": "  Pradhan   Mantri Test  Scheme  ",
        "description": "  A   description with   spaces  ",
        "category": " Agriculture ",
        "ministry": " Ministry of Agri ",
        "benefits": [" Benefit   1  ", " "],
        "documents": [" Aadhaar   card "],
        "application_steps": [" Step  1 "],
    }
    cleaned = cleaner.clean(raw)
    assert cleaned["slug"] == "pm-test"
    assert cleaned["name"] == "Pradhan Mantri Test Scheme"
    assert cleaned["description"] == "A description with spaces"
    assert cleaned["benefits"] == ["Benefit 1"]
    assert cleaned["documents"] == ["Aadhaar card"]


def test_scheme_validator_valid():
    validator = SchemeValidator()
    item = {
        "slug": "pm-kisan",
        "name": "PM Kisan",
        "description": "Financial assistance for farmers",
        "category": "Agriculture",
        "ministry": "Ministry of Agriculture",
        "official_url": "https://pmkisan.gov.in/",
        "eligibility_rules": {"occupation": ["farmer"]},
    }
    is_valid, errors = validator.validate(item)
    assert is_valid is True
    assert len(errors) == 0


def test_scheme_validator_invalid_url():
    validator = SchemeValidator()
    item = {
        "slug": "pm-kisan",
        "name": "PM Kisan",
        "description": "Financial assistance for farmers",
        "category": "Agriculture",
        "ministry": "Ministry of Agriculture",
        "official_url": "invalid_url_without_protocol",
        "eligibility_rules": {},
    }
    is_valid, errors = validator.validate(item)
    assert is_valid is False
    assert any("official_url" in e for e in errors)


@pytest.mark.asyncio
async def test_curated_source():
    source = CuratedSource(file_path="data/seed/schemes.json")
    schemes = await source.fetch_schemes()
    assert len(schemes) >= 10
    slugs = [s["slug"] for s in schemes]
    assert "pm-kisan" in slugs
    assert "ayushman-bharat-pmjay" in slugs
