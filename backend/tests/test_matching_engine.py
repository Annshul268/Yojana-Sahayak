"""Comprehensive tests for Deterministic Matching Engine."""

import pytest
from backend.app.database.models import Scheme
from backend.app.matching.engine import MatchingEngine
from backend.app.matching.models import CitizenProfileInput, EligibilityStatus


@pytest.fixture
def sample_schemes():
    return [
        Scheme(
            id="s1",
            slug="pm-kisan-test",
            name="PM Kisan Test",
            category="Agriculture",
            ministry="Ministry of Agriculture",
            states=["ALL"],
            eligibility_rules={"occupation": ["farmer"], "states": ["ALL"]},
            benefits=["₹6,000 yearly"],
            official_url="https://pmkisan.gov.in/",
            active=True,
        ),
        Scheme(
            id="s2",
            slug="scholarship-test",
            name="Post Matric Scholarship Test",
            category="Education",
            ministry="Ministry of Social Justice",
            states=["ALL"],
            eligibility_rules={
                "occupation": ["student"],
                "category": ["SC", "ST", "OBC"],
                "income": {"max": 250000},
            },
            benefits=["Full tuition fee"],
            official_url="https://scholarships.gov.in/",
            active=True,
        ),
        Scheme(
            id="s3",
            slug="pension-test",
            name="Atal Pension Test",
            category="Pension",
            ministry="Ministry of Finance",
            states=["ALL"],
            eligibility_rules={"age": {"min": 18, "max": 40}},
            benefits=["Guaranteed monthly pension"],
            official_url="https://npscra.nsdl.co.in/",
            active=True,
        ),
        Scheme(
            id="s4",
            slug="disability-test",
            name="Divyangjan Support Test",
            category="Differently Abled Support",
            ministry="Ministry of Social Justice",
            states=["ALL"],
            eligibility_rules={"disability": True, "age": {"min": 18}},
            benefits=["Concessional loan"],
            official_url="https://nhfdc.org/",
            active=True,
        ),
    ]


def test_eligible_farmer(sample_schemes):
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        state="Uttar Pradesh",
        age=35,
        gender="male",
        annual_income=150000,
        occupation="farmer",
        category="General",
        area="Rural",
        disability=False,
    )
    response = engine.match_all(sample_schemes, profile)
    assert response.total_schemes_evaluated == 4
    # PM Kisan should be ELIGIBLE
    kisan_match = next(r for r in response.results if r.slug == "pm-kisan-test")
    assert kisan_match.status == EligibilityStatus.ELIGIBLE
    assert kisan_match.score >= 90
    assert len(kisan_match.failed_rules) == 0


def test_income_too_high_disqualification(sample_schemes):
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        state="Bihar",
        age=20,
        gender="female",
        annual_income=450000,  # Limit is 250000
        occupation="student",
        category="SC",
    )
    response = engine.match_all(sample_schemes, profile)
    scholarship_match = next(r for r in response.results if r.slug == "scholarship-test")
    assert scholarship_match.status == EligibilityStatus.NOT_ELIGIBLE
    assert any(r.rule_name == "annual_income" for r in scholarship_match.failed_rules)
    assert scholarship_match.score < 50


def test_age_outside_range_disqualification(sample_schemes):
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        state="Maharashtra",
        age=45,  # Max limit is 40
        annual_income=200000,
        occupation="self-employed",
    )
    response = engine.match_all(sample_schemes, profile)
    pension_match = next(r for r in response.results if r.slug == "pension-test")
    assert pension_match.status == EligibilityStatus.NOT_ELIGIBLE
    assert any(r.rule_name == "age" for r in pension_match.failed_rules)


def test_missing_information_yields_potentially_eligible(sample_schemes):
    engine = MatchingEngine()
    # Missing annual_income
    profile = CitizenProfileInput(
        state="Punjab",
        age=21,
        occupation="student",
        category="SC",
        annual_income=None,  # Missing
    )
    response = engine.match_all(sample_schemes, profile)
    scholarship_match = next(r for r in response.results if r.slug == "scholarship-test")
    assert scholarship_match.status == EligibilityStatus.POTENTIALLY_ELIGIBLE
    assert any(m["field"] == "annual_income" for m in scholarship_match.missing_information)
    assert 50 <= scholarship_match.score <= 89


def test_ranking_order(sample_schemes):
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        state="Delhi",
        age=25,
        annual_income=100000,
        occupation="student",
        category="SC",
        disability=False,
    )
    response = engine.match_all(sample_schemes, profile)
    statuses = [r.status for r in response.results]
    # Check that ELIGIBLE is sorted ahead of NOT_ELIGIBLE
    eligible_indices = [i for i, s in enumerate(statuses) if s == EligibilityStatus.ELIGIBLE]
    not_eligible_indices = [i for i, s in enumerate(statuses) if s == EligibilityStatus.NOT_ELIGIBLE]
    if eligible_indices and not_eligible_indices:
        assert max(eligible_indices) < min(not_eligible_indices)
