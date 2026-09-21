"""Validate government schemes data integrity, schema compliance, and URL validity."""

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, List, Tuple


def validate_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def validate_scheme(item: Dict[str, Any], index: int) -> Tuple[bool, List[str]]:
    errors = []
    
    slug = item.get("slug")
    if not slug or not isinstance(slug, str):
        errors.append("Missing or invalid 'slug'")
        
    name = item.get("name")
    if not name or not isinstance(name, str):
        errors.append("Missing or invalid 'name'")
        
    description = item.get("description")
    if not description or not isinstance(description, str):
        errors.append("Missing or invalid 'description'")
        
    category = item.get("category")
    if not category or not isinstance(category, str):
        errors.append("Missing or invalid 'category'")
        
    ministry = item.get("ministry")
    if not ministry or not isinstance(ministry, str):
        errors.append("Missing or invalid 'ministry'")
        
    level = item.get("level", "Central")
    if level not in ("Central", "State"):
        errors.append(f"Invalid 'level': '{level}'. Must be 'Central' or 'State'")
        
    states = item.get("states")
    if not isinstance(states, list) or len(states) == 0:
        errors.append("Missing or invalid 'states'. Must be non-empty list of state names or ['ALL']")
        
    intents = item.get("intents")
    if not isinstance(intents, list) or len(intents) == 0:
        errors.append("Missing or invalid 'intents'. Must be non-empty list")
        
    rules = item.get("eligibility_rules")
    if not isinstance(rules, dict):
        errors.append("Field 'eligibility_rules' must be a dictionary")
        
    official_url = item.get("official_url", "")
    if not validate_url(official_url):
        errors.append(f"Invalid 'official_url': '{official_url}'")
        
    return len(errors) == 0, errors


def validate_file(file_path: Path) -> bool:
    print(f"\n=======================================================")
    print(f"Validating Scheme Catalog: {file_path}")
    print(f"=======================================================")
    
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)
    except Exception as exc:
        print(f"ERROR: Failed to parse JSON in {file_path}: {exc}")
        return False
        
    if not isinstance(schemes, list):
        print(f"ERROR: Root structure must be a list of scheme objects")
        return False
        
    print(f"Total schemes in file: {len(schemes)}")
    
    seen_slugs = set()
    total_valid = 0
    total_errors = 0
    by_category: Dict[str, int] = {}
    by_level: Dict[str, int] = {}
    by_intent: Dict[str, int] = {}
    
    for idx, item in enumerate(schemes):
        slug = item.get("slug", f"<index_{idx}>")
        if slug in seen_slugs:
            print(f"  [ERROR] Duplicate slug detected: '{slug}' at index {idx}")
            total_errors += 1
        seen_slugs.add(slug)
        
        is_valid, errors = validate_scheme(item, idx)
        if not is_valid:
            total_errors += len(errors)
            print(f"  [INVALID] Scheme '{slug}':")
            for err in errors:
                print(f"    - {err}")
        else:
            total_valid += 1
            cat = item.get("category", "Unknown")
            by_category[cat] = by_category.get(cat, 0) + 1
            lvl = item.get("level", "Central")
            by_level[lvl] = by_level.get(lvl, 0) + 1
            for intent in item.get("intents", []):
                by_intent[intent] = by_intent.get(intent, 0) + 1
                
    print(f"\nValidation Summary for {file_path.name}:")
    print(f"- Total Schemes: {len(schemes)}")
    print(f"- Valid: {total_valid}")
    print(f"- Errors: {total_errors}")
    print(f"- By Level: {dict(by_level)}")
    print(f"- By Intent: {dict(by_intent)}")
    
    return total_errors == 0


def main():
    parser = argparse.ArgumentParser(description="Validate government schemes dataset")
    parser.add_argument("--file", type=str, default=None, help="Path to specific JSON file to validate")
    args = parser.parse_args()
    
    files_to_check = [Path(args.file)] if args.file else [
        Path("data/processed/schemes.json"),
        Path("data/seed/schemes.json"),
    ]
    
    all_success = True
    for f in files_to_check:
        success = validate_file(f)
        if not success:
            all_success = False
            
    if all_success:
        print("\nAll scheme datasets passed validation with 0 errors!")
        sys.exit(0)
    else:
        print("\nScheme validation encountered errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
