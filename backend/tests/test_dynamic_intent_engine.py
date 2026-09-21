"""Comprehensive tests for Dynamic Intent Engine, Adaptive Questionnaire, and Taxonomy."""

import pytest
from backend.app.database.models import Scheme
from backend.app.matching.engine import MatchingEngine
from backend.app.matching.models import CitizenProfileInput, EligibilityStatus
from backend.app.matching.taxonomy import INTENT_REGISTRY, get_all_intents, match_intent_candidate_schemes
from frontend.services.questionnaire_engine import questionnaire_engine


def test_intent_taxonomy_structure():
    """Verify intent taxonomy definitions and required attributes."""
    intents = get_all_intents()
    assert len(intents) >= 10
    intent_ids = [i.id for i in intents]
    assert "education" in intent_ids
    assert "business" in intent_ids
    assert "agriculture" in intent_ids
    assert "jobs" in intent_ids
    assert "skills" in intent_ids
    assert "housing" in intent_ids
    assert "healthcare" in intent_ids
    assert "pension" in intent_ids
    assert "women_child" in intent_ids
    assert "disability" in intent_ids


def test_adaptive_question_conditional_branching():
    """Verify irrelevant questions are skipped per Section 66 requirements."""
    # 1. Scholarship Intent: Must ask student_type, MUST NOT ask business_stage or landholding
    answers_edu = {"intent": "education"}
    q_edu_ids = [q.id for q in questionnaire_engine.get_active_questions(answers_edu)]
    assert "student_type" in q_edu_ids
    assert "business_stage" not in q_edu_ids
    assert "landholding" not in q_edu_ids
    assert "employment_status" not in q_edu_ids

    # 2. Business Intent: Must ask business_stage, MUST NOT ask student_type or landholding
    answers_biz = {"intent": "business"}
    q_biz_ids = [q.id for q in questionnaire_engine.get_active_questions(answers_biz)]
    assert "business_stage" in q_biz_ids
    assert "student_type" not in q_biz_ids
    assert "landholding" not in q_biz_ids
    assert "employment_status" not in q_biz_ids

    # 3. Agriculture Intent: When landowner, ask landholding. When laborer, skip landholding.
    answers_agri = {"intent": "agriculture", "farmer_type": "landowner"}
    q_agri_ids = [q.id for q in questionnaire_engine.get_active_questions(answers_agri)]
    assert "landholding" in q_agri_ids
    assert "student_type" not in q_agri_ids
    assert "business_stage" not in q_agri_ids

    answers_laborer = {"intent": "agriculture", "farmer_type": "agri_worker"}
    q_laborer_ids = [q.id for q in questionnaire_engine.get_active_questions(answers_laborer)]
    assert "landholding" not in q_laborer_ids

    # 4. Employment Intent: Must ask employment_status, MUST NOT ask student_type or landholding
    answers_job = {"intent": "jobs"}
    q_job_ids = [q.id for q in questionnaire_engine.get_active_questions(answers_job)]
    assert "employment_status" in q_job_ids
    assert "student_type" not in q_job_ids
    assert "landholding" not in q_job_ids


