"""Resume data models with validation."""

from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator, EmailStr


class Skill(BaseModel):
    """Individual skill with proficiency level."""
    name: str = Field(..., min_length=1, max_length=100)
    proficiency: Optional[str] = Field(None, pattern="^(Beginner|Intermediate|Advanced|Expert)$")
    years_experience: Optional[int] = Field(None, ge=0, le=50)


class Education(BaseModel):
    """Educational qualification details."""
    degree: str = Field(..., min_length=1)
    institution: str = Field(..., min_length=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=10.0)

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class WorkExperience(BaseModel):
    """Work experience entry."""
    company: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    start_date: date
    end_date: Optional[date] = None
    description: str = Field(..., min_length=10)
    achievements: List[str] = Field(default_factory=list)


class Resume(BaseModel):
    """Complete resume structure."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    summary: str = Field(..., min_length=20, max_length=1000)
    skills: List[Skill] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        if len(v) < 1:
            raise ValueError('At least one skill is required')
        return v

class ResumeAnalysis(BaseModel):
    """Resume quality analysis result."""
    overall_assessment: str = Field(..., min_length=20)
    strengths: List[str] = Field(default_factory=list, min_items=3)
    weaknesses: List[str] = Field(default_factory=list, min_items=3)
    content_improvements: List[str] = Field(default_factory=list)
    format_suggestions: List[str] = Field(default_factory=list)
    ats_optimization: List[str] = Field(default_factory=list)