"""Complete Backend API client for Streamlit frontend."""

import os
from typing import Any, Dict, List, Optional
import httpx

BACKEND_API_URL = os.getenv("BACKEND_API_URL") or os.getenv("API_BASE_URL", "http://localhost:8000")


def get_backend_api_url() -> str:
    """Dynamically resolves the backend API URL from env or Streamlit secrets."""
    url = os.getenv("BACKEND_API_URL") or os.getenv("API_BASE_URL")
    if url:
        return url
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "BACKEND_API_URL" in st.secrets:
                return str(st.secrets["BACKEND_API_URL"])
            if "API_BASE_URL" in st.secrets:
                return str(st.secrets["API_BASE_URL"])
    except Exception:
        pass
    return "http://localhost:8000"


class APIClient:
    """Client for communicating with the Yojana Sahayak FastAPI backend."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 15.0):
        self._custom_base_url = base_url
        self.timeout = timeout

    @property
    def base_url(self) -> str:
        if self._custom_base_url:
            return self._custom_base_url.rstrip("/")
        return get_backend_api_url().rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method=method, url=url, params=params, json=json_data)
                response.raise_for_status()
                return {
                    "ok": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "error": None,
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "status_code": None,
                "data": None,
                "error": f"Cannot connect to backend at {self.base_url}. Ensure the FastAPI service is running.",
            }
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            try:
                detail = exc.response.json().get("detail", detail)
            except Exception:
                pass
            return {
                "ok": False,
                "status_code": exc.response.status_code,
                "data": None,
                "error": f"HTTP {exc.response.status_code}: {detail}",
            }
        except Exception as exc:
            return {
                "ok": False,
                "status_code": None,
                "data": None,
                "error": f"Request failed: {str(exc)}",
            }

    # Health
    def check_health(self) -> Dict[str, Any]:
        return self._request("GET", "/api/health")

    # Schemes
    def list_schemes(
        self,
        q: Optional[str] = None,
        category: Optional[str] = None,
        ministry: Optional[str] = None,
        state: Optional[str] = None,
        level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        if category and category != "ALL":
            params["category"] = category
        if ministry and ministry != "ALL":
            params["ministry"] = ministry
        if state and state != "ALL":
            params["state"] = state
        if level and level != "ALL":
            params["level"] = level
        return self._request("GET", "/api/schemes", params=params)

    def get_featured_schemes(self, limit: int = 5) -> Dict[str, Any]:
        return self._request("GET", "/api/schemes/featured", params={"limit": limit})

    def get_scheme_stats(self) -> Dict[str, Any]:
        return self._request("GET", "/api/schemes/stats")

    def get_scheme_statistics(self) -> Dict[str, Any]:
        return self._request("GET", "/api/schemes/statistics")

    def get_scheme_categories(self) -> Dict[str, Any]:
        return self._request("GET", "/api/schemes/categories")

    def get_scheme_states(self) -> Dict[str, Any]:
        return self._request("GET", "/api/schemes/states")

    def get_scheme(self, slug_or_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/schemes/{slug_or_id}")

    # Matching Engine
    def match_schemes(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/api/schemes/match", json_data=profile)

    # Citizen Profile
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        res = self._request("GET", "/api/profile", params={"user_id": user_id})
        if res.get("ok"):
            return res
        # Fallback to direct DB
        from frontend.services.scheme_data import get_user_profile_db
        prof = get_user_profile_db(user_id=user_id)
        if prof:
            return {"ok": True, "data": prof}
        return {"ok": False, "data": None, "error": "Profile not found"}

    def upsert_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._request("POST", "/api/profile", json_data=profile_data)
        if res.get("ok"):
            return res
        # Fallback to direct DB
        from frontend.services.scheme_data import upsert_user_profile_db
        return upsert_user_profile_db(profile_data)

    # Saved Schemes
    def list_saved(self, user_id: str) -> Dict[str, Any]:
        return self._request("GET", "/api/saved", params={"user_id": user_id})

    def save_scheme(self, scheme_id: str, user_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/api/saved/{scheme_id}", params={"user_id": user_id})

    def remove_saved_scheme(self, scheme_id: str, user_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/api/saved/{scheme_id}", params={"user_id": user_id})

    # Application Tracking & My Applications
    def list_tracking(self, user_id: str) -> Dict[str, Any]:
        res = self._request("GET", "/api/applications", params={"user_id": user_id})
        if res.get("ok"):
            return res
        # Fallback to direct DB
        from frontend.services.scheme_data import get_user_applications_db
        db_entries = get_user_applications_db(user_id=user_id)
        return {"ok": True, "data": db_entries}

    def create_tracking(
        self, user_id: str, scheme_id: str, status: str = "Saved", notes: str = ""
    ) -> Dict[str, Any]:
        payload = {"user_id": user_id, "scheme_id": scheme_id, "status": status, "notes": notes}
        res = self._request("POST", "/api/applications", json_data=payload)
        if res.get("ok"):
            return res
        # Fallback to direct DB
        from frontend.services.scheme_data import add_user_application_db
        return add_user_application_db(user_id=user_id, scheme_id=scheme_id, status=status, notes=notes)

    def update_tracking(
        self, tracking_id: str, user_id: str = "", status: Optional[str] = None, notes: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if status:
            payload["status"] = status
        if notes is not None:
            payload["notes"] = notes
        params = {"user_id": user_id} if user_id else {}
        res = self._request("PATCH", f"/api/applications/{tracking_id}", params=params, json_data=payload)
        if res.get("ok"):
            return res
        # Fallback to direct DB
        from frontend.services.scheme_data import update_user_application_status_db
        updated = update_user_application_status_db(tracking_id=tracking_id, user_id=user_id, status=status or "Saved", notes=notes)
        return {"ok": updated}

    def delete_tracking(self, tracking_id: str, user_id: str = "") -> Dict[str, Any]:
        params = {"user_id": user_id} if user_id else {}
        res = self._request("DELETE", f"/api/applications/{tracking_id}", params=params)
        if res.get("ok"):
            return res
        # Fallback to direct DB
        from frontend.services.scheme_data import delete_user_application_db
        deleted = delete_user_application_db(tracking_id=tracking_id, user_id=user_id)
        return {"ok": deleted}

    def is_in_applications(self, user_id: str, scheme_id: str) -> bool:
        from frontend.services.scheme_data import is_scheme_in_applications_db
        return is_scheme_in_applications_db(user_id=user_id, scheme_id=scheme_id)

    # AI Service
    def explain_eligibility(
        self,
        match_result: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        language: str = "en",
        scheme_id: Optional[str] = None,
        scheme_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"language": language}
        if match_result:
            payload["match_result"] = match_result
        if user_profile:
            payload["user_profile"] = user_profile
        if scheme_id:
            payload["scheme_id"] = scheme_id
        if scheme_slug:
            payload["scheme_slug"] = scheme_slug
        return self._request("POST", "/api/ai/explain", json_data=payload)

    def ask_ai(
        self,
        question: str,
        language: str = "en",
        category: Optional[str] = None,
        scheme_id: Optional[str] = None,
        scheme_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"question": question, "language": language}
        if category:
            payload["category"] = category
        if scheme_id:
            payload["scheme_id"] = scheme_id
        if scheme_slug:
            payload["scheme_slug"] = scheme_slug
        return self._request("POST", "/api/ai/ask", json_data=payload)

    # Admin Dashboard
    def admin_list_schemes(self) -> Dict[str, Any]:
        return self._request("GET", "/api/admin/schemes")

    def admin_create_scheme(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/api/admin/schemes", json_data=payload)

    def admin_update_scheme(self, scheme_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/api/admin/schemes/{scheme_id}", json_data=payload)

    def admin_sync(self) -> Dict[str, Any]:
        return self._request("POST", "/api/admin/sync")

    def admin_sync_logs(self) -> Dict[str, Any]:
        return self._request("GET", "/api/admin/sync-logs")


api_client = APIClient()
