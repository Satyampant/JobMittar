
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator


class InterviewQuestion(BaseModel):
    question: str = Field(..., min_length=10)
    category: str = Field(default="General", pattern="^(Technical|Behavioral|Situational|General)$")
    difficulty: str = Field(default="Medium", pattern="^(Easy|Medium|Hard)$")
    suggested_answer: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)
    
    # app.py expects 'tips' field
    @property
    def tips(self) -> str:
        """Convert key_points to tips string for UI."""
        if self.key_points:
            return "\n".join(f"• {point}" for point in self.key_points)
        return ""


class InterviewResponse(BaseModel):
    question_id: str
    response: str = Field(..., min_length=10)
    feedback: Optional[str] = None
    score: Optional[float] = Field(None, ge=0.0, le=10.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class Interview(BaseModel):
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
    


class InterviewQuestionResponse(BaseModel):
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
        """Formatting time taken as HH:MM:SS."""
        if self.time_taken_seconds:
            return str(timedelta(seconds=int(self.time_taken_seconds)))
        return "Not recorded"


class InterviewFeedback(BaseModel):
    evaluation: str = Field(..., min_length=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=10.0)
    accuracy_score: float = Field(..., ge=0.0, le=10.0)
    
    def to_formatted_string(self) -> str:
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


class InterviewSessionState(BaseModel):
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
        if not self.questions:
            return 0.0
        return (len(self.responses) / len(self.questions)) * 100
    
    @property
    def average_confidence(self) -> Optional[float]:
        scores = [r.confidence_score for r in self.responses if r.confidence_score]
        return sum(scores) / len(scores) if scores else None
    
    @property
    def average_accuracy(self) -> Optional[float]:
        scores = [r.accuracy_score for r in self.responses if r.accuracy_score]
        return sum(scores) / len(scores) if scores else None