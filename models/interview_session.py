"""Enhanced interview session models with real-time interaction support."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator


class InterviewQuestionResponse(BaseModel):
    """Real-time response to an interview question."""
    question_id: int
    question_text: str
    audio_response_path: Optional[str] = None
    transcribed_text: str = Field(default="", min_length=0)
    time_taken_seconds: Optional[float] = Field(None, ge=0)
    feedback: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def time_taken_formatted(self) -> str:
        """Format time taken as HH:MM:SS."""
        if self.time_taken_seconds:
            return str(timedelta(seconds=int(self.time_taken_seconds)))
        return "Not recorded"


class InterviewSessionState(BaseModel):
    """State management for live interview session."""
    job_title: str
    company_name: str
    interview_type: str = Field(default="Technical Interview")
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    responses: List[InterviewQuestionResponse] = Field(default_factory=list)
    current_question_index: int = Field(default=0, ge=0)
    session_start_time: Optional[datetime] = None
    session_end_time: Optional[datetime] = None
    is_active: bool = Field(default=False)
    
    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if len(v) < 1:
            raise ValueError('At least one question is required')
        return v
    
    @property
    def progress_percentage(self) -> float:
        """Calculate interview progress percentage."""
        if not self.questions:
            return 0.0
        return (len(self.responses) / len(self.questions)) * 100
    
    @property
    def average_confidence(self) -> Optional[float]:
        """Calculate average confidence score."""
        scores = [r.confidence_score for r in self.responses if r.confidence_score]
        return sum(scores) / len(scores) if scores else None
    
    @property
    def average_accuracy(self) -> Optional[float]:
        """Calculate average accuracy score."""
        scores = [r.accuracy_score for r in self.responses if r.accuracy_score]
        return sum(scores) / len(scores) if scores else None


class InterviewFeedback(BaseModel):
    """Structured feedback for interview response."""
    evaluation: str = Field(..., min_length=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=10.0)
    accuracy_score: float = Field(..., ge=0.0, le=10.0)
    
    def to_formatted_string(self) -> str:
        """Convert feedback to formatted string for display."""
        output = f"**Evaluation:**\n{self.evaluation}\n\n"
        
        if self.strengths:
            output += "**Strengths:**\n"
            output += "\n".join(f"- {s}" for s in self.strengths) + "\n\n"
        
        if self.weaknesses:
            output += "**Weaknesses:**\n"
            output += "\n".join(f"- {w}" for w in self.weaknesses) + "\n\n"
        
        if self.suggestions:
            output += "**Suggestions for Improvement:**\n"
            output += "\n".join(f"- {s}" for s in self.suggestions) + "\n\n"
        
        output += f"**Confidence Score:** {self.confidence_score}/10\n"
        output += f"**Accuracy Score:** {self.accuracy_score}/10"
        
        return output