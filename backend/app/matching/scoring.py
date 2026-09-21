"""Eligibility scoring algorithm."""

from typing import List
from backend.app.matching.models import EligibilityStatus, RuleResult


class MatchScorer:
    """Calculates a normalized 0-100 score reflecting scheme fit and eligibility certainty."""

    @staticmethod
    def calculate_score(
        status: EligibilityStatus,
        matched_rules: List[RuleResult],
        failed_rules: List[RuleResult],
        missing_count: int,
        keyword_boost: bool = False,
    ) -> int:
        if status == EligibilityStatus.NOT_ELIGIBLE:
            # Low score for schemes where citizen is disqualified
            score = max(5, 30 - len(failed_rules) * 10)
            return int(score)

        if status == EligibilityStatus.POTENTIALLY_ELIGIBLE:
            # Baseline 70, adjusted by matched rules and missing details
            score = 65 + min(20, len(matched_rules) * 5) - min(15, missing_count * 5)
            if keyword_boost:
                score += 5
            return int(min(89, max(50, score)))

        # Status is ELIGIBLE
        score = 90 + min(10, len(matched_rules) * 2)
        if keyword_boost:
            score = 100
        return int(min(100, max(90, score)))
