"""Strict validator for government scheme information."""

from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse


class SchemeValidator:
    """Ensures verified integrity and security of incoming scheme data."""

    @staticmethod
    def validate_url(url: str) -> bool:
        if not url:
            return False
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ("http", "https") and parsed.netloc)
        except Exception:
            return False

    @classmethod
    def validate(cls, item: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not item.get("slug"):
            errors.append("Missing required field: 'slug'")
        if not item.get("name"):
            errors.append("Missing required field: 'name'")
        if not item.get("description"):
            errors.append("Missing required field: 'description'")
        if not item.get("category"):
            errors.append("Missing required field: 'category'")
        if not item.get("ministry"):
            errors.append("Missing required field: 'ministry'")

        official_url = item.get("official_url", "")
        if not cls.validate_url(official_url):
            errors.append(f"Invalid or missing official_url: '{official_url}'")

        if not isinstance(item.get("eligibility_rules"), dict):
            errors.append("Field 'eligibility_rules' must be a valid JSON object/dictionary")

        return len(errors) == 0, errors
