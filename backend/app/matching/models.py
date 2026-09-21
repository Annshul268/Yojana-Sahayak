"""Data models for deterministic matching engine."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    POTENTIALLY_ELIGIBLE = "potentially_eligible"
    NOT_ELIGIBLE = "not_eligible"


class CitizenProfileInput(BaseModel):
    state: Optional[str] = Field(None, description="State of residence (e.g. 'Uttar Pradesh')")
    age: Optional[int] = Field(None, ge=0, le=120, description="Citizen age in years")
    gender: Optional[str] = Field(None, description="Gender (e.g. 'female', 'male', 'transgender')")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual family income in INR")
    occupation: Optional[str] = Field(None, description="Primary occupation (e.g. 'farmer', 'student')")
    category: Optional[str] = Field(None, description="Social category (e.g. 'General', 'OBC', 'SC', 'ST', 'EWS')")
    area: Optional[str] = Field(None, description="Area of residence ('Rural' or 'Urban')")
    disability: Optional[bool] = Field(False, description="Whether person has a documented disability")
    requirement: Optional[str] = Field(None, description="Specific need or assistance requested")


class RuleResult(BaseModel):
    rule_name: str
    passed: bool
    reason: str
    required_value: Any
    user_value: Any


class SchemeMatchResult(BaseModel):
    scheme_id: str
    slug: str
    scheme_name: str
    scheme_name_hi: Optional[str] = None
    category: str
    ministry: str
    status: EligibilityStatus
    score: int
    matched_rules: List[RuleResult] = []
    failed_rules: List[RuleResult] = []
    missing_information: List[Dict[str, str]] = []
    benefits: List[str] = []
    official_url: str


class MatchResponse(BaseModel):
    total_schemes_evaluated: int
    eligible_count: int
    potentially_eligible_count: int
    not_eligible_count: int
    results: List[SchemeMatchResult]
