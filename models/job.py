"""Job listing data models with validation."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator


class Company(BaseModel):
    """Company information."""
    name: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[HttpUrl] = None


class JobRequirements(BaseModel):
    """Job requirements and qualifications."""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    education_level: Optional[str] = None


class Job(BaseModel):
    """Job listing structure."""
    title: str = Field(..., min_length=1, max_length=200)
    company: Company
    description: str = Field(..., min_length=20)
    requirements: JobRequirements
    salary_range: Optional[str] = None
    employment_type: str = Field(default="Full-time", pattern="^(Full-time|Part-time|Contract|Internship)$")
    posted_date: datetime = Field(default_factory=datetime.now)
    application_url: Optional[HttpUrl] = None
    match_score: Optional[float] = Field(None, ge=0.0, le=100.0)

    @field_validator('match_score')
    @classmethod
    def round_score(cls, v):
        return round(v, 2) if v is not None else v
