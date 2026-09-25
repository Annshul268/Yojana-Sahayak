"""Integration tests for My Applications REST API endpoints and user isolation."""

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
async def test_applications_lifecycle_and_user_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get a valid scheme
        s_res = await client.get("/api/schemes?limit=2")
        assert s_res.status_code == 200
        schemes = s_res.json()["items"]
        scheme_1 = schemes[0]["id"]
        scheme_2 = schemes[1]["id"]

        user_a = "test_user_alpha"
        user_b = "test_user_beta"

        # Clean existing test entries if any
        res_a_init = await client.get(f"/api/applications?user_id={user_a}")
        for item in res_a_init.json():
            await client.delete(f"/api/applications/{item['id']}?user_id={user_a}")

        res_b_init = await client.get(f"/api/applications?user_id={user_b}")
        for item in res_b_init.json():
            await client.delete(f"/api/applications/{item['id']}?user_id={user_b}")

        # 1. User A adds scheme_1
        post_res = await client.post(
            "/api/applications",
            json={"user_id": user_a, "scheme_id": scheme_1, "status": "Saved", "notes": "Test notes"},
        )
        assert post_res.status_code == 200
        app_record = post_res.json()
        assert app_record["user_id"] == user_a
        assert app_record["scheme_id"] == scheme_1
        assert app_record["status"] == "Saved"
        app_id = app_record["id"]

        # 2. Duplicate prevention: adding same scheme again returns existing without duplicate
        dup_res = await client.post(
            "/api/applications",
            json={"user_id": user_a, "scheme_id": scheme_1, "status": "Saved"},
        )
        assert dup_res.status_code == 200
        assert dup_res.json()["id"] == app_id

        get_a = await client.get(f"/api/applications?user_id={user_a}")
        assert get_a.status_code == 200
        assert len(get_a.json()) == 1

        # 3. User Isolation: User B cannot see User A's applications
        get_b = await client.get(f"/api/applications?user_id={user_b}")
        assert get_b.status_code == 200
        assert len(get_b.json()) == 0

        # 4. Update status to Applied - verify applied_at is set
        patch_res = await client.patch(
            f"/api/applications/{app_id}?user_id={user_a}",
            json={"status": "Applied"},
        )
        assert patch_res.status_code == 200
        updated = patch_res.json()
        assert updated["status"] == "Applied"
        assert updated["applied_at"] is not None

        # 5. User Isolation on update: User B cannot modify User A's application
        unauth_patch = await client.patch(
            f"/api/applications/{app_id}?user_id={user_b}",
            json={"status": "Completed"},
        )
        assert unauth_patch.status_code == 403

        # 6. User Isolation on delete: User B cannot delete User A's application
        unauth_del = await client.delete(f"/api/applications/{app_id}?user_id={user_b}")
        assert unauth_del.status_code in (403, 404)

        # 7. User A deletes their application
        del_res = await client.delete(f"/api/applications/{app_id}?user_id={user_a}")
        assert del_res.status_code == 200

        get_a_after = await client.get(f"/api/applications?user_id={user_a}")
        assert len(get_a_after.json()) == 0

        # 8. Scheme in schemes table still exists
        scheme_check = await client.get(f"/api/schemes/{schemes[0]['slug']}")
        assert scheme_check.status_code == 200
