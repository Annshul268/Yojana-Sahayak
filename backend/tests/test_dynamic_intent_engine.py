"""Comprehensive tests for Sector-Aware Intent Engine, Grouped Questionnaire, and Taxonomy."""

import pytest
from backend.app.database.models import Scheme
from backend.app.matching.engine import MatchingEngine
from backend.app.matching.models import CitizenProfileInput, EligibilityStatus
from backend.app.matching.taxonomy import INTENT_REGISTRY, get_all_intents, match_intent_candidate_schemes
from frontend.services.questionnaire_engine import questionnaire_engine


@pytest.fixture
def comprehensive_scheme_catalog():
    return [
        Scheme(
            id="s_agri",
            slug="pm-kisan",
            name="PM-KISAN",
            category="Agriculture & Rural Development",
            ministry="Ministry of Agriculture",
            states=["ALL"],
            tags=["agriculture", "farmer", "income-support", "crop"],
            eligibility_rules={"occupation": ["farmer"], "states": ["ALL"]},
            benefits=["₹6,000 yearly"],
            official_url="https://pmkisan.gov.in/",
            active=True,
        ),
        Scheme(
            id="s_health",
            slug="ayushman-bharat-pmjay",
            name="Ayushman Bharat PM-JAY",
            category="Healthcare",
            ministry="Ministry of Health & Family Welfare",
            states=["ALL"],
            tags=["health", "medical", "hospital", "ayushman", "insurance"],
            eligibility_rules={"income": {"max": 250000}, "states": ["ALL"]},
            benefits=["₹5,00,000 cashless health insurance"],
            official_url="https://beneficiary.nha.gov.in/",
            active=True,
        ),
        Scheme(
            id="s_house",
            slug="pm-awas-yojana-gramin",
            name="PMAY Gramin",
            category="Housing & Shelter",
            ministry="Ministry of Rural Development",
            states=["ALL"],
            tags=["housing", "awas", "shelter", "pucca-house", "rural"],
            eligibility_rules={"area": ["Rural"], "income": {"max": 300000}, "states": ["ALL"]},
            benefits=["₹1,20,000 pucca house subsidy"],
            official_url="https://pmayg.nic.in/",
            active=True,
        ),
        Scheme(
            id="s_biz",
            slug="pm-mudra-yojana",
            name="PM MUDRA Yojana",
            category="Business & Self Employment",
            ministry="Ministry of Finance",
            states=["ALL"],
            tags=["business", "msme", "entrepreneurship", "loan", "credit"],
            eligibility_rules={"age": {"min": 18, "max": 65}, "states": ["ALL"]},
            benefits=["Collateral-free micro loans up to ₹20 Lakh"],
            official_url="https://www.mudra.org.in/",
            active=True,
        ),
        Scheme(
            id="s_edu",
            slug="post-matric-scholarship",
            name="Post-Matric Scholarship",
            category="Education & Learning",
            ministry="Ministry of Social Justice",
            states=["ALL"],
            tags=["education", "scholarship", "student", "tuition", "college"],
            eligibility_rules={
                "occupation": ["student"],
                "category": ["SC", "ST", "OBC"],
                "income": {"max": 250000},
                "states": ["ALL"],
            },
            benefits=["Full tuition fee reimbursement"],
            official_url="https://scholarships.gov.in/",
            active=True,
        ),
        Scheme(
            id="s_women",
            slug="sukanya-samriddhi",
            name="Sukanya Samriddhi Yojana",
            category="Women & Child Development",
            ministry="Ministry of Finance",
            states=["ALL"],
            tags=["women", "girl-child", "sukanya", "savings", "child"],
            eligibility_rules={"gender": ["female"], "age": {"min": 0, "max": 10}, "states": ["ALL"]},
            benefits=["Triple tax exempt girl child savings"],
            official_url="https://www.indiapost.gov.in/",
            active=True,
        ),
        Scheme(
            id="s_intern",
            slug="pm-internship-scheme",
            name="PM Internship Scheme",
            category="Employment & Skills",
            ministry="Ministry of Corporate Affairs",
            states=["ALL"],
            tags=["internship", "apprenticeship", "stipend", "youth"],
            eligibility_rules={"age": {"min": 21, "max": 24}, "income": {"max": 800000}, "states": ["ALL"]},
            benefits=["₹5,000 monthly stipend"],
            official_url="https://pminternship.mca.gov.in/",
            active=True,
        ),
        Scheme(
            id="s_skills",
            slug="pmkvy",
            name="PM Kaushal Vikas Yojana",
            category="Employment & Skills",
            ministry="Ministry of Skill Development",
            states=["ALL"],
            tags=["skill", "training", "vocational", "certification", "pmkvy"],
            eligibility_rules={"age": {"min": 15, "max": 45}, "states": ["ALL"]},
            benefits=["100% free certified vocational training"],
            official_url="https://www.pmkvyofficial.org/",
            active=True,
        ),
    ]


