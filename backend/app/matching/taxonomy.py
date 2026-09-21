"""Intent Taxonomy and Scheme Tagging Registry for Yojana Sahayak."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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


# 14 Primary Intents Taxonomy (Section 3)
INTENT_REGISTRY: Dict[str, IntentDefinition] = {
    "education": IntentDefinition(
        id="education",
        name="Education & Scholarships",
        name_hi="शिक्षा एवं छात्रवृत्ति",
        description="Pre-matric, post-matric, higher education fellowships, and tuition fee aid.",
        description_hi="छात्रवृत्ति, शिक्षण सहायता, उच्च शिक्षा फेलोशिप और शुल्क प्रतिपूर्ति।",
        icon="🎓",
        candidate_tags=["education", "scholarship", "student", "tuition", "coaching", "school", "college", "fellowship"],
        category_mappings=["Education & Learning"],
        required_attributes=["education_level", "state"],
        optional_attributes=["category", "annual_income", "gender"],
    ),
    "jobs": IntentDefinition(
        id="jobs",
        name="Jobs & Employment",
        name_hi="रोजगार एवं आजीविका",
        description="Public work, wage employment, civil service jobs, and livelihood programs.",
        description_hi="सार्वजनिक रोजगार, मजदूरी रोजगार और आजीविका सहायता।",
        icon="🏢",
        candidate_tags=["employment", "jobs", "livelihood", "wage", "work", "recruitment"],
        category_mappings=["Employment & Skills", "Business & Self Employment"],
        required_attributes=["employment_status", "age", "state"],
        optional_attributes=["annual_income", "category"],
    ),
    "internships": IntentDefinition(
        id="internships",
        name="Internships / Apprenticeships",
        name_hi="इंटर्नशिप एवं शिक्षुता",
        description="PM Internship Scheme, NATS apprenticeship stipends, and industrial training.",
        description_hi="पीएम इंटर्नशिप योजना, शिक्षुता वजीफा और व्यावहारिक औद्योगिक प्रशिक्षण।",
        icon="💼",
        candidate_tags=["internship", "apprenticeship", "nats", "stipend", "learner", "industrial-training"],
        category_mappings=["Education & Learning", "Employment & Skills"],
        required_attributes=["education_level", "age", "state"],
        optional_attributes=["course", "skills"],
    ),
    "skills": IntentDefinition(
        id="skills",
        name="Skill Development / Training",
        name_hi="कौशल विकास एवं प्रशिक्षण",
        description="Free vocational training, PMKVY certification, ITI trades, and technical upskilling.",
        description_hi="नि:शुल्क व्यावसायिक प्रशिक्षण, पीएमकेवीवाई प्रमाणन और तकनीकी कौशल।",
        icon="🛠️",
        candidate_tags=["skill", "training", "vocational", "certification", "iti", "polytechnic", "pmkvy"],
        category_mappings=["Employment & Skills", "Education & Learning"],
        required_attributes=["education_level", "state"],
        optional_attributes=["age", "category"],
    ),
    "business": IntentDefinition(
        id="business",
        name="Business & Entrepreneurship",
        name_hi="व्यवसाय एवं ऋण",
        description="Micro-loans, MSME collateral-free credit, vendor working capital, and startup capital.",
        description_hi="सूक्ष्म ऋण, एमएसएमई ऋण, वेंडर कार्यशील पूंजी और स्टार्टअप पूंजी।",
        icon="📈",
        candidate_tags=["business", "msme", "entrepreneurship", "loan", "vendor", "working-capital", "credit", "startup"],
        category_mappings=["Business & Self Employment"],
        required_attributes=["business_stage", "state"],
        optional_attributes=["annual_income", "category"],
    ),
    "agriculture": IntentDefinition(
        id="agriculture",
        name="Agriculture & Farming",
        name_hi="कृषि एवं किसान कल्याण",
        description="PM-KISAN direct income, crop insurance (PMFBY), farm equipment, and inputs.",
        description_hi="प्रत्यक्ष आय सहायता, फसल बीमा, कृषि उपकरण और उर्वरक सब्सिडी।",
        icon="🌾",
        candidate_tags=["agriculture", "farmer", "income-support", "crop", "irrigation", "kisan", "rural"],
        category_mappings=["Agriculture & Rural Development"],
        required_attributes=["landholding", "state"],
        optional_attributes=["annual_income"],
    ),
    "housing": IntentDefinition(
        id="housing",
        name="Housing & Shelter",
        name_hi="आवास एवं आश्रय",
        description="Financial assistance for pucca house construction under PMAY Rural and Urban.",
        description_hi="पक्के मकान हेतु वित्तीय सहायता और गृह निर्माण अनुदान।",
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
        description="Cashless hospital treatment, Ayushman Bharat health card, and subsidized medicines.",
        description_hi="कैशलेस अस्पताल उपचार, आयुष्मान भारत कार्ड और सस्ती दवाएं।",
        icon="🏥",
        candidate_tags=["health", "medical", "hospital", "ayushman", "insurance", "treatment", "pmjay"],
        category_mappings=["Healthcare"],
        required_attributes=["annual_income", "state"],
        optional_attributes=["category", "area"],
    ),
    "financial": IntentDefinition(
        id="financial",
        name="Financial Assistance",
        name_hi="वित्तीय सहायता",
        description="Direct benefit transfers, emergency grants, social relief, and financial inclusion.",
        description_hi="प्रत्यक्ष लाभ हस्तांतरण (DBT), आपातकालीन सहायता और वित्तीय समावेशन।",
        icon="💳",
        candidate_tags=["financial", "subsidy", "dbt", "grant", "assistance", "inclusion"],
        category_mappings=["Social Security & Pension", "Business & Self Employment"],
        required_attributes=["annual_income", "state"],
        optional_attributes=["category"],
    ),
    "women_child": IntentDefinition(
        id="women_child",
        name="Women & Child Welfare",
        name_hi="महिला एवं बाल विकास",
        description="Maternity benefits, Sukanya Samriddhi girl child savings, and women empowerment.",
        description_hi="मातृत्व लाभ, सुकन्या समृद्धि बालिका बचत और महिला सशक्तिकरण योजनाएं।",
        icon="👩‍👧",
        candidate_tags=["women", "girl-child", "sukanya", "maternity", "mother", "child", "poshan"],
        category_mappings=["Women & Child Development"],
        required_attributes=["gender", "age", "state"],
        optional_attributes=["annual_income"],
    ),
    "pension": IntentDefinition(
        id="pension",
        name="Senior Citizens & Pension",
        name_hi="वरिष्ठ नागरिक एवं पेंशन",
        description="Old age pensions (IGNOAPS), Atal Pension Yojana, and retirement social security.",
        description_hi="वृद्धावस्था पेंशन और सेवानिवृत्ति सामाजिक सुरक्षा।",
        icon="👴",
        candidate_tags=["pension", "senior-citizen", "old-age", "nsap", "atal", "retirement"],
        category_mappings=["Social Security & Pension"],
        required_attributes=["age", "annual_income", "state"],
        optional_attributes=["category"],
    ),
    "disability": IntentDefinition(
        id="disability",
        name="Disability Support (Divyangjan)",
        name_hi="दिव्यांगजन सहायता",
        description="Concessional self-employment loans, assistive devices, and disability pensions.",
        description_hi="रियायती स्वरोजगार ऋण, सहायक उपकरण और दिव्यांग पेंशन।",
        icon="♿",
        candidate_tags=["disability", "differently-abled", "divyangjan", "nhfdc", "handicap", "assistive", "pwd"],
        category_mappings=["Differently Abled Support"],
        required_attributes=["disability", "state"],
        optional_attributes=["age", "annual_income"],
    ),
    "social_welfare": IntentDefinition(
        id="social_welfare",
        name="Social Welfare",
        name_hi="समाज कल्याण",
        description="Support for marginalized groups, SC/ST development, EWS aid, and backward classes.",
        description_hi="हाशिए पर स्थित वर्गों, अनुसूचित जातियों व जनजातियों हेतु कल्याणकारी योजनाएं।",
        icon="🤝",
        candidate_tags=["welfare", "marginalized", "sc-st", "tribal", "backward", "minority", "ews"],
        category_mappings=["Social Security & Pension", "Education & Learning", "Differently Abled Support"],
        required_attributes=["category", "annual_income", "state"],
        optional_attributes=["age"],
    ),
    "general": IntentDefinition(
        id="general",
        name="Explore All Government Benefits",
        name_hi="सभी योजनाओं का अन्वेषण करें",
        description="Broad eligibility check across all government schemes with basic demographic details.",
        description_hi="बुनियादी विवरण के साथ सभी सरकारी योजनाओं की पात्रता जांचें।",
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
    if not intent_id:
        return None
    normalized_id = intent_id.strip().lower()
    # Handle aliases
    aliases = {
        "education_scholarship": "education",
        "scholarship": "education",
        "internship": "internships",
        "skill": "skills",
        "entrepreneurship": "business",
        "farmer": "agriculture",
        "senior": "pension",
        "senior_citizens": "pension",
        "divyang": "disability",
        "health": "healthcare",
    }
    target_id = aliases.get(normalized_id, normalized_id)
    return INTENT_REGISTRY.get(target_id)


def match_intent_candidate_schemes(intent_id: str, schemes: List[Any]) -> List[Any]:
    """Strictly pre-filters candidate schemes relevant to the selected intent/sector.
    
    Prevents unrelated schemes (e.g. healthcare, housing, savings) from leaking into
    education/scholarship searches and vice versa.
    """
    intent = get_intent_by_id(intent_id)
    if not intent or intent.id == "general":
        return schemes

    matched = []
    for s in schemes:
        # 1. Scheme explicit intents check
        scheme_intents = getattr(s, "intents", None) or []
        if isinstance(scheme_intents, str):
            scheme_intents = [scheme_intents]
        if intent.id in [str(i).lower() for i in scheme_intents]:
            matched.append(s)
            continue

        # 2. Scheme tags and category check
        scheme_tags = getattr(s, "tags", []) or []
        scheme_category = getattr(s, "category", "") or ""
        scheme_name = (getattr(s, "name", "") or "").lower()

        # Check tag intersection
        has_tag_match = any(t in intent.candidate_tags for t in scheme_tags)
        has_cat_match = scheme_category in intent.category_mappings
        has_name_match = any(t in scheme_name for t in intent.candidate_tags if len(t) > 3)

        if has_tag_match or has_cat_match or has_name_match:
            matched.append(s)

    # Return matched candidates strictly in that sector
    return matched


def is_geographically_applicable(scheme: Any, user_state: Optional[str]) -> bool:
    """Checks if a scheme is geographically applicable to the citizen.
    
    A scheme is applicable if:
    1. Scheme level is Central or scheme states contains 'ALL', OR
    2. User state is empty/None (explore all), OR
    3. User state matches one of the scheme's designated states (case-insensitive).
    """
    if not user_state:
        return True
    
    scheme_states = getattr(scheme, "states", None)
    if scheme_states is None and isinstance(scheme, dict):
        scheme_states = scheme.get("states")
    if not scheme_states:
        scheme_states = ["ALL"]
    elif isinstance(scheme_states, str):
        scheme_states = [scheme_states]
        
    normalized_states = [str(st).strip().upper() for st in scheme_states]
    if "ALL" in normalized_states:
        return True
    
    user_state_clean = user_state.strip().upper()
    return user_state_clean in normalized_states

