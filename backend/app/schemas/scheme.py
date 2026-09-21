"""Pydantic schemas for Scheme resources."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SchemeBase(BaseModel):
    slug: str
    name: str
    name_hi: Optional[str] = None
    description: str
    description_hi: Optional[str] = None
    category: str
    ministry: str
    level: str = "Central"
    states: List[str] = ["ALL"]
    eligibility_rules: Dict[str, Any] = Field(default_factory=dict)
    benefits: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    application_steps: List[str] = Field(default_factory=list)
    official_url: str
    source_url: Optional[str] = None
    source_name: str = "Government Portal"
    verification_status: str = "Verified"
    active: bool = True


class SchemeCreate(SchemeBase):
    pass


class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    name_hi: Optional[str] = None
    description: Optional[str] = None
    description_hi: Optional[str] = None
    category: Optional[str] = None
    ministry: Optional[str] = None
    level: Optional[str] = None
    states: Optional[List[str]] = None
    eligibility_rules: Optional[Dict[str, Any]] = None
    benefits: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    application_steps: Optional[List[str]] = None
    official_url: Optional[str] = None
    active: Optional[bool] = None
    verification_status: Optional[str] = None


class SchemeResponse(SchemeBase):
    id: str
    last_verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SchemeListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[SchemeResponse]
