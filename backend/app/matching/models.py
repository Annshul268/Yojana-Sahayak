"""Data models for deterministic matching engine."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    POTENTIALLY_ELIGIBLE = "potentially_eligible"
    NOT_ELIGIBLE = "not_eligible"


class CitizenProfileInput(BaseModel):
    state: Optional[str] = Field(None, description="State of residence (e.g. 'Uttar Pradesh')")
    district: Optional[str] = Field(None, description="District of residence")
    age: Optional[int] = Field(None, ge=0, le=120, description="Citizen age in years")
    gender: Optional[str] = Field(None, description="Gender ('female', 'male', 'transgender', 'other')")
    marital_status: Optional[str] = Field(None, description="Marital status ('single', 'married', 'widowed', 'divorced')")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual family income in INR")
    annual_family_income: Optional[float] = Field(None, ge=0, description="Annual family income in INR")
    occupation: Optional[str] = Field(None, description="Primary occupation ('farmer', 'student', 'self-employed', etc.)")
    employment_status: Optional[str] = Field(None, description="Employment status ('employed', 'student', 'unemployed', etc.)")
    category: Optional[str] = Field(None, description="Social category ('General', 'OBC', 'SC', 'ST', 'EWS')")
    area: Optional[str] = Field(None, description="Area of residence ('Rural' or 'Urban')")
    residence_type: Optional[str] = Field(None, description="Residence type ('Rural' or 'Urban')")
    disability: Optional[bool] = Field(False, description="Whether person has a documented disability")
    minority_status: Optional[bool] = Field(False, description="Whether person belongs to a notified minority community")
    requirement: Optional[str] = Field(None, description="Specific need or assistance requested")
    intent: Optional[str] = Field(None, description="Citizen's primary goal or intent")
    needs: Optional[List[str]] = Field(default_factory=list, description="Selected need/category tags")
    education: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured education profile")
    business: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured business profile")
    agriculture: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured agriculture profile")
    disability_details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Detailed disability parameters")
    dynamic_answers: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contextual dynamic question answers")

    @model_validator(mode="after")
    def sync_aliases(self) -> "CitizenProfileInput":
        # Sync income fields
        if self.annual_family_income is not None and self.annual_income is None:
            self.annual_income = self.annual_family_income
        elif self.annual_income is not None and self.annual_family_income is None:
            self.annual_family_income = self.annual_income

        # Sync residence area fields
        if self.residence_type and not self.area:
            self.area = self.residence_type
        elif self.area and not self.residence_type:
            self.residence_type = self.area

        return self


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
    relevance: str = "medium"
    matched_rules: List[RuleResult] = []
    failed_rules: List[RuleResult] = []
    missing_information: List[Dict[str, str]] = []
    matched_attributes: List[str] = []
    failed_conditions: List[str] = []
    important_conditions: List[str] = []
    reason: str = ""
    benefits: List[str] = []
    official_url: str
    tags: List[str] = []
    scheme: Optional[Dict[str, Any]] = None


class MatchResponse(BaseModel):
    total_schemes_evaluated: int
    eligible_count: int
    potentially_eligible_count: int
    not_eligible_count: int
    total_active_schemes: Optional[int] = None
    candidate_count: Optional[int] = None
    results: List[SchemeMatchResult]
