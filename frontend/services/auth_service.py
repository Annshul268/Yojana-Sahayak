"""Citizen Authentication Service for Yojana Sahayak.

Supports realistic email/password authentication with secure password hashing (bcrypt / PBKDF2),
profile synchronization, and optional Supabase Auth integration.
"""

from datetime import datetime, timezone
import hashlib
import logging
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, Optional, Tuple
import uuid

from frontend.services.scheme_data import (
    find_db_path,
    upsert_user_profile_db,
    get_user_profile_db,
    ensure_database_schema,
)

logger = logging.getLogger("yojana_sahayak.auth")


def get_env_or_secret(key: str, default: str = "") -> str:
    """Resolve environment variable or Streamlit secret safely."""
    val = os.environ.get(key, "").strip()
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if key in st.secrets:
                return str(st.secrets[key]).strip()
            if key.lower() in st.secrets:
                return str(st.secrets[key.lower()]).strip()
            # Support nested [supabase] section
            if "supabase" in st.secrets and isinstance(st.secrets["supabase"], dict):
                sub_key = key.replace("SUPABASE_", "").lower()
                if sub_key in st.secrets["supabase"]:
                    return str(st.secrets["supabase"][sub_key]).strip()
                if key in st.secrets["supabase"]:
                    return str(st.secrets["supabase"][key]).strip()
    except Exception:
        pass
    return default


