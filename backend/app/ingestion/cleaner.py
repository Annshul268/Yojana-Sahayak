"""Government scheme data cleaner and normalizer."""

import re
from typing import Any, Dict


class SchemeCleaner:
    """Cleans and standardizes raw scheme attributes."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Strip excessive whitespaces and standardize line breaks
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def clean(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = dict(raw)
        cleaned["slug"] = raw.get("slug", "").strip().lower()
        cleaned["name"] = cls.clean_text(raw.get("name", ""))
        cleaned["name_hi"] = cls.clean_text(raw.get("name_hi", ""))
        cleaned["description"] = cls.clean_text(raw.get("description", ""))
        cleaned["description_hi"] = cls.clean_text(raw.get("description_hi", ""))
        cleaned["category"] = cls.clean_text(raw.get("category", "General"))
        cleaned["ministry"] = cls.clean_text(raw.get("ministry", "Government of India"))
        cleaned["level"] = raw.get("level", "Central").strip().capitalize()
        cleaned["official_url"] = raw.get("official_url", "").strip()
        cleaned["source_url"] = raw.get("source_url", "").strip()
        cleaned["source_name"] = raw.get("source_name", "Government Portal").strip()
        cleaned["states"] = raw.get("states", ["ALL"])
        cleaned["tags"] = [cls.clean_text(t).lower() for t in raw.get("tags", []) if cls.clean_text(t)]
        cleaned["intents"] = [cls.clean_text(i).lower() for i in raw.get("intents", []) if cls.clean_text(i)]
        cleaned["eligibility_rules"] = raw.get("eligibility_rules", {})
        cleaned["benefits"] = [cls.clean_text(b) for b in raw.get("benefits", []) if cls.clean_text(b)]
        cleaned["documents"] = [cls.clean_text(d) for d in raw.get("documents", []) if cls.clean_text(d)]
        cleaned["application_steps"] = [cls.clean_text(s) for s in raw.get("application_steps", []) if cls.clean_text(s)]
        return cleaned
