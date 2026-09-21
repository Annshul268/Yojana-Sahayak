"""Deterministic Matching Engine for government schemes."""

from typing import List
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

        # 3. Income evaluation
        if "income" in rules:
            inc_passed, inc_rule, inc_missing = self.evaluator.evaluate_income(
                rules["income"], profile.annual_income
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
        if "occupation" in rules:
            occ_passed, occ_rule, occ_missing = self.evaluator.evaluate_occupation(
                rules["occupation"], profile.occupation
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

        # 7. Area evaluation
        if "area" in rules:
            area_passed, area_rule, area_missing = self.evaluator.evaluate_area(
                rules["area"], profile.area
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

        # Keyword relevancy check for user requirement
        keyword_boost = False
        if profile.requirement:
            req_words = profile.requirement.lower().split()
            combined_text = f"{scheme.name} {scheme.category} {scheme.description}".lower()
            if any(w in combined_text for w in req_words if len(w) > 3):
                keyword_boost = True

        score = self.scorer.calculate_score(
            status=status,
            matched_rules=matched_rules,
            failed_rules=failed_rules,
            missing_count=len(missing_info),
            keyword_boost=keyword_boost,
        )

        return SchemeMatchResult(
            scheme_id=scheme.id,
            slug=scheme.slug,
            scheme_name=scheme.name,
            scheme_name_hi=scheme.name_hi,
            category=scheme.category,
            ministry=scheme.ministry,
            status=status,
            score=score,
            matched_rules=matched_rules,
            failed_rules=failed_rules,
            missing_information=missing_info,
            benefits=scheme.benefits or [],
            official_url=scheme.official_url,
        )

    def match_all(
        self,
        schemes: List[Scheme],
        profile: CitizenProfileInput,
    ) -> MatchResponse:
        results: List[SchemeMatchResult] = []
        for scheme in schemes:
            if scheme.active:
                result = self.evaluate_scheme(scheme, profile)
                results.append(result)

        # Sort results: Eligible first, then Potentially Eligible, then Not Eligible; then descending by score
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
            results=results,
        )


matching_engine = MatchingEngine()
