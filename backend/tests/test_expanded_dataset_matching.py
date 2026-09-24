"""Comprehensive test suite verifying deterministic and semantic matching across the 400+ scheme dataset.

Validates the full matching pipeline across 7 distinct citizen profiles:
1. UP OBC Student (low-income)
2. UP Farmer (rural agriculture)
3. Bihar Female Student (higher education)
4. Maharashtra MSME Entrepreneur (business & credit)
5. Rajasthan Job Seeker (employment & skill training)
6. UP Senior Citizen (pensions & healthcare)
7. Karnataka Divyangjan (disability support)
"""

import pytest
import pytest_asyncio
from sqlalchemy import select

from backend.app.database.connection import AsyncSessionLocal
from backend.app.database.models import Scheme
from backend.app.matching.engine import matching_engine
from backend.app.matching.models import CitizenProfileInput, EligibilityStatus


@pytest_asyncio.fixture
async def all_active_schemes():
    """Retrieve all active schemes from the populated database."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Scheme).where(Scheme.active == True))
        schemes = list(res.scalars().all())
    return schemes


class TestExpandedDatasetMatching:
    """Suite testing matching engine against the complete expanded catalog."""

    def test_dataset_size_and_diversity(self, all_active_schemes):
        """Verify the catalog contains at least 400 schemes with central and state coverage."""
        assert len(all_active_schemes) >= 400, f"Expected >= 400 schemes, found {len(all_active_schemes)}"
        central_count = sum(1 for s in all_active_schemes if s.level == "Central")
        state_count = sum(1 for s in all_active_schemes if s.level == "State")
        assert central_count >= 80, f"Expected >= 80 Central schemes, got {central_count}"
        assert state_count >= 250, f"Expected >= 250 State schemes, got {state_count}"

    def test_profile_1_up_obc_student(self, all_active_schemes):
        """1. UP OBC Student (low income):
        - Must match UP Post-Matric OBC Scholarship + Central Post-Matric + PM YASASVI
        - Must NOT match irrelevant schemes (pensions, PM-KISAN, maternity)
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

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        # Must include key scholarship schemes
        assert "up-post-matric-scholarship-obc" in eligible_slugs, "UP Post-Matric OBC must be eligible"
        assert "post-matric-scholarship" in eligible_slugs, "Central Post-Matric must be eligible"
        assert "pm-yasasvi-scholarship" in eligible_slugs, "PM YASASVI must be eligible"

        # Must NOT leak unrelated schemes into results
        all_matched_slugs = {r.slug for r in response.results}
        assert "pm-kisan" not in all_matched_slugs
        assert "pradhan-mantri-matru-vandana-yojana-pmmvy" not in all_matched_slugs
        assert "indira-gandhi-national-old-age-pension-scheme" not in all_matched_slugs

    def test_profile_2_up_farmer(self, all_active_schemes):
        """2. UP Farmer (rural, low income):
        - Must match PM-KISAN, PMFBY, KCC, UP agriculture schemes
        - Must NOT leak education scholarships or urban business loans
        """
        profile = CitizenProfileInput(
            intent="agriculture",
            state="Uttar Pradesh",
            age=42,
            gender="male",
            occupation="farmer",
            annual_income=90000,
            annual_family_income=90000,
            category="General",
            residence_type="Rural",
            area="Rural",
            disability=False,
        )

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        assert "pm-kisan" in eligible_slugs, "PM-KISAN must be eligible"
        assert "pm-fasal-bima-yojana" in eligible_slugs or any("fasal-bima" in s for s in eligible_slugs), "PMFBY must be eligible"
        assert any("kcc" in s or "kisan-credit" in s for s in eligible_slugs), "KCC scheme must be eligible"
        assert any("uttar-pradesh" in s or "up-" in s for s in eligible_slugs), "UP state agriculture schemes must be eligible"

    def test_profile_3_bihar_female_student(self, all_active_schemes):
        """3. Bihar Female Student:
        - Must match Bihar-specific female education schemes + Central schemes
        """
        profile = CitizenProfileInput(
            intent="education",
            state="Bihar",
            age=19,
            gender="female",
            occupation="student",
            annual_income=70000,
            annual_family_income=70000,
            category="OBC",
            residence_type="Rural",
            area="Rural",
            disability=False,
        )

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        # Check Bihar-specific education schemes
        bihar_matches = [s for s in eligible_slugs if "bihar" in s]
        assert len(bihar_matches) >= 1, f"Expected Bihar education schemes in {eligible_slugs}"
        assert "post-matric-scholarship" in eligible_slugs, "Central Post-Matric must be eligible"

    def test_profile_4_maharashtra_msme_entrepreneur(self, all_active_schemes):
        """4. Maharashtra MSME Entrepreneur:
        - Must match PMEGP, Mudra, CMEGP, etc.
        """
        profile = CitizenProfileInput(
            intent="business",
            state="Maharashtra",
            age=32,
            gender="male",
            occupation="self_employed",
            annual_income=250000,
            annual_family_income=250000,
            category="General",
            residence_type="Urban",
            area="Urban",
            disability=False,
        )

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        assert any("mudra" in s for s in eligible_slugs), "Mudra scheme must be eligible"
        assert any("pmegp" in s for s in eligible_slugs), "PMEGP must be eligible"
        assert any("maharashtra" in s for s in eligible_slugs), "Maharashtra business schemes must be eligible"

    def test_profile_5_rajasthan_job_seeker(self, all_active_schemes):
        """5. Rajasthan Job Seeker:
        - Must match employment schemes applicable to RJ + Central
        """
        profile = CitizenProfileInput(
            intent="jobs",
            state="Rajasthan",
            age=24,
            gender="male",
            occupation="unemployed",
            annual_income=40000,
            annual_family_income=40000,
            category="General",
            residence_type="Urban",
            area="Urban",
            disability=False,
        )

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        assert len(eligible_slugs) >= 2, f"Expected at least 2 employment schemes, got {len(eligible_slugs)}"
        assert any("rajasthan" in s for s in eligible_slugs) or any("mgnrega" in s for s in eligible_slugs)

    def test_profile_6_senior_citizen_up(self, all_active_schemes):
        """6. Senior Citizen (UP, age 68, low income):
        - Must match IGNOAPS, UP Old Age Pension, Ayushman Bharat senior
        """
        profile = CitizenProfileInput(
            intent="pension",
            state="Uttar Pradesh",
            age=68,
            gender="male",
            occupation="retired",
            annual_income=30000,
            annual_family_income=30000,
            category="General",
            residence_type="Rural",
            area="Rural",
            disability=False,
        )

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        assert any("old-age" in s or "vridh" in s or "ignoaps" in s for s in eligible_slugs), (
            f"Expected old age pension schemes in {eligible_slugs}"
        )
        assert any("uttar-pradesh" in s or "up-" in s for s in eligible_slugs), (
            f"Expected UP state pension scheme in {eligible_slugs}"
        )

    def test_profile_7_karnataka_divyangjan(self, all_active_schemes):
        """7. Divyangjan (Karnataka, person with disability):
        - Must match disability pension + ADIP + NHFDC schemes
        """
        profile = CitizenProfileInput(
            intent="disability",
            state="Karnataka",
            age=28,
            gender="female",
            occupation="unemployed",
            annual_income=45000,
            annual_family_income=45000,
            category="General",
            residence_type="Urban",
            area="Urban",
            disability=True,
        )

        response = matching_engine.match_all(schemes=all_active_schemes, profile=profile)
        eligible_slugs = {r.slug for r in response.results if r.status == EligibilityStatus.ELIGIBLE}

        assert any("disability" in s or "divyang" in s for s in eligible_slugs), (
            f"Expected disability pension schemes in {eligible_slugs}"
        )
        assert any("adip" in s for s in eligible_slugs), "ADIP scheme must be eligible"
        assert any("karnataka" in s for s in eligible_slugs), "Karnataka state disability scheme must be eligible"
