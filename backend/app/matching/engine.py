"""Deterministic Matching Engine for government schemes."""

from typing import Any, Dict, List, Optional
from backend.app.database.models import Scheme
from backend.app.matching.models import (
    CitizenProfileInput,
    EligibilityStatus,
    MatchResponse,
    RuleResult,
    SchemeMatchResult,
)
from backend.app.matching.rules import RuleEvaluator
from backend.app.matching.scoring import MatchScorer
from backend.app.matching.taxonomy import (
    is_geographically_applicable,
    match_intent_candidate_schemes,
)


class MatchingEngine:
    """Evaluates citizen eligibility against structured government scheme rules."""

    def __init__(self):
        self.evaluator = RuleEvaluator()
        self.scorer = MatchScorer()

    def evaluate_scheme(
        self,
        scheme: Scheme,
        profile: CitizenProfileInput,
    ) -> SchemeMatchResult:
        rules = scheme.eligibility_rules or {}
        matched_rules: List[RuleResult] = []
        failed_rules: List[RuleResult] = []
        missing_info: List[dict] = []

        # 1. State evaluation
        scheme_states = scheme.states or ["ALL"]
        state_passed, state_rule, state_missing = self.evaluator.evaluate_state(
            scheme_states, profile.state
        )
        if state_missing:
            missing_info.append(state_missing)
        elif state_rule:
            (matched_rules if state_passed else failed_rules).append(state_rule)

        # 2. Age evaluation
        if "age" in rules:
            age_passed, age_rule, age_missing = self.evaluator.evaluate_age(
                rules["age"], profile.age
            )
            if age_missing:
                missing_info.append(age_missing)
            elif age_rule:
                (matched_rules if age_passed else failed_rules).append(age_rule)

        # 3. Income evaluation (Manual numeric check against ceiling)
        effective_income = profile.annual_family_income if profile.annual_family_income is not None else profile.annual_income
        if "income" in rules:
            inc_passed, inc_rule, inc_missing = self.evaluator.evaluate_income(
                rules["income"], effective_income
            )
            if inc_missing:
                missing_info.append(inc_missing)
            elif inc_rule:
                (matched_rules if inc_passed else failed_rules).append(inc_rule)

        # 4. Gender evaluation
        if "gender" in rules:
            gen_passed, gen_rule, gen_missing = self.evaluator.evaluate_gender(
                rules["gender"], profile.gender
            )
            if gen_missing:
                missing_info.append(gen_missing)
            elif gen_rule:
                (matched_rules if gen_passed else failed_rules).append(gen_rule)

        # 5. Occupation evaluation
        effective_occupation = profile.occupation
        if not effective_occupation:
            if profile.intent == "education" or profile.education:
                effective_occupation = "student"
            elif profile.intent == "agriculture" or profile.agriculture:
                effective_occupation = "farmer"
            elif profile.intent == "business" or profile.business:
                effective_occupation = "entrepreneur"
            elif profile.intent in ("internships", "skills"):
                effective_occupation = "student"

        if "occupation" in rules:
            occ_passed, occ_rule, occ_missing = self.evaluator.evaluate_occupation(
                rules["occupation"], effective_occupation
            )
            if occ_missing:
                missing_info.append(occ_missing)
            elif occ_rule:
                (matched_rules if occ_passed else failed_rules).append(occ_rule)

        # 6. Social Category evaluation
        if "category" in rules:
            cat_passed, cat_rule, cat_missing = self.evaluator.evaluate_category(
                rules["category"], profile.category
            )
            if cat_missing:
                missing_info.append(cat_missing)
            elif cat_rule:
                (matched_rules if cat_passed else failed_rules).append(cat_rule)

        # 7. Area evaluation (Rural / Urban)
        effective_area = profile.residence_type or profile.area
        if "area" in rules:
            area_passed, area_rule, area_missing = self.evaluator.evaluate_area(
                rules["area"], effective_area
            )
            if area_missing:
                missing_info.append(area_missing)
            elif area_rule:
                (matched_rules if area_passed else failed_rules).append(area_rule)

        # 8. Disability evaluation
        if "disability" in rules and rules["disability"] is True:
            dis_passed, dis_rule, dis_missing = self.evaluator.evaluate_disability(
                rules["disability"], profile.disability
            )
            if dis_missing:
                missing_info.append(dis_missing)
            elif dis_rule:
                (matched_rules if dis_passed else failed_rules).append(dis_rule)

        # Determine Final Status
        if len(failed_rules) > 0:
            status = EligibilityStatus.NOT_ELIGIBLE
        elif len(missing_info) > 0:
            status = EligibilityStatus.POTENTIALLY_ELIGIBLE
        else:
            status = EligibilityStatus.ELIGIBLE

        # Keyword relevancy check for user requirement or intent
        keyword_boost = False
        text_queries = []
        if profile.requirement:
            text_queries.extend(profile.requirement.lower().split())
        if profile.intent:
            text_queries.extend(profile.intent.lower().split())

        combined_text = f"{scheme.name} {scheme.category} {scheme.description or ''}".lower()
        if any(w in combined_text for w in text_queries if len(w) > 3):
            keyword_boost = True

        # Need / Category Intent Matching
        needs_boost = False
        if profile.needs:
            need_keywords = {
                "Education & scholarships": ["education", "scholarship", "learning", "student"],
                "Health": ["health", "medical", "hospital", "ayushman"],
                "Housing": ["housing", "awas", "shelter", "home"],
                "Agriculture": ["agriculture", "agri", "farmer", "kisan", "crop", "rural"],
                "Business & loans": ["business", "loan", "mudra", "svanidhi", "micro", "enterprise"],
                "Employment & skills": ["employment", "skill", "job", "training", "work", "internship"],
                "Pension": ["pension", "atal", "nsap", "senior", "retirement"],
                "Insurance": ["insurance", "bima", "security", "cover"],
                "Women & child": ["women", "child", "girl", "sukanya", "mahila", "mother"],
                "Disability support": ["disability", "differently abled", "divyangjan", "handicapped", "nhfdc"],
            }
            scheme_cat_lower = (scheme.category or "").lower()
            for need in profile.needs:
                if need.lower() in scheme_cat_lower:
                    needs_boost = True
                    break
                keywords = need_keywords.get(need, [need.lower()])
                if any(kw in scheme_cat_lower or kw in combined_text for kw in keywords):
                    needs_boost = True
                    break

        score = self.scorer.calculate_score(
            status=status,
            matched_rules=matched_rules,
            failed_rules=failed_rules,
            missing_count=len(missing_info),
            keyword_boost=keyword_boost,
            needs_boost=needs_boost,
        )

        # Extract important conditions for citizen awareness
        important_conditions = []
        if "income" in rules:
            inc_rule_def = rules["income"]
            if isinstance(inc_rule_def, dict) and "max" in inc_rule_def:
                important_conditions.append(f"Family income must be below ₹{inc_rule_def['max']:,}")
        if "age" in rules:
            age_def = rules["age"]
            if isinstance(age_def, dict):
                if "min" in age_def and "max" in age_def:
                    important_conditions.append(f"Age must be between {age_def['min']} and {age_def['max']} years")
                elif "min" in age_def:
                    important_conditions.append(f"Minimum age is {age_def['min']} years")
        if "occupation" in rules:
            important_conditions.append(f"Restricted to: {', '.join(rules['occupation']).title()}")
        if "category" in rules and isinstance(rules["category"], list):
            important_conditions.append(f"Eligible categories: {', '.join(rules['category'])}")
        if scheme.states and "ALL" not in scheme.states:
            important_conditions.append(f"Valid only in: {', '.join(scheme.states)}")

        # Build matched & failed attribute descriptions
        matched_attributes = [r.reason for r in matched_rules]
        failed_conditions = [r.reason for r in failed_rules]

        # Calculate human-friendly match reason
        if status == EligibilityStatus.ELIGIBLE:
            reason = "You satisfy all core eligibility rules for this scheme."
            relevance = "high" if (needs_boost or keyword_boost or score >= 90) else "medium"
        elif status == EligibilityStatus.POTENTIALLY_ELIGIBLE:
            reason = f"Your details match, but {len(missing_info)} item(s) need verification."
            relevance = "high" if needs_boost else "medium"
        else:
            reason = f"Ineligible due to: {failed_rules[0].reason if failed_rules else 'criteria requirements'}."
            relevance = "low"

        scheme_summary = {
            "id": scheme.id,
            "slug": scheme.slug,
            "name": scheme.name,
            "name_hi": scheme.name_hi,
            "category": scheme.category,
            "ministry": scheme.ministry,
            "level": scheme.level,
            "benefits": scheme.benefits or [],
            "documents": scheme.documents or [],
            "application_steps": scheme.application_steps or [],
            "official_url": scheme.official_url,
            "tags": getattr(scheme, "tags", []) or [],
        }

        return SchemeMatchResult(
            scheme_id=scheme.id,
            slug=scheme.slug,
            scheme_name=scheme.name,
            scheme_name_hi=scheme.name_hi,
            category=scheme.category,
            ministry=scheme.ministry,
            status=status,
            score=score,
            relevance=relevance,
            matched_rules=matched_rules,
            failed_rules=failed_rules,
            missing_information=missing_info,
            matched_attributes=matched_attributes,
            failed_conditions=failed_conditions,
            important_conditions=important_conditions,
            reason=reason,
            benefits=scheme.benefits or [],
            official_url=scheme.official_url,
            tags=getattr(scheme, "tags", []) or [],
            scheme=scheme_summary,
        )

    def match_all(
        self,
        schemes: List[Scheme],
        profile: CitizenProfileInput,
    ) -> MatchResponse:
        # Step 1: Normalize citizen answers into canonical structure
        raw_income = profile.annual_family_income if profile.annual_family_income is not None else profile.annual_income
        res_area = (profile.residence_type or profile.area or "").strip().capitalize() or None

        normalized_profile = CitizenProfileInput(
            state=profile.state.strip() if profile.state else None,
            district=profile.district.strip() if profile.district else None,
            age=profile.age,
            gender=profile.gender.strip().lower() if profile.gender else None,
            marital_status=profile.marital_status.strip().lower() if profile.marital_status else None,
            annual_income=raw_income,
            annual_family_income=raw_income,
            occupation=profile.occupation.strip().lower() if profile.occupation else None,
            employment_status=profile.employment_status.strip().lower() if profile.employment_status else None,
            category=profile.category.strip() if profile.category else None,
            area=res_area,
            residence_type=res_area,
            disability=profile.disability,
            minority_status=profile.minority_status,
            requirement=profile.requirement.strip() if profile.requirement else None,
            intent=profile.intent.strip().lower() if profile.intent else None,
            needs=list(profile.needs or []),
            education=dict(profile.education or {}),
            business=dict(profile.business or {}),
            agriculture=dict(profile.agriculture or {}),
            disability_details=dict(profile.disability_details or {}),
            dynamic_answers=dict(profile.dynamic_answers or {}),
        )

        # Step 2: Intent determination
        intent_id = normalized_profile.intent
        if not intent_id and normalized_profile.needs:
            need_first = normalized_profile.needs[0].lower()
            if "education" in need_first or "scholarship" in need_first:
                intent_id = "education"
            elif "intern" in need_first or "apprentice" in need_first:
                intent_id = "internships"
            elif "skill" in need_first or "training" in need_first:
                intent_id = "skills"
            elif "business" in need_first or "loan" in need_first:
                intent_id = "business"
            elif "agri" in need_first or "farm" in need_first:
                intent_id = "agriculture"
            elif "job" in need_first or "employ" in need_first:
                intent_id = "jobs"
            elif "pension" in need_first or "senior" in need_first:
                intent_id = "pension"
            elif "health" in need_first:
                intent_id = "healthcare"
            elif "housing" in need_first:
                intent_id = "housing"
            elif "women" in need_first or "child" in need_first:
                intent_id = "women_child"
            elif "disab" in need_first or "divyang" in need_first:
                intent_id = "disability"

        # Step 3: Geographic & Sector Candidate Retrieval
        # Evaluates Central schemes applicable across India PLUS citizen's State schemes
        active_schemes = [s for s in schemes if getattr(s, "active", True)]

        # 3a. Filter geographically applicable schemes for citizen's state
        if normalized_profile.state:
            geo_schemes = [
                s for s in active_schemes
                if is_geographically_applicable(s, normalized_profile.state)
            ]
        else:
            geo_schemes = active_schemes

        # 3b. Filter candidate schemes by citizen intent / sector
        if intent_id and intent_id != "general":
            candidate_schemes = match_intent_candidate_schemes(intent_id, geo_schemes)
            # If no schemes matched the narrow intent, fall back to all geo schemes
            if not candidate_schemes:
                candidate_schemes = geo_schemes
        else:
            candidate_schemes = geo_schemes

        # Step 4: Evaluate deterministic hard eligibility on candidate schemes
        results: List[SchemeMatchResult] = []
        for scheme in candidate_schemes:
            result = self.evaluate_scheme(scheme, normalized_profile)
            results.append(result)

        # Step 5: Sort results: Eligible first, then Potentially Eligible, then Not Eligible; then descending by score
        status_priority = {
            EligibilityStatus.ELIGIBLE: 0,
            EligibilityStatus.POTENTIALLY_ELIGIBLE: 1,
            EligibilityStatus.NOT_ELIGIBLE: 2,
        }
        results.sort(key=lambda r: (status_priority[r.status], -r.score))

        eligible_count = sum(1 for r in results if r.status == EligibilityStatus.ELIGIBLE)
        pot_count = sum(1 for r in results if r.status == EligibilityStatus.POTENTIALLY_ELIGIBLE)
        not_count = sum(1 for r in results if r.status == EligibilityStatus.NOT_ELIGIBLE)

        return MatchResponse(
            total_schemes_evaluated=len(results),
            eligible_count=eligible_count,
            potentially_eligible_count=pot_count,
            not_eligible_count=not_count,
            total_active_schemes=len(active_schemes),
            candidate_count=len(candidate_schemes),
            results=results,
        )


matching_engine = MatchingEngine()
