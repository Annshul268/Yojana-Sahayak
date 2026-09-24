"""Verification tests for Scheme Discovery API, Featured Schemes Carousel, and Dynamic Statistics."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.app.database.connection import AsyncSessionLocal, init_db
from backend.app.database.models import Scheme
from backend.app.main import app
from sqlalchemy import func, select


@pytest_asyncio.fixture
async def client():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_featured_schemes_carousel_endpoint(client):
    """Verify /api/schemes/featured returns verified flagship schemes with valid URLs."""
    res = await client.get("/api/schemes/featured?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5, f"Expected at least 5 featured schemes, got {len(data)}"

    for item in data:
        assert item.get("name"), "Featured scheme must have a name"
        assert item.get("category"), "Featured scheme must have a category"
        assert item.get("level") in ("Central", "State"), "Level must be Central or State"
        url = item.get("official_url")
        assert url and url.startswith("http"), f"Must have valid official government URL, got {url}"
        assert item.get("verification_status") == "Verified"


@pytest.mark.asyncio
async def test_scheme_stats_dynamic_calculation(client):
    """Verify /api/schemes/stats calculates actual metrics from database records."""
    res = await client.get("/api/schemes/stats")
    assert res.status_code == 200
    data = res.json()

    # Query DB directly to check accuracy
    async with AsyncSessionLocal() as db:
        tot_res = await db.execute(select(func.count(Scheme.id)).where(Scheme.active == True))
        actual_total = tot_res.scalar()

    assert data["total"] == actual_total
    assert data["central"] + data["state"] == actual_total
    assert data["total"] >= 400
    assert data["central"] >= 100
    assert data["state"] >= 300

    # Ensure categories dict is populated and matches counts
    categories = data["categories"]
    assert "Education & Learning" in categories
    assert categories["Education & Learning"] >= 50
    assert sum(categories.values()) == actual_total

    # Ensure states dict is populated
    states = data["states"]
    assert "Uttar Pradesh" in states
    assert states["Uttar Pradesh"] >= 25


@pytest.mark.asyncio
async def test_categories_endpoint(client):
    """Verify /api/schemes/categories returns list with icons and counts."""
    res = await client.get("/api/schemes/categories")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10, f"Expected at least 10 categories, got {len(data)}"

    for cat in data:
        assert "name" in cat
        assert "count" in cat and cat["count"] > 0
        assert "icon" in cat
        assert "name_hi" in cat


@pytest.mark.asyncio
async def test_states_endpoint(client):
    """Verify /api/schemes/states returns states list with central and state counts."""
    res = await client.get("/api/schemes/states")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 20, f"Expected >= 20 states, got {len(data)}"

    for st in data:
        assert "state" in st
        assert "state_count" in st
        assert "central_count" in st
        assert "total_applicable" in st
        assert st["total_applicable"] == st["state_count"] + st["central_count"]

    # Check Uttar Pradesh specifically
    up_data = next((s for s in data if s["state"] == "Uttar Pradesh"), None)
    assert up_data is not None
    assert up_data["state_count"] == 31
    assert up_data["central_count"] == 109
    assert up_data["total_applicable"] == 140


@pytest.mark.asyncio
async def test_state_filter_returns_central_plus_state(client):
    """CRITICAL: Selecting a state must return Central schemes + state's specific schemes."""
    res = await client.get("/api/schemes?state=Uttar%20Pradesh&page_size=100")
    assert res.status_code == 200
    data = res.json()
    total = data["total"]
    items = data["items"]

    assert total == 140, f"Expected 140 applicable schemes for Uttar Pradesh, got {total}"
    assert len(items) > 0

    for item in items:
        level = item["level"]
        states = [str(x).upper() for x in (item.get("states") or [])]
        is_central = level == "Central" or "ALL" in states
        is_up = "UTTAR PRADESH" in states
        assert is_central or is_up, f"Scheme {item['slug']} ({states}) should not be in UP results"


@pytest.mark.asyncio
async def test_category_filter(client):
    """Selecting a category must return only schemes belonging to that category."""
    res = await client.get("/api/schemes?category=Healthcare&page_size=50")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 40
    for item in data["items"]:
        assert item["category"] == "Healthcare"
