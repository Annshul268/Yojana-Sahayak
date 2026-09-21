"""Backend API client for Streamlit frontend."""

import os
from typing import Any, Dict
import httpx

# Read from environment or default to local backend
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


class APIClient:
    """Client for communicating with the Yojana Sahayak FastAPI backend."""

    def __init__(self, base_url: str = BACKEND_API_URL, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        """Calls GET /api/health to verify backend operational readiness."""
        endpoint = f"{self.base_url}/api/health"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(endpoint)
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
                "error": f"Unable to connect to backend at {self.base_url}. Ensure the FastAPI server is running.",
            }
        except httpx.HTTPStatusError as exc:
            return {
                "ok": False,
                "status_code": exc.response.status_code,
                "data": None,
                "error": f"Backend returned HTTP error status: {exc.response.status_code}",
            }
        except Exception as exc:
            return {
                "ok": False,
                "status_code": None,
                "data": None,
                "error": f"An unexpected error occurred: {str(exc)}",
            }


# Singleton instance
api_client = APIClient()
