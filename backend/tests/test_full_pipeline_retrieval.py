"""Comprehensive verification tests for scheme ingestion, geographic scoping, and full retrieval pipeline."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from backend.app.database.connection import AsyncSessionLocal
from backend.app.database.models import Scheme
from backend.app.ingestion.sources.curated import CuratedSource
from backend.app.ingestion.validator import SchemeValidator
from backend.app.main import app
from backend.app.matching.engine import matching_engine
from backend.app.matching.models import CitizenProfileInput, EligibilityStatus
from backend.app.matching.taxonomy import is_geographically_applicable, match_intent_candidate_schemes
from sqlalchemy import select


@pytest_asyncio.fixture
async def active_schemes():
    """Load all active schemes from the populated database."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Scheme).where(Scheme.active == True))
        schemes = list(res.scalars().all())
    return schemes


class TestFullSchemeRetrievalPipeline:
    """End-to-end tests for scheme catalog, geographic scoping, and deterministic matching."""

    def test_curated_catalog_validation(self):
        """All schemes in the verified catalog must pass strict schema validation."""
        source = CuratedSource("data/processed/schemes.json")
        validator = SchemeValidator()
        import json
        with open("data/processed/schemes.json") as f:
            schemes = json.load(f)

        assert len(schemes) >= 40, f"Catalog should contain at least 40 schemes, found {len(schemes)}"
        
        for item in schemes:
            is_valid, errors = validator.validate(item)
            assert is_valid, f"Scheme '{item.get('slug')}' failed validation: {errors}"

    def test_target_case_education_scholarships_up_obc_student(self, active_schemes):
        """CRITICAL TEST CASE:
        Profile:
          Intent: Education & Scholarships
          State: Uttar Pradesh
          Age: 20
          Gender: Male
          Occupation: Student
          Income: ₹55,000
          Category: OBC
          Residence: Rural
          
        MUST return multiple valid education schemes (both Central and UP State)
        and MUST NOT return unrelated schemes like PM-KISAN, Ayushman Bharat, PMAY.
        """
        profile = CitizenProfileInput(
            intent="education",
            state="Uttar Pradesh",
            age=20,
            gender="male",
            occupation="student",
            annual_income=55000,
            annual_family_income=55000,
            category="OBC",
            residence_type="Rural",
            area="Rural",
            disability=False,
        )

        response = matching_engine.match_all(schemes=active_schemes, profile=profile)

        # 1. Candidate count must be realistic (not 1!)
        assert response.total_schemes_evaluated >= 10, (
            f"Expected at least 10 education candidate schemes evaluated, got {response.total_schemes_evaluated}"
        )

        # 2. Must return multiple eligible schemes
        assert response.eligible_count >= 5, (
            f"Expected at least 5 eligible schemes, got {response.eligible_count}"
        )

        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        # 3. Must include UP state-specific schemes
        assert "up-post-matric-scholarship-obc" in eligible_slugs, "UP Post-Matric Scholarship (OBC) must be eligible"
        assert "up-dashmottar-scholarship" in eligible_slugs, "UP Dashmottar Scholarship must be eligible"
        assert "up-mukhyamantri-abhyudaya" in eligible_slugs, "UP Mukhyamantri Abhyudaya must be eligible"

        # 4. Must include Central education schemes applicable to UP
        assert "post-matric-scholarship" in eligible_slugs, "Central Post-Matric Scholarship must be eligible"
        assert "pm-yasasvi-scholarship" in eligible_slugs, "PM YASASVI Scholarship must be eligible"
        assert "central-sector-scholarship-pm-usp" in eligible_slugs, "Central Sector Scholarship must be eligible"
        assert "vidya-lakshmi-csis" in eligible_slugs, "Vidya Lakshmi CSIS must be eligible"

        # 5. Must NOT contain unrelated sectors (agriculture, healthcare, housing, mudra)
        all_result_slugs = {r.slug for r in response.results}
        unrelated_slugs = {
            "pm-kisan",
            "ayushman-bharat-pmjay",
            "pm-awas-yojana-gramin",
            "pm-awas-yojana-urban",
            "pm-mudra-yojana",
            "pm-svanidhi",
            "mgnrega",
            "atal-pension-yojana",
        }
        leaked_schemes = all_result_slugs.intersection(unrelated_slugs)
        assert len(leaked_schemes) == 0, f"Unrelated schemes leaked into education results: {leaked_schemes}"

        # 6. Ineligible schemes must have valid disqualification reasons
        ineligible_map = {r.slug: r for r in response.results if r.status == EligibilityStatus.NOT_ELIGIBLE}
        if "aicte-pragati-scholarship" in ineligible_map:
            assert any("gender" in cond.lower() for cond in ineligible_map["aicte-pragati-scholarship"].failed_conditions)
        if "aicte-saksham-scholarship" in ineligible_map:
            assert any("disability" in cond.lower() or "pwd" in cond.lower() for cond in ineligible_map["aicte-saksham-scholarship"].failed_conditions)
        if "national-means-cum-merit-scholarship" in ineligible_map:
            assert any("age" in cond.lower() for cond in ineligible_map["national-means-cum-merit-scholarship"].failed_conditions)

    def test_geographic_applicability_filtering(self):
        """Central schemes apply everywhere; state schemes apply only in designated states."""
        class MockScheme:
            def __init__(self, slug, states, level="State"):
                self.slug = slug
                self.states = states
                self.level = level

        central_scheme = MockScheme("pm-kisan", ["ALL"], level="Central")
        up_scheme = MockScheme("up-scholarship", ["Uttar Pradesh"], level="State")
        mh_scheme = MockScheme("mh-scholarship", ["Maharashtra"], level="State")

        # Citizen in Uttar Pradesh
        assert is_geographically_applicable(central_scheme, "Uttar Pradesh") is True
        assert is_geographically_applicable(up_scheme, "Uttar Pradesh") is True
        assert is_geographically_applicable(mh_scheme, "Uttar Pradesh") is False

        # Citizen in Maharashtra
        assert is_geographically_applicable(central_scheme, "Maharashtra") is True
        assert is_geographically_applicable(up_scheme, "Maharashtra") is False
        assert is_geographically_applicable(mh_scheme, "Maharashtra") is True

        # Unspecified state explores all
        assert is_geographically_applicable(up_scheme, None) is True
        assert is_geographically_applicable(mh_scheme, "") is True

    @pytest.mark.asyncio
    async def test_matching_api_endpoint(self):
        """API POST /api/schemes/match must return full diagnostic fields and expected schemes."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "intent": "education",
                "state": "Uttar Pradesh",
                "age": 20,
                "gender": "male",
                "occupation": "student",
                "annual_income": 55000,
                "annual_family_income": 55000,
                "category": "OBC",
                "residence_type": "Rural",
                "area": "Rural",
                "disability": False,
            }
            res = await ac.post("/api/schemes/match", json=payload)
            assert res.status_code == 200
            data = res.json()

            assert data["total_schemes_evaluated"] >= 10
            assert data["eligible_count"] >= 5
            slugs = [r["slug"] for r in data["results"] if r["status"] == "eligible"]
            assert "up-post-matric-scholarship-obc" in slugs
            assert "pm-yasasvi-scholarship" in slugs

    @pytest.mark.asyncio
    async def test_admin_diagnostics_endpoint(self):
        """API GET /api/admin/diagnostics must report complete dataset distribution."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.get("/api/admin/diagnostics")
            assert res.status_code == 200
            data = res.json()

            assert data["total_schemes"] >= 40
            assert data["active_schemes"] >= 40
            assert "Central" in data["by_level"]
            assert "State" in data["by_level"]
            assert data["chromadb_documents"] >= 40
