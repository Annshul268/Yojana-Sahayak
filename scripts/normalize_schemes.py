"""Normalization script for Yojana Sahayak Scheme Datasets.

Standardizes taxonomy categories, state names, level classifications,
numeric eligibility constraints, and ensures data cleanliness.
"""

import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


STATE_CANONICAL_MAP = {
    "UP": "Uttar Pradesh",
    "UTTAR PRADESH": "Uttar Pradesh",
    "MH": "Maharashtra",
    "MAHARASHTRA": "Maharashtra",
    "RJ": "Rajasthan",
    "RAJASTHAN": "Rajasthan",
    "MP": "Madhya Pradesh",
    "MADHYA PRADESH": "Madhya Pradesh",
    "BR": "Bihar",
    "BIHAR": "Bihar",
    "WB": "West Bengal",
    "WEST BENGAL": "West Bengal",
    "GJ": "Gujarat",
    "GUJARAT": "Gujarat",
    "KA": "Karnataka",
    "KARNATAKA": "Karnataka",
    "TN": "Tamil Nadu",
    "TAMIL NADU": "Tamil Nadu",
    "TS": "Telangana",
    "TELANGANA": "Telangana",
    "AP": "Andhra Pradesh",
    "ANDHRA PRADESH": "Andhra Pradesh",
    "OD": "Odisha",
    "ORISSA": "Odisha",
    "ODISHA": "Odisha",
    "PB": "Punjab",
    "PUNJAB": "Punjab",
    "HR": "Haryana",
    "HARYANA": "Haryana",
    "KL": "Kerala",
    "KERALA": "Kerala",
    "JH": "Jharkhand",
    "JHARKHAND": "Jharkhand",
    "CG": "Chhattisgarh",
    "CHHATTISGARH": "Chhattisgarh",
    "AS": "Assam",
    "ASSAM": "Assam",
    "UK": "Uttarakhand",
    "UA": "Uttarakhand",
    "UTTARAKHAND": "Uttarakhand",
    "HP": "Himachal Pradesh",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "DL": "Delhi",
    "DELHI": "Delhi",
    "NCT OF DELHI": "Delhi",
    "ALL": "ALL",
    "CENTRAL": "ALL",
    "INDIA": "ALL",
    "NATIONAL": "ALL",
}

CATEGORY_CANONICAL_MAP = {
    "Education & Scholarships": "Education & Learning",
    "Education & Learning": "Education & Learning",
    "Jobs & Employment": "Employment & Skills",
    "Employment & Skills": "Employment & Skills",
    "Internships": "Employment & Skills",
    "Skill Development": "Employment & Skills",
    "Business & Entrepreneurship": "Business & Self Employment",
    "Business & Self Employment": "Business & Self Employment",
    "Agriculture & Farming": "Agriculture & Rural Development",
    "Agriculture & Rural Development": "Agriculture & Rural Development",
    "Housing": "Housing & Shelter",
    "Housing & Shelter": "Housing & Shelter",
    "Healthcare": "Healthcare",
    "Health & Wellness": "Healthcare",
    "Financial Assistance": "Financial Assistance",
    "Women & Child Welfare": "Women & Child Development",
    "Women & Child Development": "Women & Child Development",
    "Senior Citizens & Pension": "Social Security & Pension",
    "Social Security & Pension": "Social Security & Pension",
    "Disability Support": "Differently Abled Support",
    "Differently Abled Support": "Differently Abled Support",
    "Social Welfare": "Social Welfare",
}


def normalize_state_name(state: str) -> str:
    """Normalize state name to its canonical title."""
    if not state:
        return "ALL"
    cleaned = state.strip().upper()
    return STATE_CANONICAL_MAP.get(cleaned, state.strip().title())


def normalize_states_list(states: Any) -> List[str]:
    """Ensure states is a clean, canonical list of state names."""
    if not states:
        return ["ALL"]
    if isinstance(states, str):
        states = [states]
    normalized = []
    for s in states:
        norm = normalize_state_name(str(s))
        if norm not in normalized:
            normalized.append(norm)
    if "ALL" in normalized:
        return ["ALL"]
    return normalized


