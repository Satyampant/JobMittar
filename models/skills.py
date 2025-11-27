"""Skills analysis and matching models."""

from typing import List, Optional
from pydantic import BaseModel, Field

class JobMatchAnalysis(BaseModel):
    """Simple job-resume match analysis result."""
    match_score: float = Field(..., ge=0.0, le=100.0, description="Overall match percentage")
    key_matches: List[str] = Field(default_factory=list, description="Matching qualifications")
    gaps: List[str] = Field(default_factory=list, description="Missing requirements")
    recommendations: List[str] = Field(default_factory=list, description="Improvement suggestions")