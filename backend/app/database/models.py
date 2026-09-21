"""SQLAlchemy ORM Models for Yojana Sahayak."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    annual_income = Column(Float, nullable=True)
    occupation = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)  # General, OBC, SC, ST, EWS
    area = Column(String(50), nullable=True)  # Rural, Urban
    disability = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    name_hi = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    description_hi = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    ministry = Column(String(255), nullable=False, index=True)
    level = Column(String(50), default="Central", index=True)  # Central, State
    states = Column(JSON, default=lambda: ["ALL"])  # List of state names or ["ALL"]
    tags = Column(JSON, default=list)
    intents = Column(JSON, default=list)
    eligibility_rules = Column(JSON, default=dict)
    benefits = Column(JSON, default=list)
    documents = Column(JSON, default=list)
    application_steps = Column(JSON, default=list)
    official_url = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    source_name = Column(String(100), default="National Portal of India")
    last_verified_at = Column(DateTime(timezone=True), default=utcnow)
    verification_status = Column(String(50), default="Verified")
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    saved_by = relationship("SavedScheme", back_populates="scheme", cascade="all, delete-orphan")
    tracking_entries = relationship("SchemeTracking", back_populates="scheme", cascade="all, delete-orphan")


class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(128), index=True, nullable=False)
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    scheme = relationship("Scheme", back_populates="saved_by")


class SchemeTracking(Base):
    __tablename__ = "scheme_tracking"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(128), index=True, nullable=False)
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        String(50),
        default="Saved",
        nullable=False,
    )  # Saved, Planning to Apply, Application Started, Applied, Completed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    scheme = relationship("Scheme", back_populates="tracking_entries")


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_name = Column(String(100), nullable=False)
    schemes_ingested = Column(Integer, default=0)
    status = Column(String(50), default="Success")  # Success, Partial, Failed
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
