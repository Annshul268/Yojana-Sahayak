"""Intent Taxonomy and Scheme Tagging Registry for Yojana Sahayak."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IntentDefinition:
    id: str
    name: str
    name_hi: str
    description: str
    description_hi: str
    icon: str
    candidate_tags: List[str]
    category_mappings: List[str]
    required_attributes: List[str] = field(default_factory=list)
    optional_attributes: List[str] = field(default_factory=list)


# Top-level Intent Taxonomy (Section 56 & 57)
INTENT_REGISTRY: Dict[str, IntentDefinition] = {
    "education": IntentDefinition(
        id="education",
        name="Education & Scholarships",
        name_hi="शिक्षा एवं छात्रवृत्ति",
        description="Scholarships, tuition aid, coaching, and student welfare programs.",
        description_hi="छात्रवृत्ति, शिक्षण सहायता, कोचिंग और छात्र कल्याणकारी योजनाएं।",
        icon="🎓",
        candidate_tags=["education", "scholarship", "student", "tuition", "coaching", "school", "college"],
        category_mappings=["Education & Learning"],
        required_attributes=["education_level", "state"],
        optional_attributes=["category", "annual_income", "gender"],
    ),
    "business": IntentDefinition(
        id="business",
        name="Business & Entrepreneurship",
        name_hi="व्यवसाय एवं ऋण",
        description="Micro-loans, MSME collateral-free credit, vendor working capital, and startup grants.",
        description_hi="सूक्ष्म ऋण, एमएसएमई ऋण, वेंडर कार्यशील पूंजी और स्टार्टअप अनुदान।",
        icon="💼",
        candidate_tags=["business", "msme", "entrepreneurship", "loan", "vendor", "working-capital", "credit"],
        category_mappings=["Business & Self Employment"],
        required_attributes=["business_stage", "state"],
        optional_attributes=["annual_income", "category"],
    ),
    "agriculture": IntentDefinition(
        id="agriculture",
        name="Agriculture & Farming",
        name_hi="कृषि एवं किसान कल्याण",
        description="Direct income transfers, crop insurance, farm equipment, and fertilizer subsidies.",
        description_hi="प्रत्यक्ष आय सहायता, फसल बीमा, कृषि उपकरण और उर्वरक सब्सिडी।",
        icon="🌾",
        candidate_tags=["agriculture", "farmer", "income-support", "crop", "irrigation", "kisan", "rural"],
        category_mappings=["Agriculture & Rural Development"],
        required_attributes=["landholding", "state"],
        optional_attributes=["annual_income"],
    ),
    "jobs": IntentDefinition(
        id="jobs",
        name="Jobs & Employment",
        name_hi="रोजगार एवं आजीविका",
        description="Public employment, apprenticeship stipends, wage employment, and livelihood support.",
        description_hi="सार्वजनिक रोजगार, शिक्षुता वजीफा और आजीविका सहायता।",
        icon="🏢",
        candidate_tags=["employment", "jobs", "apprenticeship", "livelihood", "wage", "work"],
        category_mappings=["Business & Self Employment", "Social Security & Pension"],
        required_attributes=["employment_status", "age", "state"],
        optional_attributes=["annual_income", "category"],
    ),
    "skills": IntentDefinition(
        id="skills",
        name="Skill Development & Training",
        name_hi="कौशल विकास एवं प्रशिक्षण",
        description="Free vocational training, industrial skills certification, and technical courses.",
        description_hi="नि:शुल्क व्यावसायिक प्रशिक्षण और औद्योगिक कौशल प्रमाणन।",
        icon="🛠️",
        candidate_tags=["skill", "training", "vocational", "certification", "iti", "polytechnic"],
        category_mappings=["Education & Learning"],
        required_attributes=["education_level", "state"],
        optional_attributes=["age", "category"],
    ),
    "housing": IntentDefinition(
        id="housing",
        name="Housing & Shelter",
        name_hi="आवास एवं आश्रय",
        description="Financial assistance for pucca houses, rural home construction, and home loan subsidy.",
        description_hi="पक्के मकान हेतु वित्तीय सहायता और गृह ऋण सब्सिडी।",
        icon="🏠",
        candidate_tags=["housing", "awas", "shelter", "pucca-house", "construction", "home-loan"],
        category_mappings=["Housing & Shelter"],
        required_attributes=["area", "annual_income", "state"],
        optional_attributes=["category"],
    ),
    "healthcare": IntentDefinition(
        id="healthcare",
        name="Healthcare & Medical",
        name_hi="स्वास्थ्य एवं चिकित्सा",
        description="Cashless hospital treatment, insurance cover, maternal care, and subsidized medicines.",
        description_hi="कैशलेस अस्पताल उपचार, स्वास्थ्य बीमा और सस्ती दवाएं।",
        icon="🏥",
        candidate_tags=["health", "medical", "hospital", "ayushman", "insurance", "treatment"],
        category_mappings=["Healthcare"],
        required_attributes=["annual_income", "state"],
        optional_attributes=["category", "area"],
    ),
    "pension": IntentDefinition(
        id="pension",
        name="Senior Citizens & Pension",
        name_hi="वरिष्ठ नागरिक एवं पेंशन",
        description="Old age pension, contributory retirement security, and healthcare for elderly.",
        description_hi="वृद्धावस्था पेंशन और सेवानिवृत्ति सामाजिक सुरक्षा।",
        icon="👴",
        candidate_tags=["pension", "senior-citizen", "old-age", "nsap", "atal", "retirement"],
        category_mappings=["Social Security & Pension"],
        required_attributes=["age", "annual_income", "state"],
        optional_attributes=["category"],
    ),
    "women_child": IntentDefinition(
        id="women_child",
        name="Women & Child Welfare",
        name_hi="महिला एवं बाल विकास",
        description="Maternity benefits, girl child savings, nutritional support, and female entrepreneurship.",
        description_hi="मातृत्व लाभ, सुकन्या बचत और महिला सशक्तिकरण योजनाएं।",
        icon="👩‍👧",
        candidate_tags=["women", "girl-child", "sukanya", "maternity", "mother", "child"],
        category_mappings=["Women & Child Development"],
        required_attributes=["gender", "age", "state"],
        optional_attributes=["annual_income"],
    ),
    "disability": IntentDefinition(
        id="disability",
        name="Disability Support (Divyangjan)",
        name_hi="दिव्यांगजन सहायता",
        description="Concessional self-employment loans, assistive devices, and disability pensions.",
        description_hi="रियायती स्वरोजगार ऋण, सहायक उपकरण और दिव्यांग पेंशन।",
        icon="♿",
        candidate_tags=["disability", "differently-abled", "divyangjan", "nhfdc", "handicap", "assistive"],
        category_mappings=["Differently Abled Support"],
        required_attributes=["disability", "state"],
        optional_attributes=["age", "annual_income"],
    ),
    "general": IntentDefinition(
        id="general",
        name="Explore All Benefits",
        name_hi="सभी योजनाओं का अन्वेषण करें",
        description="Broad eligibility check across all government schemes with basic demographic details.",
        description_hi="बुनियादी विवरण के साथ सभी योजनाओं की पात्रता जांचें।",
        icon="🌐",
        candidate_tags=[],
        category_mappings=[],
        required_attributes=["state", "age", "annual_income"],
        optional_attributes=["occupation", "category", "area"],
    ),
}


def get_all_intents() -> List[IntentDefinition]:
    """Returns list of all available intents."""
    return list(INTENT_REGISTRY.values())


def get_intent_by_id(intent_id: str) -> Optional[IntentDefinition]:
    """Retrieve intent definition by ID."""
    return INTENT_REGISTRY.get(intent_id)


def match_intent_candidate_schemes(intent_id: str, schemes: list) -> list:
    """Pre-filters candidate schemes relevant to the selected intent using tags and category."""
    intent = get_intent_by_id(intent_id)
    if not intent or intent.id == "general":
        return schemes

    matched = []
    for s in schemes:
        # Check scheme tags
        scheme_tags = getattr(s, "tags", []) or []
        scheme_category = getattr(s, "category", "")
        scheme_name = getattr(s, "name", "").lower()

        # Check tag intersection
        has_tag_match = any(t in intent.candidate_tags for t in scheme_tags)
        has_cat_match = scheme_category in intent.category_mappings
        has_name_match = any(t in scheme_name for t in intent.candidate_tags)

        if has_tag_match or has_cat_match or has_name_match:
            matched.append(s)

    # Fallback to all schemes if none matched
    return matched if matched else schemes
