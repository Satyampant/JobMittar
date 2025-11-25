"""Skills analysis and matching models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SkillCategory(BaseModel):
    """Categorized skill group."""
    category: str = Field(..., min_length=1)
    skills: List[str] = Field(default_factory=list)
    importance: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")


class SkillMatch(BaseModel):
    """Skill matching result between resume and job."""
    skill_name: str
    has_skill: bool
    proficiency_level: Optional[str] = None
    required_level: Optional[str] = None
    match_percentage: float = Field(ge=0.0, le=100.0)


class SkillGap(BaseModel):
    """Skills gap analysis."""
    matched_skills: List[SkillMatch] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    overall_match: float = Field(ge=0.0, le=100.0)
    recommendations: List[str] = Field(default_factory=list)
