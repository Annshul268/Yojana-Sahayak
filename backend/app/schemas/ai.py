"""Pydantic schemas for AI requests and responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from backend.app.matching.models import SchemeMatchResult


class ExplainEligibilityRequest(BaseModel):
    match_result: SchemeMatchResult
    user_profile: Dict[str, Any]
    language: str = "en"


class ExplainEligibilityResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    explanation: str
    language: str


class AskAIRequest(BaseModel):
    question: str
    language: str = "en"
    category: Optional[str] = None


class AskAIResponse(BaseModel):
    question: str
    answer: str
    language: str
    grounded_references: List[Dict[str, Any]]