def test_intent_taxonomy_structure():
    """Verify all 14 intent taxonomy definitions exist with metadata."""
    intents = get_all_intents()
    assert len(intents) >= 14
    intent_ids = [i.id for i in intents]
    expected = [
        "education", "jobs", "internships", "skills", "business",
        "agriculture", "housing", "healthcare", "financial", "women_child",
        "pension", "disability", "social_welfare", "general"
    ]
    for exp in expected:
        assert exp in intent_ids


def test_strict_sector_filtering_education(comprehensive_scheme_catalog):
    """Section 21: Verify Education query strictly excludes healthcare, housing, and savings schemes."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="education",
        state="Uttar Pradesh",
        age=20,
        gender="female",
        annual_family_income=120000.0,
        category="SC",
        area="Rural",
    )
    response = engine.match_all(comprehensive_scheme_catalog, profile)

    result_slugs = [r.slug for r in response.results]
    # Post-Matric Scholarship should match
    assert "post-matric-scholarship" in result_slugs

    # Unrelated sectors MUST NOT be returned
    assert "ayushman-bharat-pmjay" not in result_slugs
    assert "pm-awas-yojana-gramin" not in result_slugs
    assert "sukanya-samriddhi" not in result_slugs
    assert "pm-kisan" not in result_slugs


def test_strict_sector_filtering_business(comprehensive_scheme_catalog):
    """Verify Business query strictly excludes agriculture and student schemes."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="business",
        state="Maharashtra",
        age=30,
        annual_family_income=200000.0,
    )
    response = engine.match_all(comprehensive_scheme_catalog, profile)

    result_slugs = [r.slug for r in response.results]
    assert "pm-mudra-yojana" in result_slugs
    assert "pm-kisan" not in result_slugs
    assert "post-matric-scholarship" not in result_slugs


def test_strict_sector_filtering_agriculture(comprehensive_scheme_catalog):
    """Verify Agriculture query strictly excludes scholarships and business loans."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="agriculture",
        state="Punjab",
        occupation="farmer",
        annual_family_income=180000.0,
    )
    response = engine.match_all(comprehensive_scheme_catalog, profile)

    result_slugs = [r.slug for r in response.results]
    assert "pm-kisan" in result_slugs
    assert "post-matric-scholarship" not in result_slugs
    assert "pm-mudra-yojana" not in result_slugs


def test_strict_sector_filtering_healthcare(comprehensive_scheme_catalog):
    """Verify Healthcare query strictly excludes student scholarships."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="healthcare",
        state="Bihar",
        annual_family_income=150000.0,
        category="OBC",
    )
    response = engine.match_all(comprehensive_scheme_catalog, profile)

    result_slugs = [r.slug for r in response.results]
    assert "ayushman-bharat-pmjay" in result_slugs
    assert "post-matric-scholarship" not in result_slugs
    assert "pm-kisan" not in result_slugs


def test_manual_numeric_income_evaluation(comprehensive_scheme_catalog):
    """Section 4D: Verify manual numeric income evaluation."""
    engine = MatchingEngine()

    # User with income ₹1,80,000 (within ₹2,50,000 limit) -> Eligible
    passing_profile = CitizenProfileInput(
        intent="education",
        state="Delhi",
        age=19,
        occupation="student",
        category="SC",
        annual_family_income=180000.0,
    )
    res_pass = engine.match_all(comprehensive_scheme_catalog, passing_profile)
    sch_pass = next(r for r in res_pass.results if r.slug == "post-matric-scholarship")
    assert sch_pass.status == EligibilityStatus.ELIGIBLE

    # User with income ₹3,20,000 (exceeds ₹2,50,000 limit) -> Disqualified
    failing_profile = CitizenProfileInput(
        intent="education",
        state="Delhi",
        age=19,
        occupation="student",
        category="SC",
        annual_family_income=320000.0,
    )
    res_fail = engine.match_all(comprehensive_scheme_catalog, failing_profile)
    sch_fail = next(r for r in res_fail.results if r.slug == "post-matric-scholarship")
    assert sch_fail.status == EligibilityStatus.NOT_ELIGIBLE