def normalize_eligibility_rules(rules: Any, scheme_states: List[str]) -> Dict[str, Any]:
    """Normalize eligibility rules dictionary with proper types."""
    if not isinstance(rules, dict):
        rules = {}
    cleaned = copy.deepcopy(rules)

    # Ensure states in rules aligns with scheme states
    if "states" not in cleaned or not cleaned["states"]:
        cleaned["states"] = scheme_states

    # Age normalization
    if "age" in cleaned and cleaned["age"] is not None:
        age_val = cleaned["age"]
        if isinstance(age_val, (int, float)):
            cleaned["age"] = {"min": int(age_val)}
        elif isinstance(age_val, dict):
            sub = {}
            if "min" in age_val and age_val["min"] is not None:
                sub["min"] = int(age_val["min"])
            if "max" in age_val and age_val["max"] is not None:
                sub["max"] = int(age_val["max"])
            cleaned["age"] = sub

    # Income normalization
    if "income" in cleaned and cleaned["income"] is not None:
        inc_val = cleaned["income"]
        if isinstance(inc_val, (int, float)):
            cleaned["income"] = {"max": int(inc_val)}
        elif isinstance(inc_val, dict):
            sub = {}
            if "min" in inc_val and inc_val["min"] is not None:
                sub["min"] = int(inc_val["min"])
            if "max" in inc_val and inc_val["max"] is not None:
                sub["max"] = int(inc_val["max"])
            cleaned["income"] = sub

    # Lists normalization
    for list_key in ("category", "occupation", "gender", "area"):
        if list_key in cleaned and cleaned[list_key] is not None:
            val = cleaned[list_key]
            if isinstance(val, str):
                cleaned[list_key] = [val.strip()]
            elif isinstance(val, list):
                cleaned[list_key] = [str(x).strip() for x in val if x]

    # Disability normalization
    if "disability" in cleaned:
        d = cleaned["disability"]
        if isinstance(d, str):
            cleaned["disability"] = d.lower() in ("true", "yes", "1", "required")
        elif isinstance(d, bool):
            cleaned["disability"] = d

    return cleaned


def normalize_scheme(scheme: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a single scheme item."""
    s = copy.deepcopy(scheme)

    # Slug
    slug = str(s.get("slug", "")).strip().lower().replace(" ", "-")
    s["slug"] = slug

    # States
    s["states"] = normalize_states_list(s.get("states"))

    # Level
    if "ALL" in s["states"]:
        s["level"] = "Central"
    else:
        s["level"] = "State"

    # Category
    cat = s.get("category") or s.get("primary_category") or "Social Security & Pension"
    canonical_cat = CATEGORY_CANONICAL_MAP.get(cat, cat)
    s["category"] = canonical_cat
    s["primary_category"] = canonical_cat

    # Intents
    intents = s.get("intents", [])
    if isinstance(intents, str):
        intents = [intents]
    s["intents"] = [str(i).strip().lower() for i in intents if i]

    # Tags
    tags = s.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    s["tags"] = [str(t).strip().lower() for t in tags if t]

    # Rules
    s["eligibility_rules"] = normalize_eligibility_rules(s.get("eligibility_rules"), s["states"])

    # Active & status
    s["active"] = True
    s["verification_status"] = "Verified"

    return s


def normalize_dataset(schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize and deduplicate an entire catalog list."""
    dedup: Dict[str, Dict[str, Any]] = {}
    for item in schemes:
        norm = normalize_scheme(item)
        slug = norm["slug"]
        if slug in dedup:
            # Merge fields
            existing = dedup[slug]
            for k, v in norm.items():
                if v and not existing.get(k):
                    existing[k] = v
        else:
            dedup[slug] = norm

    return list(dedup.values())


if __name__ == "__main__":
    from scripts.catalog_data.builder import build_complete_catalog

    raw_catalog = build_complete_catalog()
    normalized = normalize_dataset(raw_catalog)
    print(f"Normalized {len(normalized)} unique schemes successfully.")
