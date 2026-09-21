"""Integration tests for Scheme and Feature REST endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.database.connection import init_db
from backend.app.ingestion.seed import seed_database_if_empty
from backend.app.main import app


@pytest.fixture(autouse=True)
async def prepare_database():
    await init_db()
    await seed_database_if_empty()


@pytest.mark.asyncio
async def test_list_schemes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/schemes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 10
        assert len(data["items"]) >= 10


@pytest.mark.asyncio
async def test_search_schemes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/schemes?q=kisan")
        assert response.status_code == 200
        data = response.json()
        assert any("kisan" in s["slug"] for s in data["items"])


@pytest.mark.asyncio
async def test_get_scheme_by_slug():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/schemes/pm-kisan")
        assert response.status_code == 200
        scheme = response.json()
        assert scheme["slug"] == "pm-kisan"
        assert "Agriculture" in scheme["category"]
        assert scheme["official_url"] == "https://pmkisan.gov.in/"


@pytest.mark.asyncio
async def test_match_schemes_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "state": "Uttar Pradesh",
            "age": 40,
            "gender": "male",
            "annual_income": 120000,
            "occupation": "farmer",
            "category": "OBC",
            "area": "Rural",
            "disability": False,
        }
        response = await client.post("/api/schemes/match", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_schemes_evaluated"] >= 10
        assert data["eligible_count"] >= 1
        # PM Kisan should be among results
        slugs = [r["slug"] for r in data["results"] if r["status"] == "eligible"]
        assert "pm-kisan" in slugs


@pytest.mark.asyncio
async def test_profile_and_tracking_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_id = "test_user_qa_1"

        # 1. Upsert profile
        prof_payload = {
            "user_id": user_id,
            "name": "Ramesh Kumar",
            "state": "Madhya Pradesh",
            "age": 38,
            "gender": "Male",
            "annual_income": 180000,
            "occupation": "Farmer",
            "category": "OBC",
            "area": "Rural",
        }
        res_prof = await client.post("/api/profile", json=prof_payload)
        assert res_prof.status_code == 200
        assert res_prof.json()["name"] == "Ramesh Kumar"

        # 2. Get profile
        get_prof = await client.get(f"/api/profile?user_id={user_id}")
        assert get_prof.status_code == 200
        assert get_prof.json()["state"] == "Madhya Pradesh"

        # 3. Get a scheme ID
        s_res = await client.get("/api/schemes/pm-kisan")
        scheme_id = s_res.json()["id"]

        # 4. Save scheme
        save_res = await client.post(f"/api/saved/{scheme_id}?user_id={user_id}")
        assert save_res.status_code == 200

        # 5. List saved
        saved_list = await client.get(f"/api/saved?user_id={user_id}")
        assert saved_list.status_code == 200
        assert any(item["scheme_id"] == scheme_id for item in saved_list.json())

        # 6. Add tracking
        track_payload = {
            "user_id": user_id,
            "scheme_id": scheme_id,
            "status": "Planning to Apply",
            "notes": "Gathering Khasra-Khatauni records",
        }
        track_res = await client.post("/api/tracking", json=track_payload)
        assert track_res.status_code == 200
        tracking_id = track_res.json()["id"]

        # 7. Update tracking
        up_res = await client.put(
            f"/api/tracking/{tracking_id}",
            json={"status": "Applied", "notes": "Submitted at CSC with Ref 2026-991"},
        )
        assert up_res.status_code == 200
        assert up_res.json()["status"] == "Applied"

        # 8. Clean up saved
        del_res = await client.delete(f"/api/saved/{scheme_id}?user_id={user_id}")
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_ai_ask_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/ask",
            json={"question": "What is the official portal for PM-KISAN?", "language": "en"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 10


@pytest.mark.asyncio
async def test_get_intents_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/schemes/intents")
        assert response.status_code == 200
        intents = response.json()
        assert len(intents) >= 10
        assert any(i["id"] == "education" for i in intents)