def test_grouped_questionnaire_progression():
    """Verify questionnaire engine groups active steps correctly."""
    # Step 0: Initial state with no intent -> only intent selection group
    groups_init = questionnaire_engine.get_active_groups({})
    assert len(groups_init) == 1
    assert groups_init[0].id == "intent_selection"

    # With Education intent -> Intent + Location/Personal + Economic/Social + Education sector
    groups_edu = questionnaire_engine.get_active_groups({"intent": "education"})
    group_ids_edu = [g.id for g in groups_edu]
    assert "intent_selection" in group_ids_edu
    assert "location_personal" in group_ids_edu
    assert "economic_social" in group_ids_edu
    assert "sector_education" in group_ids_edu
    assert "sector_business" not in group_ids_edu
    assert "sector_agriculture" not in group_ids_edu

    # With Business intent -> Intent + Location/Personal + Economic/Social + Business sector
    groups_biz = questionnaire_engine.get_active_groups({"intent": "business"})
    group_ids_biz = [g.id for g in groups_biz]
    assert "sector_business" in group_ids_biz
    assert "sector_education" not in group_ids_biz


def test_questionnaire_group_validation():
    """Verify validate_group enforces required fields on each card."""
    loc_group = next(g for g in questionnaire_engine.common_groups if g.id == "location_personal")

    # Empty answers should fail validation
    ok, err = questionnaire_engine.validate_group(loc_group, {})
    assert ok is False
    assert err is not None

    # Complete valid answers should pass validation
    valid_answers = {
        "state": "Uttar Pradesh",
        "area": "Rural",
        "age": 25,
        "gender": "female",
    }
    ok, err = questionnaire_engine.validate_group(loc_group, valid_answers)
    assert ok is True
    assert err is None


def test_payload_builder_normalization():
    """Verify normalized profile dictionary matches CitizenProfileInput."""
    answers = {
        "intent": "education",
        "state": "Uttar Pradesh",
        "district": "Gorakhpur",
        "area": "Rural",
        "age": 21,
        "gender": "male",
        "marital_status": "single",
        "annual_income": "220000",
        "social_category": "OBC",
        "disability": "no",
        "minority_status": "no",
        "education_level": "undergraduate",
        "course_name": "B.Tech Computer Science",
        "institution_type": "government",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["intent"] == "education"
    assert payload["state"] == "Uttar Pradesh"
    assert payload["district"] == "Gorakhpur"
    assert payload["area"] == "Rural"
    assert payload["age"] == 21
    assert payload["gender"] == "male"
    assert payload["annual_family_income"] == 220000.0
    assert payload["category"] == "OBC"
    assert payload["disability"] is False
    assert payload["occupation"] == "student"
    assert payload["education"]["level"] == "undergraduate"
    assert payload["education"]["course"] == "B.Tech Computer Science"


def test_user_journey_internship_seeker(comprehensive_scheme_catalog):
    """Verify internship seeker matches PM Internship Scheme and excludes farmer/pension schemes."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="internships",
        state="Maharashtra",
        age=22,
        gender="female",
        annual_family_income=250000.0,
    )
    res = engine.match_all(comprehensive_scheme_catalog, profile)
    slugs = [r.slug for r in res.results]
    assert "pm-internship-scheme" in slugs
    assert "pm-kisan" not in slugs
    assert "sukanya-samriddhi" not in slugs


def test_user_journey_skill_seeker(comprehensive_scheme_catalog):
    """Verify skill seeker matches PMKVY."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="skills",
        state="Rajasthan",
        age=20,
        annual_family_income=150000.0,
    )
    res = engine.match_all(comprehensive_scheme_catalog, profile)
    slugs = [r.slug for r in res.results]
    assert "pmkvy" in slugs
    assert "pm-kisan" not in slugs


def test_user_journey_housing_seeker(comprehensive_scheme_catalog):
    """Verify housing seeker matches PMAY and excludes scholarships."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="housing",
        state="Madhya Pradesh",
        area="Rural",
        annual_family_income=180000.0,
    )
    res = engine.match_all(comprehensive_scheme_catalog, profile)
    slugs = [r.slug for r in res.results]
    assert "pm-awas-yojana-gramin" in slugs
    assert "post-matric-scholarship" not in slugs
    assert "pm-mudra-yojana" not in slugs


def test_user_journey_women_child_seeker(comprehensive_scheme_catalog):
    """Verify girl child savings query matches Sukanya Samriddhi."""
    engine = MatchingEngine()
    profile = CitizenProfileInput(
        intent="women_child",
        state="Haryana",
        age=5,
        gender="female",
    )
    res = engine.match_all(comprehensive_scheme_catalog, profile)
    slugs = [r.slug for r in res.results]
    assert "sukanya-samriddhi" in slugs
    assert "pm-kisan" not in slugs
    assert "post-matric-scholarship" not in slugs

