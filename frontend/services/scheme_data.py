"""Direct and resilient database service for Yojana Sahayak frontend.

Provides live scheme counts and statistics directly from the database (SQLite or PostgreSQL),
ensuring zero network latency and 100% availability even when the FastAPI backend service
is restarting or offline.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


def find_db_path() -> Optional[str]:
    """Locate the yojana_sahayak.db database file."""
    custom_path = os.getenv("SQLITE_DB_PATH")
    if custom_path and os.path.exists(custom_path):
        return custom_path

    candidates = [
        Path(__file__).resolve().parent.parent.parent / "yojana_sahayak.db",
        Path.cwd() / "yojana_sahayak.db",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def _find_schemes_json_path() -> Optional[Path]:
    """Locate the processed or seed schemes.json file bundled with the repository."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "schemes.json",
        Path(__file__).resolve().parent.parent.parent / "data" / "seed" / "schemes.json",
        Path.cwd() / "data" / "processed" / "schemes.json",
        Path.cwd() / "data" / "seed" / "schemes.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _get_fallback_statistics_from_json() -> Dict[str, Any]:
    """Calculate scheme metrics dynamically from bundled schemes.json when DB is unavailable."""
    json_path = _find_schemes_json_path()
    if not json_path:
        return {
            "ok": False,
            "total": 0,
            "central": 0,
            "state": 0,
            "categories": {},
            "raw_categories": {},
            "category_items": [],
            "states": [],
            "ministries": [],
            "error": "Neither database file nor schemes.json could be found",
            "db_source": "None",
        }

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)

        total = len(schemes)
        central = sum(1 for s in schemes if (s.get("level") or "").capitalize() == "Central")
        state = sum(1 for s in schemes if (s.get("level") or "").capitalize() == "State")

        raw_cat_counts: Dict[str, int] = {}
        state_counts: Dict[str, int] = {}
        ministry_counts: Dict[str, int] = {}

        for s in schemes:
            cat = s.get("category", "Other")
            raw_cat_counts[cat] = raw_cat_counts.get(cat, 0) + 1

            for st in (s.get("states") or []):
                st_clean = str(st).strip()
                if st_clean and st_clean.upper() != "ALL":
                    state_counts[st_clean] = state_counts.get(st_clean, 0) + 1

            min_name = s.get("ministry")
            if min_name and (s.get("level") or "").capitalize() == "Central":
                ministry_counts[min_name] = ministry_counts.get(min_name, 0) + 1

        category_catalog = [
            ("Education & Learning", "Education & Learning", "🎓", "शिक्षा एवं ज्ञान", raw_cat_counts.get("Education & Learning", 0)),
            ("Health & Wellness", "Healthcare", "🏥", "स्वास्थ्य एवं कल्याण", raw_cat_counts.get("Healthcare", 0)),
            ("Agriculture, Rural & Environment", "Agriculture & Rural Development", "🌾", "कृषि, ग्रामीण एवं पर्यावरण", raw_cat_counts.get("Agriculture & Rural Development", 0)),
            ("Business & Entrepreneurship", "Business & Self Employment", "📈", "व्यवसाय एवं उद्यमिता", raw_cat_counts.get("Business & Self Employment", 0)),
            ("Skills & Employment", "Employment & Skills", "💼", "कौशल एवं रोजगार", raw_cat_counts.get("Employment & Skills", 0)),
            ("Housing & Shelter", "Housing & Shelter", "🏠", "आवास एवं आश्रय", raw_cat_counts.get("Housing & Shelter", 0)),
            ("Social Welfare & Empowerment", "Social Security & Pension", "👴", "सामाजिक कल्याण एवं पेंशन", raw_cat_counts.get("Social Security & Pension", 0)),
            ("Women & Child Development", "Women & Child Development", "👩‍👧", "महिला एवं बाल विकास", raw_cat_counts.get("Women & Child Development", 0)),
            ("Differently Abled Support", "Differently Abled Support", "♿", "दिव्यांगजन सहायता", raw_cat_counts.get("Differently Abled Support", 0)),
            ("Banking, Financial Services and Insurance", "Financial Assistance", "💳", "बैंकिंग, वित्तीय सेवाएं एवं बीमा", raw_cat_counts.get("Financial Assistance", 0)),
        ]

        category_items = [
            {
                "name": item[0],
                "db_category": item[1],
                "icon": item[2],
                "name_hi": item[3],
                "count": item[4],
            }
            for item in category_catalog
        ]

        states = [{"state": k, "state_count": v, "count": v} for k, v in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)]
        ministries = [{"ministry": k, "count": v} for k, v in sorted(ministry_counts.items(), key=lambda x: x[1], reverse=True)]

        categories_map = {item["name"]: item["count"] for item in category_items}
        shorthands = {
            "Education & Scholarships": raw_cat_counts.get("Education & Learning", 0),
            "Health": raw_cat_counts.get("Healthcare", 0),
            "Housing": raw_cat_counts.get("Housing & Shelter", 0),
            "Agriculture": raw_cat_counts.get("Agriculture & Rural Development", 0),
            "Business & Loans": raw_cat_counts.get("Business & Self Employment", 0),
            "Employment & Skills": raw_cat_counts.get("Employment & Skills", 0),
            "Pension": raw_cat_counts.get("Social Security & Pension", 0),
            "Insurance": raw_cat_counts.get("Financial Assistance", 0),
            "Women & Child": raw_cat_counts.get("Women & Child Development", 0),
            "Disability Support": raw_cat_counts.get("Differently Abled Support", 0),
        }
        categories_map.update(shorthands)

        return {
            "ok": True,
            "total": total,
            "central": central,
            "state": state,
            "categories": categories_map,
            "category_items": category_items,
            "raw_categories": raw_cat_counts,
            "states": states,
            "ministries": ministries,
            "db_source": f"JSON Fallback ({json_path.name})",
            "error": None,
        }
    except Exception as exc:
        return {
            "ok": False,
            "total": 0,
            "central": 0,
            "state": 0,
            "categories": {},
            "raw_categories": {},
            "category_items": [],
            "states": [],
            "ministries": [],
            "error": str(exc),
            "db_source": f"Error: {exc}",
        }


