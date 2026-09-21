"""Pydantic schemas for Citizen Profile."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    annual_income: Optional[float] = Field(None, ge=0)
    occupation: Optional[str] = None
    category: Optional[str] = None
    area: Optional[str] = None
    disability: Optional[bool] = False


class ProfileCreate(ProfileBase):
    user_id: str


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
