"""Pydantic schemas for Saved Schemes and Application Tracking."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.scheme import SchemeResponse


class SavedSchemeCreate(BaseModel):
    user_id: str
    scheme_id: str


class SavedSchemeResponse(BaseModel):
    id: str
    user_id: str
    scheme_id: str
    created_at: Optional[datetime] = None
    scheme: Optional[SchemeResponse] = None

    model_config = ConfigDict(from_attributes=True)


class SchemeTrackingCreate(BaseModel):
    user_id: str
    scheme_id: str
    status: str = "Saved"
    notes: Optional[str] = None


class SchemeTrackingUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class SchemeTrackingResponse(BaseModel):
    id: str
    user_id: str
    scheme_id: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    scheme: Optional[SchemeResponse] = None

    model_config = ConfigDict(from_attributes=True)
