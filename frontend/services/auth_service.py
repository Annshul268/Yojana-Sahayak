"""Citizen Authentication Service for Yojana Sahayak.

Supports realistic email/password authentication with secure password hashing (bcrypt / PBKDF2),
profile synchronization, and optional Supabase Auth integration.
"""

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, Optional, Tuple
import uuid

from frontend.services.scheme_data import find_db_path, upsert_user_profile_db, get_user_profile_db


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
    db_path = find_db_path()
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
    except Exception:
        return False


class AuthService:
    """Manages citizen registration, login, and profile binding."""

    def __init__(self) -> None:
        self.supabase_url = os.environ.get("SUPABASE_URL", "").strip()
        self.supabase_key = os.environ.get("SUPABASE_ANON_KEY", "").strip()
        ensure_auth_table()

    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key and "your-project" not in self.supabase_url)

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
            try:
                import requests
                resp = requests.post(
                    f"{self.supabase_url}/auth/v1/signup",
                    headers={"apikey": self.supabase_key, "Content-Type": "application/json"},
                    json={"email": clean_email, "password": password, "data": {"name": clean_name}},
                    timeout=5.0,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    user = data.get("user") or {}
                    user_id = user.get("id") or str(uuid.uuid4())
                    # Sync to profiles
                    upsert_user_profile_db({"user_id": user_id, "name": clean_name})
                    return True, "Account created successfully!", {"user_id": user_id, "email": clean_email, "name": clean_name}
                elif resp.status_code == 400 and "already registered" in resp.text.lower():
                    return False, "An account with this email already exists. Try signing in instead.", None
            except Exception:
                pass  # Fallback to local secure store

        # Local secure database registration
        db_path = find_db_path()
        if not db_path:
            return False, "Database not available. Please try again.", None

        ensure_auth_table()
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

            # Ensure empty profile row is created for the real user ID
            upsert_user_profile_db({"user_id": user_id, "name": clean_name})

            return True, "Account created successfully!", {"user_id": user_id, "email": clean_email, "name": clean_name}
        except Exception as e:
            return False, "Registration could not be completed. Please try again.", None

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
            try:
                import requests
                resp = requests.post(
                    f"{self.supabase_url}/auth/v1/token?grant_type=password",
                    headers={"apikey": self.supabase_key, "Content-Type": "application/json"},
                    json={"email": clean_email, "password": password},
                    timeout=5.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    user = data.get("user") or {}
                    user_id = user.get("id")
                    user_meta = user.get("user_metadata") or {}
                    name = user_meta.get("name") or "Citizen"
                    return True, "Signed in successfully!", {"user_id": user_id, "email": clean_email, "name": name}
            except Exception:
                pass  # Fallback to local store

        # Local secure database authentication
        db_path = find_db_path()
        if not db_path:
            return False, "Database not available. Please try again.", None

        ensure_auth_table()
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
        except Exception:
            return False, "Authentication service error. Please try again.", None


auth_service = AuthService()