def _get_fallback_featured_from_json(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve featured schemes from bundled schemes.json when database is unavailable."""
    json_path = _find_schemes_json_path()
    if not json_path:
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)

        slug_to_scheme = {s.get("slug"): s for s in schemes if isinstance(s, dict)}
        default_featured = [
            ("up-post-matric-scholarship-obc", 10),
            ("pmay-gramin", 9),
            ("adip-scheme-disabled", 8),
            ("ayushman-bharat-pmjay", 7),
            ("pm-kisan", 6),
        ]

        results = []
        for slug, priority in default_featured:
            if slug in slug_to_scheme:
                s = dict(slug_to_scheme[slug])
                s["is_featured"] = True
                s["featured_priority"] = priority
                results.append(s)
                if len(results) >= limit:
                    break

        if len(results) < limit:
            for s in schemes:
                if s.get("slug") not in [r.get("slug") for r in results]:
                    sc = dict(s)
                    sc["is_featured"] = True
                    results.append(sc)
                    if len(results) >= limit:
                        break

        return results
    except Exception:
        return []


def get_live_db_statistics() -> Dict[str, Any]:
    """Retrieve verified scheme statistics directly from SQLite or bundled JSON fallback.

    Returns:
        dict with total, central, state, category list, state list, and ministry list.
    """
    db_path = find_db_path()
    if not db_path:
        return _get_fallback_statistics_from_json()

    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()

        # 1. Total schemes
        cursor.execute("SELECT COUNT(*) FROM schemes")
        total = cursor.fetchone()[0]

        # 2. Central schemes
        cursor.execute("SELECT COUNT(*) FROM schemes WHERE level = 'Central'")
        central = cursor.fetchone()[0]

        # 3. State / UT schemes
        cursor.execute("SELECT COUNT(*) FROM schemes WHERE level = 'State'")
        state = cursor.fetchone()[0]

        # 4. Raw categories
        cursor.execute("SELECT category, COUNT(*) FROM schemes GROUP BY category ORDER BY COUNT(*) DESC")
        raw_cat_counts = dict(cursor.fetchall())

        # 5. Structured categories for the Category Explorer
        category_catalog = [
            ("Education & Learning", "Education & Learning", "🎓", "शिक्षा एवं ज्ञान", raw_cat_counts.get("Education & Learning", 0)),
            ("Health & Wellness", "Healthcare", "🏥", "स्वास्थ्य एवं कल्याण", raw_cat_counts.get("Healthcare", 0)),
            ("Agriculture, Rural & Environment", "Agriculture & Rural Development", "🌾", "कृषि, ग्रामीण एवं पर्यावरण", raw_cat_counts.get("Agriculture & Rural Development", 0)),
            ("Business & Entrepreneurship", "Business & Self Employment", "📈", "व्यवसाय एवं उद्यमिता", raw_cat_counts.get("Business & Self Employment", 0)),
            ("Skills & Employment", "Employment & Skills", "💼", "कौशल एवं रोजगार", raw_cat_counts.get("Employment & Skills", 0)),
            ("Housing & Shelter", "Housing & Shelter", "🏠", "आवास एवं आश्रय", raw_cat_counts.get("Housing & Shelter", 0)),
            ("Social Welfare & Empowerment", "Social Security & Pension", "👴", "सामाजिक कल्याण एवं पेंशन", raw_cat_counts.get("Social Security & Pension", 0)),
            ("Women & Child Development", "Women & Child Development", "👩‍👧", "महिला एवं बाल विकास", raw_cat_counts.get("Women & Child Development", 0)),
            ("Differently Abled Support", "Differently Abled Support", "♿", "दिव्यांगजन सहायता", raw_cat_counts.get("Differently Abled Support", 0)),
            ("Banking, Financial Services and Insurance", "Financial Assistance", "💳", "बैंकिंग, वित्तीय सेवाएं एवं बीमा", raw_cat_counts.get("Financial Assistance", 0)),
        ]

        category_items = [
            {
                "name": item[0],
                "db_category": item[1],
                "icon": item[2],
                "name_hi": item[3],
                "count": item[4],
            }
            for item in category_catalog
        ]

        # 6. Top states counts
        cursor.execute("""
            SELECT s.value as state_name, COUNT(DISTINCT schemes.id) as scheme_count
            FROM schemes, json_each(schemes.states) as s
            WHERE s.value != 'ALL' AND s.value != ''
            GROUP BY s.value
            ORDER BY scheme_count DESC
        """)
        state_rows = cursor.fetchall()
        states = [{"state": r[0], "state_count": r[1], "count": r[1]} for r in state_rows]

        # 7. Central Ministries counts
        cursor.execute("""
            SELECT ministry, COUNT(*) as ministry_count
            FROM schemes
            WHERE level = 'Central' AND ministry IS NOT NULL AND ministry != ''
            GROUP BY ministry
            ORDER BY ministry_count DESC
        """)
        ministry_rows = cursor.fetchall()
        ministries = [{"ministry": r[0], "count": r[1]} for r in ministry_rows]

        conn.close()

        # Map to standard category names plus shorthand aliases
        categories_map = {item["name"]: item["count"] for item in category_items}
        shorthands = {
            "Education & Scholarships": raw_cat_counts.get("Education & Learning", 0),
            "Health": raw_cat_counts.get("Healthcare", 0),
            "Housing": raw_cat_counts.get("Housing & Shelter", 0),
            "Agriculture": raw_cat_counts.get("Agriculture & Rural Development", 0),
            "Business & Loans": raw_cat_counts.get("Business & Self Employment", 0),
            "Employment & Skills": raw_cat_counts.get("Employment & Skills", 0),
            "Pension": raw_cat_counts.get("Social Security & Pension", 0),
            "Insurance": raw_cat_counts.get("Financial Assistance", 0),
            "Women & Child": raw_cat_counts.get("Women & Child Development", 0),
            "Disability Support": raw_cat_counts.get("Differently Abled Support", 0),
        }
        categories_map.update(shorthands)

        return {
            "ok": True,
            "total": total,
            "central": central,
            "state": state,
            "categories": categories_map,
            "category_items": category_items,
            "raw_categories": raw_cat_counts,
            "states": states,
            "ministries": ministries,
            "db_source": f"SQLite ({db_path})",
            "error": None,
        }
    except Exception as exc:
        fallback = _get_fallback_statistics_from_json()
        if fallback.get("ok"):
            return fallback
        return {
            "ok": False,
            "total": 0,
            "central": 0,
            "state": 0,
            "categories": {},
            "category_items": [],
            "raw_categories": {},
            "states": [],
            "ministries": [],
            "error": str(exc),
            "db_source": f"Error: {exc}",
        }


def get_featured_schemes_db(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve verified featured schemes directly from SQLite or bundled JSON fallback."""
    db_path = find_db_path()
    if not db_path:
        return _get_fallback_featured_from_json(limit)

    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, slug, name, name_hi, description, description_hi,
                   category, ministry, level, states, benefits, official_url,
                   is_featured, featured_priority, image_url
            FROM schemes
            WHERE is_featured = 1
            ORDER BY featured_priority DESC, name ASC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return _get_fallback_featured_from_json(limit)

        results = []
        for r in rows:
            benefits_val = r[10]
            if isinstance(benefits_val, str):
                try:
                    benefits_val = json.loads(benefits_val)
                except Exception:
                    pass

            states_val = r[9]
            if isinstance(states_val, str):
                try:
                    states_val = json.loads(states_val)
                except Exception:
                    pass

            results.append({
                "id": r[0],
                "slug": r[1],
                "name": r[2],
                "name_hi": r[3],
                "description": r[4],
                "description_hi": r[5],
                "category": r[6],
                "ministry": r[7],
                "level": r[8],
                "states": states_val if isinstance(states_val, list) else [],
                "benefits": benefits_val if isinstance(benefits_val, list) else [],
                "official_url": r[11],
                "is_featured": bool(r[12]),
                "featured_priority": r[13],
                "image_url": r[14],
            })
        return results
    except Exception:
        return _get_fallback_featured_from_json(limit)


def get_user_applications_db(user_id: str) -> List[Dict[str, Any]]:
    """Retrieve all tracked applications for a specific user directly from SQLite."""
    if not user_id:
        return []

    db_path = find_db_path()
    if not db_path:
        return []

    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                t.id, t.user_id, t.scheme_id, t.status, t.notes, t.applied_at, t.created_at, t.updated_at,
                s.slug, s.name, s.name_hi, s.description, s.description_hi, s.category, s.ministry,
                s.level, s.states, s.official_url, s.image_url
            FROM scheme_tracking t
            JOIN schemes s ON t.scheme_id = s.id
            WHERE t.user_id = ?
            ORDER BY t.updated_at DESC, t.created_at DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            states_val = r[16]
            if isinstance(states_val, str):
                try:
                    states_val = json.loads(states_val)
                except Exception:
                    pass

            results.append({
                "id": r[0],
                "user_id": r[1],
                "scheme_id": r[2],
                "status": r[3],
                "notes": r[4] or "",
                "applied_at": r[5],
                "created_at": r[6],
                "updated_at": r[7],
                "added_at": r[6],
                "scheme": {
                    "id": r[2],
                    "slug": r[8],
                    "name": r[9],
                    "name_hi": r[10],
                    "description": r[11],
                    "description_hi": r[12],
                    "category": r[13],
                    "ministry": r[14],
                    "level": r[15],
                    "states": states_val if isinstance(states_val, list) else [],
                    "official_url": r[17],
                    "image_url": r[18],
                },
            })
        return results
    except Exception:
        return []


def is_scheme_in_applications_db(user_id: str, scheme_id: str) -> bool:
    """Check if a scheme is already in the citizen's applications."""
    if not user_id or not scheme_id:
        return False
    db_path = find_db_path()
    if not db_path:
        return False
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM scheme_tracking WHERE user_id = ? AND scheme_id = ? LIMIT 1",
            (user_id, scheme_id),
        )
        found = cursor.fetchone() is not None
        conn.close()
        return found
    except Exception:
        return False


