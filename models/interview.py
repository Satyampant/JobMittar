"""Interview preparation data models."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class InterviewQuestion(BaseModel):
    """Individual interview question."""
    question: str = Field(..., min_length=10, description="The interview question text")
    category: str = Field(
        default="General", 
        pattern="^(Technical|Behavioral|Situational|General)$",
        description="Question category"
    )
    difficulty: str = Field(
        default="Medium", 
        pattern="^(Easy|Medium|Hard)$",
        description="Question difficulty level"
    )
    suggested_answer: Optional[str] = Field(
        None, 
        description="Suggested approach or answer to the question"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Key points to cover in the answer"
    )
    
    # Add this for backward compatibility with UI
    @property
    def tips(self) -> str:
        """Generate tips from key_points for UI compatibility."""
        if self.key_points:
            return "\n".join(f"• {point}" for point in self.key_points)
        return "Focus on providing specific examples and demonstrating your problem-solving approach."


class InterviewResponse(BaseModel):
    """User's response to interview question."""
    question_id: str
    response: str = Field(..., min_length=10)
    feedback: Optional[str] = None
    score: Optional[float] = Field(None, ge=0.0, le=10.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class Interview(BaseModel):
    """Complete interview preparation session."""
    job_title: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=1)
    questions: List[InterviewQuestion] = Field(default_factory=list)
    responses: List[InterviewResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if len(v) < 1:
            raise ValueError('At least one question is required')
        return v