def hash_password(password: str) -> str:
    """Hash password securely using bcrypt if available, with PBKDF2-SHA256 fallback."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except Exception:
        salt = os.urandom(16).hex()
        pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return f"pbkdf2_sha256${salt}${pw_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against stored hash."""
    if not password or not hashed:
        return False
    try:
        if hashed.startswith("pbkdf2_sha256$"):
            parts = hashed.split("$")
            if len(parts) == 3:
                salt, pw_hash = parts[1], parts[2]
                check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
                return check == pw_hash
        import bcrypt
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def ensure_auth_table() -> bool:
    """Ensure the auth_users table exists in SQLite database."""
    db_path = find_db_path(create_if_missing=True)
    if not db_path:
        return False
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at DATETIME,
                updated_at DATETIME
            )
            """
        )
        conn.commit()
        conn.close()
        return True
    except Exception as exc:
        logger.error(f"[AUTH] Error creating auth_users table: {exc}")
        return False


class AuthService:
    """Manages citizen registration, login, and profile binding."""

    def __init__(self) -> None:
        ensure_auth_table()

    @property
    def supabase_url(self) -> str:
        return get_env_or_secret("SUPABASE_URL")

    @property
    def supabase_key(self) -> str:
        return get_env_or_secret("SUPABASE_ANON_KEY") or get_env_or_secret("SUPABASE_KEY")

    @property
    def supabase_service_role_key(self) -> str:
        return get_env_or_secret("SUPABASE_SERVICE_ROLE_KEY")

    def is_supabase_configured(self) -> bool:
        url = self.supabase_url
        key = self.supabase_key
        return bool(url and key and "your-project" not in url)

    def register_user(
        self,
        name: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Registers a new citizen account with realistic validation."""
        clean_name = (name or "").strip()
        clean_email = (email or "").strip().lower()

        if not clean_name:
            return False, "Please enter your name.", None

        if not clean_email or not validate_email(clean_email):
            return False, "Please enter a valid email address.", None

        if not password:
            return False, "Please enter a password.", None

        if len(password) < 6:
            return False, "Password must be at least 6 characters.", None

        if password != confirm_password:
            return False, "Passwords do not match.", None

        # Check if Supabase Auth is configured and active
        if self.is_supabase_configured():
            logger.info("[AUTH] signup started")
            print("[AUTH] signup started")
            try:
                import requests
                resp = requests.post(
                    f"{self.supabase_url}/auth/v1/signup",
                    headers={"apikey": self.supabase_key, "Content-Type": "application/json"},
                    json={"email": clean_email, "password": password, "data": {"name": clean_name}},
                    timeout=8.0,
                )
                logger.info(f"[AUTH] signup response received: status={resp.status_code}")
                print(f"[AUTH] signup response received: status={resp.status_code}")

                if resp.status_code in (200, 201):
                    data = resp.json()
                    user = data.get("user") if isinstance(data.get("user"), dict) else data
                    user_id = user.get("id") or str(uuid.uuid4())
                    access_token = data.get("access_token")
                    logger.info(f"[AUTH] user created: {user_id}")
                    print(f"[AUTH] user created: {user_id}")

                    # Attempt profile insertion in Supabase
                    logger.info("[PROFILE] insert started")
                    print("[PROFILE] insert started")
                    now_iso = datetime.now(timezone.utc).isoformat()
                    prof_payload = {
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "name": clean_name,
                        "created_at": now_iso,
                        "updated_at": now_iso,
                    }
                    prof_headers = {
                        "apikey": self.supabase_key,
                        "Content-Type": "application/json",
                        "Prefer": "resolution=merge-duplicates,return=representation",
                    }
                    if access_token:
                        prof_headers["Authorization"] = f"Bearer {access_token}"
                    elif self.supabase_service_role_key:
                        prof_headers["Authorization"] = f"Bearer {self.supabase_service_role_key}"
                    else:
                        prof_headers["Authorization"] = f"Bearer {self.supabase_key}"

                    try:
                        prof_resp = requests.post(
                            f"{self.supabase_url}/rest/v1/profiles",
                            headers=prof_headers,
                            json=prof_payload,
                            timeout=5.0,
                        )
                        logger.info(f"[PROFILE] status: {prof_resp.status_code}")
                        print(f"[PROFILE] status: {prof_resp.status_code}")
                        if prof_resp.status_code not in (200, 201, 204):
                            safe_err = prof_resp.text[:200].replace("\n", " ")
                            logger.warning(f"[PROFILE] insert failed: status={prof_resp.status_code}, error={safe_err}")
                            print(f"[PROFILE] insert failed: status={prof_resp.status_code}, error={safe_err}")
                        else:
                            logger.info(f"[PROFILE] insert succeeded: status={prof_resp.status_code}")
                            print(f"[PROFILE] insert succeeded: status={prof_resp.status_code}")
                    except Exception as prof_exc:
                        logger.warning(f"[PROFILE] insert failed: error={type(prof_exc).__name__}")
                        print(f"[PROFILE] insert failed: error={type(prof_exc).__name__}")

                    # Also cache profile locally in SQLite
                    upsert_user_profile_db({"user_id": user_id, "name": clean_name})

                    return True, "Account created successfully!", {"user_id": user_id, "email": clean_email, "name": clean_name}

                elif resp.status_code >= 400:
                    err_msg = ""
                    try:
                        err_json = resp.json()
                        err_msg = (
                            err_json.get("msg")
                            or err_json.get("message")
                            or err_json.get("error_description")
                            or ""
                        )
                    except Exception:
                        err_msg = resp.text[:200]

                    logger.warning(f"[AUTH] signup error: status={resp.status_code}, message={err_msg}")
                    print(f"[AUTH] signup error: status={resp.status_code}, message={err_msg}")

                    if "already registered" in err_msg.lower() or "already exists" in err_msg.lower():
                        return False, "An account with this email already exists. Try signing in instead.", None
                    if "password" in err_msg.lower():
                        return False, f"Password requirement: {err_msg}", None
                    if "rate limit" in err_msg.lower():
                        return False, "Rate limit reached. Please wait a few moments and try again.", None
                    if err_msg:
                        return False, f"Account creation failed: {err_msg}", None
                    return False, f"Account creation failed (status {resp.status_code}). Please try again.", None

            except requests.exceptions.RequestException as req_exc:
                logger.warning(f"[AUTH] Supabase network error: {type(req_exc).__name__}")
                print(f"[AUTH] Supabase network error: {type(req_exc).__name__}")
                # Fall back to local store if Supabase server is unreachable

        # Local secure database registration
        db_path = find_db_path(create_if_missing=True)
        if not db_path:
            return False, "Local database storage unavailable. Please check system permissions.", None

        ensure_auth_table()
        ensure_database_schema(db_path)
        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM auth_users WHERE email = ? LIMIT 1", (clean_email,))
            if cursor.fetchone():
                conn.close()
                return False, "An account with this email already exists. Try signing in instead.", None

            user_id = str(uuid.uuid4())
            pw_hash = hash_password(password)
            now_iso = datetime.now(timezone.utc).isoformat()

            cursor.execute(
                """
                INSERT INTO auth_users (id, email, password_hash, name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, clean_email, pw_hash, clean_name, now_iso, now_iso),
            )
            conn.commit()
            conn.close()

            # Ensure profile row is created for the real user ID
            upsert_user_profile_db({"user_id": user_id, "name": clean_name})

            logger.info(f"[AUTH] local user registered: {user_id}")
            print(f"[AUTH] local user registered: {user_id}")
            return True, "Account created successfully!", {"user_id": user_id, "email": clean_email, "name": clean_name}
        except Exception as e:
            logger.error(f"[DB] Registration failed with SQLite error: {e}")
            print(f"[DB] Registration failed with SQLite error: {e}")
            return False, f"Registration failed: {str(e)}", None

    def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticates citizen with email and password."""
        clean_email = (email or "").strip().lower()
        if not clean_email or not validate_email(clean_email):
            return False, "Please enter a valid email address.", None

        if not password:
            return False, "Please enter your password.", None

        # Check Supabase Auth if configured
        if self.is_supabase_configured():
            logger.info("[AUTH] signin started")
            print("[AUTH] signin started")
            try:
                import requests
                resp = requests.post(
                    f"{self.supabase_url}/auth/v1/token?grant_type=password",
                    headers={"apikey": self.supabase_key, "Content-Type": "application/json"},
                    json={"email": clean_email, "password": password},
                    timeout=8.0,
                )
                logger.info(f"[AUTH] signin response received: status={resp.status_code}")
                print(f"[AUTH] signin response received: status={resp.status_code}")

                if resp.status_code == 200:
                    data = resp.json()
                    user = data.get("user") or {}
                    user_id = user.get("id")
                    user_meta = user.get("user_metadata") or {}
                    name = user_meta.get("name") or user_meta.get("full_name") or "Citizen"

                    # Check if profile has updated name locally or via Supabase
                    prof = get_user_profile_db(user_id=user_id)
                    if prof and prof.get("name"):
                        name = prof.get("name")

                    return True, "Signed in successfully!", {"user_id": user_id, "email": clean_email, "name": name}
                elif resp.status_code >= 400:
                    err_msg = ""
                    try:
                        err_json = resp.json()
                        err_msg = (
                            err_json.get("msg")
                            or err_json.get("message")
                            or err_json.get("error_description")
                            or ""
                        )
                    except Exception:
                        err_msg = resp.text[:200]

                    if "invalid" in err_msg.lower() or "credentials" in err_msg.lower():
                        return False, "Incorrect email or password.", None
                    if "email not confirmed" in err_msg.lower():
                        return False, "Please confirm your email address before signing in.", None
                    if err_msg:
                        return False, err_msg, None
                    return False, "Incorrect email or password.", None
            except requests.exceptions.RequestException as req_exc:
                logger.warning(f"[AUTH] Supabase network error during signin: {type(req_exc).__name__}")
                print(f"[AUTH] Supabase network error during signin: {type(req_exc).__name__}")
                # Fall back to local store if Supabase is unreachable

        # Local secure database authentication
        db_path = find_db_path(create_if_missing=True)
        if not db_path:
            return False, "Local database storage unavailable. Please check system permissions.", None

        ensure_auth_table()
        ensure_database_schema(db_path)
        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password_hash, name FROM auth_users WHERE email = ? LIMIT 1", (clean_email,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return False, "Incorrect email or password.", None

            u_id, u_email, u_hash, u_name = row
            if not verify_password(password, u_hash):
                return False, "Incorrect email or password.", None

            # Check if profile has updated name
            prof = get_user_profile_db(user_id=u_id)
            if prof and prof.get("name"):
                u_name = prof.get("name")

            return True, "Signed in successfully!", {"user_id": u_id, "email": u_email, "name": u_name}
        except Exception as e:
            logger.error(f"[DB] Authentication failed with SQLite error: {e}")
            print(f"[DB] Authentication failed with SQLite error: {e}")
            return False, f"Authentication error: {str(e)}", None


auth_service = AuthService()
