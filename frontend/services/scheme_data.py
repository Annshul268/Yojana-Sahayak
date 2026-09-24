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
        Path("/Users/anshulmac/Documents/Projects/Yojana-Sahayak/yojana_sahayak.db"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def get_live_db_statistics() -> Dict[str, Any]:
    """Retrieve verified scheme statistics directly from the SQLite database.

    Returns:
        dict with total, central, state, category list, state list, and ministry list.
    """
    db_path = find_db_path()
    if not db_path:
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
            "error": "Database file yojana_sahayak.db not found",
            "db_source": "None",
        }

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
    """Retrieve verified featured schemes directly from the SQLite database."""
    db_path = find_db_path()
    if not db_path:
        return []

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
        return []