def test_payload_builder_normalization():
    """Verify questionnaire answers correctly translate into CitizenProfileInput."""
    answers = {
        "intent": "education",
        "student_type": "college",
        "social_category": "SC",
        "annual_income": "250000",
        "state": "Uttar Pradesh",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["occupation"] == "student"
    assert payload["category"] == "SC"
    assert payload["annual_income"] == 250000.0
    assert payload["state"] == "Uttar Pradesh"
    assert "Education & scholarships" in payload["needs"]
    assert payload["dynamic_answers"]["education_level"] == "college"


def test_structured_matching_result_fields():
    """Verify Section 59 structured result attributes."""
    engine = MatchingEngine()
    test_scheme = Scheme(
        id="pm-kisan-id",
        slug="pm-kisan-test",
        name="PM Kisan Test",
        category="Agriculture & Rural Development",
        ministry="Ministry of Agriculture",
        states=["ALL"],
        tags=["agriculture", "farmer", "income-support"],
        eligibility_rules={"occupation": ["farmer"], "states": ["ALL"]},
        benefits=["₹6,000 yearly"],
        documents=["Aadhaar", "Land Records"],
        application_steps=["Apply online"],
        official_url="https://pmkisan.gov.in/",
        active=True,
    )

    profile = CitizenProfileInput(
        state="Uttar Pradesh",
        age=35,
        gender="male",
        annual_income=150000,
        occupation="farmer",
        category="General",
        area="Rural",
        intent="agriculture",
        needs=["Agriculture"],
    )

    result = engine.evaluate_scheme(test_scheme, profile)
    assert result.status == EligibilityStatus.ELIGIBLE
    assert result.score == 100
    assert result.relevance == "high"
    assert len(result.matched_attributes) > 0
    assert len(result.failed_conditions) == 0
    assert result.reason != ""
    assert result.scheme is not None
    assert result.scheme["slug"] == "pm-kisan-test"
    assert "agriculture" in result.tags


def test_candidate_scheme_tag_retrieval():
    """Verify intent pre-filtering candidates based on structured tags."""
    schemes = [
        Scheme(id="1", slug="s1", name="Kisan", category="Agriculture", tags=["agriculture", "farmer"], active=True),
        Scheme(id="2", slug="s2", name="Scholarship", category="Education", tags=["education", "student"], active=True),
        Scheme(id="3", slug="s3", name="Mudra", category="Business", tags=["business", "msme"], active=True),
    ]

    agri_candidates = match_intent_candidate_schemes("agriculture", schemes)
    assert len(agri_candidates) == 1
    assert agri_candidates[0].slug == "s1"

    edu_candidates = match_intent_candidate_schemes("education", schemes)
    assert len(edu_candidates) == 1
    assert edu_candidates[0].slug == "s2"


def test_validation_invalid_age():
    """Verify validation rejects invalid age values."""
    with pytest.raises(Exception):
        CitizenProfileInput(age=-5)

    with pytest.raises(Exception):
        CitizenProfileInput(age=150)


def test_validation_negative_income():
    """Verify validation rejects negative income values."""
    with pytest.raises(Exception):
        CitizenProfileInput(annual_income=-50000)


def test_user_journey_scholarship_college():
    """Verify complete user journey for College Student Scholarship."""
    answers = {
        "intent": "education",
        "student_type": "college",
        "social_category": "OBC",
        "annual_income": "200000",
        "state": "Uttar Pradesh",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["occupation"] == "student"
    assert payload["category"] == "OBC"
    assert payload["annual_income"] == 200000.0
    assert payload["intent"] == "education"


def test_user_journey_business_vendor():
    """Verify complete user journey for Street Vendor / Micro Loan."""
    answers = {
        "intent": "business",
        "business_stage": "street_vendor",
        "social_category": "General",
        "annual_income": "100000",
        "state": "Delhi",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["occupation"] == "street vendor"
    assert payload["intent"] == "business"
    assert "Business & loans" in payload["needs"]


def test_user_journey_agriculture_farmer():
    """Verify complete user journey for Marginal Farmer."""
    answers = {
        "intent": "agriculture",
        "landholding": "marginal",
        "area": "Rural",
        "state": "Punjab",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["occupation"] == "farmer"
    assert payload["area"] == "Rural"
    assert payload["state"] == "Punjab"
    assert "Agriculture" in payload["needs"]


def test_user_journey_internship_training():
    """Verify complete user journey for Internship / Skill Training (Section 25)."""
    answers = {
        "intent": "skills",
        "skill_status": "student",
        "skill_sector": "it_digital",
        "social_category": "General",
        "state": "Karnataka",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["intent"] == "skills"
    assert payload["dynamic_answers"]["skill_status"] == "student"
    assert payload["dynamic_answers"]["skill_sector"] == "it_digital"
    assert payload["state"] == "Karnataka"
    assert "Employment & skills" in payload["needs"]


def test_user_journey_employment_worker():
    """Verify complete user journey for Employment & Jobs (Section 28)."""
    answers = {
        "intent": "jobs",
        "employment_status": "unemployed",
        "qualification": "12th_pass",
        "age": "24",
        "social_category": "SC",
        "area": "Rural",
        "state": "Bihar",
    }
    payload = questionnaire_engine.build_profile_payload(answers)
    assert payload["intent"] == "jobs"
    assert payload["occupation"] == "unemployed"
    assert payload["age"] == 24
    assert payload["state"] == "Bihar"
    assert payload["category"] == "SC"


def test_questionnaire_validation_cannot_advance_with_empty_required_field():
    """Verify Continue fails when required question is unanswered (Problem 2)."""
    state_q = next(q for q in questionnaire_engine.questions if q.id == "state")
    assert state_q.required is True

    # Empty None
    ok, msg = questionnaire_engine.validate_answer(state_q, None)
    assert ok is False
    assert "Please select your state to continue" in msg

    # Empty string
    ok, msg = questionnaire_engine.validate_answer(state_q, "")
    assert ok is False

    # Placeholder string
    ok, msg = questionnaire_engine.validate_answer(state_q, "Select your state...")
    assert ok is False

    # Valid state
    ok, msg = questionnaire_engine.validate_answer(state_q, "Uttar Pradesh")
    assert ok is True
    assert msg is None


def test_stale_conditional_answer_cleanup():
    """Verify Section 16 & 17 stale answers cleanup."""
    # User was on business existing, entered turnover, then switched to new_startup
    answers = {
        "intent": "business",
        "business_stage": "new_startup",
        "annual_turnover": "5_to_25lakh",  # Irrelevant for new_startup
        "employees_count": "1_to_5",        # Irrelevant for new_startup
        "state": "Maharashtra",
    }
    cleaned = questionnaire_engine.clean_stale_answers(answers)
    assert "annual_turnover" not in cleaned
    assert "employees_count" not in cleaned
    assert cleaned["business_stage"] == "new_startup"
    assert cleaned["state"] == "Maharashtra"
