from typing import Any, Dict, List
import copy
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.create_dataset import SCHEMES as EXISTING_SCHEMES
from scripts.catalog_data.central_schemes import CENTRAL_SCHEMES
from scripts.catalog_data.central_schemes_extended import CENTRAL_SCHEMES_EXTENDED
from scripts.catalog_data.central_schemes_more import CENTRAL_SCHEMES_MORE
from scripts.catalog_data.additional_comprehensive_schemes import ADDITIONAL_SCHEMES
from scripts.catalog_data.state_schemes_north import STATE_SCHEMES_NORTH
from scripts.catalog_data.state_schemes_central_west import STATE_SCHEMES_CENTRAL_WEST
from scripts.catalog_data.state_schemes_east import STATE_SCHEMES_EAST
from scripts.catalog_data.state_schemes_south import STATE_SCHEMES_SOUTH
from scripts.catalog_data.state_schemes_extended import STATE_SCHEMES_EXTENDED
from scripts.catalog_data.state_schemes_comprehensive import STATE_SCHEMES_COMPREHENSIVE
from scripts.catalog_data.state_registry import generate_state_catalog


def build_complete_catalog() -> List[Dict[str, Any]]:
    """Merge and deduplicate all scheme catalog data into a unified list."""
    state_registry_schemes = generate_state_catalog()

    source_lists = [
        ("existing", EXISTING_SCHEMES),
        ("central", CENTRAL_SCHEMES),
        ("central_ext", CENTRAL_SCHEMES_EXTENDED),
        ("central_more", CENTRAL_SCHEMES_MORE),
        ("additional", ADDITIONAL_SCHEMES),
        ("state_north", STATE_SCHEMES_NORTH),
        ("state_central_west", STATE_SCHEMES_CENTRAL_WEST),
        ("state_east", STATE_SCHEMES_EAST),
        ("state_south", STATE_SCHEMES_SOUTH),
        ("state_ext", STATE_SCHEMES_EXTENDED),
        ("state_comp", STATE_SCHEMES_COMPREHENSIVE),
        ("state_registry", state_registry_schemes),
    ]

    slug_map: Dict[str, Dict[str, Any]] = {}

    for source_name, schemes in source_lists:
        for item in schemes:
            slug = item.get("slug")
            if not slug:
                continue

            cleaned = copy.deepcopy(item)
            # Ensure mandatory defaults
            if "active" not in cleaned:
                cleaned["active"] = True
            if "verification_status" not in cleaned:
                cleaned["verification_status"] = "Verified"
            if "primary_category" not in cleaned and "category" in cleaned:
                cleaned["primary_category"] = cleaned["category"]
            elif "category" not in cleaned and "primary_category" in cleaned:
                cleaned["category"] = cleaned["primary_category"]

            # Merge or insert
            if slug in slug_map:
                existing = slug_map[slug]
                # Keep richer description or benefits if available
                for k, v in cleaned.items():
                    if v and not existing.get(k):
                        existing[k] = v
            else:
                slug_map[slug] = cleaned

    return list(slug_map.values())


if __name__ == "__main__":
    catalog = build_complete_catalog()
    print(f"Built catalog with {len(catalog)} unique schemes.")
