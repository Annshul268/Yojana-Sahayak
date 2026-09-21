"""Deterministic rule evaluators for government schemes."""

from typing import Any, Dict, List, Optional, Tuple
from backend.app.matching.models import CitizenProfileInput, RuleResult


class RuleEvaluator:
    """Evaluates individual criteria against citizen demographic profiles."""

    @staticmethod
    def evaluate_state(
        rule_states: List[str],
        user_state: Optional[str],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        if not rule_states or "ALL" in [s.upper() for s in rule_states]:
            return True, RuleResult(
                rule_name="state",
                passed=True,
                reason="Scheme is applicable across all states in India.",
                required_value="ALL",
                user_value=user_state or "Unspecified",
            ), None

        if not user_state:
            return None, None, {
                "field": "state",
                "reason": f"Scheme requires verification in: {', '.join(rule_states)}",
            }

        user_clean = user_state.strip().lower()
        matched = any(s.strip().lower() == user_clean for s in rule_states)
        return matched, RuleResult(
            rule_name="state",
            passed=matched,
            reason=f"State {'matches' if matched else 'does not match'} scheme criteria." ,
            required_value=rule_states,
            user_value=user_state,
        ), None

    @staticmethod
    def evaluate_age(
        age_rule: Dict[str, Any],
        user_age: Optional[int],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        min_age = age_rule.get("min")
        max_age = age_rule.get("max")

        if user_age is None:
            return None, None, {
                "field": "age",
                "reason": f"Age requirement: {f'Min {min_age}' if min_age else ''} {f'Max {max_age}' if max_age else ''}".strip(),
            }

        passed = True
        reason_parts = []
        if min_age is not None and user_age < min_age:
            passed = False
            reason_parts.append(f"Age {user_age} is below minimum {min_age}")
        if max_age is not None and user_age > max_age:
            passed = False
            reason_parts.append(f"Age {user_age} exceeds maximum {max_age}")

        reason = "; ".join(reason_parts) if not passed else f"Age {user_age} satisfies criteria."
        return passed, RuleResult(
            rule_name="age",
            passed=passed,
            reason=reason,
            required_value=age_rule,
            user_value=user_age,
        ), None

    @staticmethod
    def evaluate_income(
        income_rule: Dict[str, Any],
        user_income: Optional[float],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        max_income = income_rule.get("max")
        if max_income is None:
            return True, None, None

        if user_income is None:
            return None, None, {
                "field": "annual_income",
                "reason": f"Annual family income ceiling: ₹{max_income:,.0f}",
            }

        passed = user_income <= max_income
        reason = (
            f"Income ₹{user_income:,.0f} is within ceiling of ₹{max_income:,.0f}"
            if passed
            else f"Income ₹{user_income:,.0f} exceeds maximum ceiling of ₹{max_income:,.0f}"
        )
        return passed, RuleResult(
            rule_name="annual_income",
            passed=passed,
            reason=reason,
            required_value=income_rule,
            user_value=user_income,
        ), None

    @staticmethod
    def evaluate_gender(
        allowed_genders: Any,
        user_gender: Optional[str],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        if isinstance(allowed_genders, str):
            allowed_genders = [allowed_genders]
        allowed_lower = [g.lower() for g in (allowed_genders or [])]
        if not allowed_lower or "all" in allowed_lower:
            return True, None, None

        if not user_gender:
            return None, None, {
                "field": "gender",
                "reason": f"Scheme specifies gender criteria: {', '.join(allowed_genders)}",
            }

        passed = user_gender.lower().strip() in allowed_lower
        return passed, RuleResult(
            rule_name="gender",
            passed=passed,
            reason=f"Gender '{user_gender}' {'qualifies' if passed else 'does not match scheme criteria'}.",
            required_value=allowed_genders,
            user_value=user_gender,
        ), None

    @staticmethod
    def evaluate_occupation(
        allowed_occupations: Any,
        user_occupation: Optional[str],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        if isinstance(allowed_occupations, str):
            allowed_occupations = [allowed_occupations]
        allowed_list = allowed_occupations or []
        if not allowed_list or "all" in [o.lower() for o in allowed_list]:
            return True, None, None

        if not user_occupation:
            return None, None, {
                "field": "occupation",
                "reason": f"Target occupations: {', '.join(allowed_list)}",
            }

        user_clean = user_occupation.lower().strip()
        passed = any(
            req.lower().strip() in user_clean or user_clean in req.lower().strip()
            for req in allowed_list
        )
        return passed, RuleResult(
            rule_name="occupation",
            passed=passed,
            reason=f"Occupation '{user_occupation}' {'matches' if passed else 'does not match'} target group.",
            required_value=allowed_list,
            user_value=user_occupation,
        ), None

    @staticmethod
    def evaluate_category(
        allowed_categories: Any,
        user_category: Optional[str],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        if isinstance(allowed_categories, str):
            allowed_categories = [allowed_categories]
        allowed_list = allowed_categories or []
        if not allowed_list or "all" in [c.lower() for c in allowed_list]:
            return True, None, None

        if not user_category:
            return None, None, {
                "field": "category",
                "reason": f"Target social categories: {', '.join(allowed_list)}",
            }

        user_clean = user_category.upper().strip()
        passed = any(c.upper().strip() == user_clean for c in allowed_list)
        return passed, RuleResult(
            rule_name="category",
            passed=passed,
            reason=f"Category '{user_category}' {'qualifies' if passed else 'is not among eligible categories'}.",
            required_value=allowed_list,
            user_value=user_category,
        ), None

    @staticmethod
    def evaluate_area(
        allowed_areas: Any,
        user_area: Optional[str],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        if isinstance(allowed_areas, str):
            allowed_areas = [allowed_areas]
        allowed_list = allowed_areas or []
        if not allowed_list or "all" in [a.lower() for a in allowed_list]:
            return True, None, None

        if not user_area:
            return None, None, {
                "field": "area",
                "reason": f"Target area: {', '.join(allowed_list)}",
            }

        user_clean = user_area.lower().strip()
        passed = any(a.lower().strip() == user_clean for a in allowed_list)
        return passed, RuleResult(
            rule_name="area",
            passed=passed,
            reason=f"Area '{user_area}' {'matches' if passed else 'does not match'} scheme coverage.",
            required_value=allowed_list,
            user_value=user_area,
        ), None

    @staticmethod
    def evaluate_disability(
        required_disability: bool,
        user_disability: Optional[bool],
    ) -> Tuple[Optional[bool], Optional[RuleResult], Optional[Dict[str, str]]]:
        if not required_disability:
            return True, None, None

        if user_disability is None:
            return None, None, {
                "field": "disability",
                "reason": "Scheme is specifically designed for Persons with Disabilities (Divyangjan).",
            }

        passed = bool(user_disability) is True
        return passed, RuleResult(
            rule_name="disability",
            passed=passed,
            reason="Beneficiary disability criteria verified." if passed else "Scheme requires PwD certificate / disability.",
            required_value=required_disability,
            user_value=user_disability,
        ), None