def add_user_application_db(
    user_id: str, scheme_id: str, status: str = "Saved", notes: str = ""
) -> Dict[str, Any]:
    """Add a scheme to the user's applications or return existing."""
    import uuid
    from datetime import datetime, timezone

    if not user_id or not scheme_id:
        return {"ok": False, "error": "Missing user_id or scheme_id"}
    db_path = find_db_path()
    if not db_path:
        return {"ok": False, "error": "Database not found"}
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, status, notes, created_at FROM scheme_tracking WHERE user_id = ? AND scheme_id = ?",
            (user_id, scheme_id),
        )
        existing = cursor.fetchone()
        now_str = datetime.now(timezone.utc).isoformat()
        if existing:
            conn.close()
            return {
                "ok": True,
                "data": {
                    "id": existing[0],
                    "user_id": user_id,
                    "scheme_id": scheme_id,
                    "status": existing[1],
                    "notes": existing[2],
                    "created_at": existing[3],
                },
                "already_existed": True,
            }

        app_id = str(uuid.uuid4())
        applied_at = now_str if status in ("Applied", "Application Submitted") else None
        cursor.execute(
            """
            INSERT INTO scheme_tracking (id, user_id, scheme_id, status, notes, applied_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (app_id, user_id, scheme_id, status, notes, applied_at, now_str, now_str),
        )
        conn.commit()
        conn.close()
        return {
            "ok": True,
            "data": {
                "id": app_id,
                "user_id": user_id,
                "scheme_id": scheme_id,
                "status": status,
                "notes": notes,
                "applied_at": applied_at,
                "created_at": now_str,
                "updated_at": now_str,
            },
            "already_existed": False,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def update_user_application_status_db(
    tracking_id: str, user_id: str, status: str, notes: Optional[str] = None
) -> bool:
    """Update application tracking status with user isolation."""
    from datetime import datetime, timezone

    if not tracking_id or not user_id:
        return False
    db_path = find_db_path()
    if not db_path:
        return False
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()
        if status in ("Applied", "Application Submitted"):
            if notes is not None:
                cursor.execute(
                    """
                    UPDATE scheme_tracking
                    SET status = ?, notes = ?, applied_at = COALESCE(applied_at, ?), updated_at = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (status, notes, now_str, now_str, tracking_id, user_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE scheme_tracking
                    SET status = ?, applied_at = COALESCE(applied_at, ?), updated_at = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (status, now_str, now_str, tracking_id, user_id),
                )
        else:
            if notes is not None:
                cursor.execute(
                    """
                    UPDATE scheme_tracking
                    SET status = ?, notes = ?, updated_at = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (status, notes, now_str, tracking_id, user_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE scheme_tracking
                    SET status = ?, updated_at = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (status, now_str, tracking_id, user_id),
                )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    except Exception:
        return False


def delete_user_application_db(tracking_id: str, user_id: str) -> bool:
    """Delete an application record strictly for the authenticated user."""
    if not tracking_id or not user_id:
        return False
    db_path = find_db_path()
    if not db_path:
        return False
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM scheme_tracking WHERE id = ? AND user_id = ?",
            (tracking_id, user_id),
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception:
        return False
