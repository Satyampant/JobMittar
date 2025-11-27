"""Core state schema for JobMittar LangGraph workflow.

This state replaces session_state as the single source of truth,
flowing through all nodes in the graph.
"""

from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, field_validator


class JobMittrState(TypedDict, total=False):
    """Comprehensive state model for JobMittar workflow.
    Each field is optional to allow partial initialization and gradual population.
    """
    
    # Resume Management
    resume_data: Optional[Dict[str, Any]]
    """Parsed resume: {name, email, phone, summary, skills, education, experience}"""
    
    # Job Search
    job_query: Optional[Dict[str, Any]]
    """Search parameters: {keywords, location, platform, count}"""
    
    job_results: List[Dict[str, Any]]
    """Retrieved job listings from SERP API"""
    
    selected_job: Optional[Dict[str, Any]]
    """Currently selected job for analysis/interview prep"""
    
    # Analysis
    match_analysis: Optional[Dict[str, Any]]
    """Resume-job compatibility: {match_score, key_matches, gaps, recommendations}"""
    
    # Interview Preparation
    interview_questions: List[Dict[str, Any]]
    """Generated interview questions with metadata"""
    
    interview_session: Optional[Dict[str, Any]]
    """Active interview state: {current_question_index, responses, is_active}"""
    
    # Workflow Control
    current_step: str
    """Current workflow stage: 'resume_upload', 'job_search', 'analysis', 'interview'"""
    
    error: Optional[str]
    """Error message if workflow encounters issues"""
    
    # Conversation Context
    messages: List[BaseMessage]
    """LangChain message history for conversational context"""
    
    # Metadata
    user_preferences: Optional[Dict[str, Any]]
    """User settings: {interview_type, question_count, notification_prefs}"""


class JobMittrStateValidator(BaseModel):
    """Pydantic validator for state integrity checks.
    Use this to validate state before critical operations.
    """
    
    resume_data: Optional[Dict[str, Any]] = None
    job_query: Optional[Dict[str, Any]] = None
    job_results: List[Dict[str, Any]] = Field(default_factory=list)
    selected_job: Optional[Dict[str, Any]] = None
    match_analysis: Optional[Dict[str, Any]] = None
    interview_questions: List[Dict[str, Any]] = Field(default_factory=list)
    interview_session: Optional[Dict[str, Any]] = None
    current_step: str = Field(default="resume_upload")
    error: Optional[str] = None
    messages: List[Any] = Field(default_factory=list)  # BaseMessage not serializable
    user_preferences: Optional[Dict[str, Any]] = None
    
    @field_validator('current_step')
    @classmethod
    def validate_step(cls, v: str) -> str:
        """Ensure current_step is a valid workflow stage."""
        valid_steps = {
            'resume_upload', 'resume_analysis', 
            'job_search', 'job_selection',
            'match_analysis', 'interview_prep', 
            'interview_active', 'interview_complete'
        }
        if v not in valid_steps:
            raise ValueError(f"Invalid step: {v}. Must be one of {valid_steps}")
        return v
    
    @field_validator('job_query')
    @classmethod
    def validate_query(cls, v: Optional[Dict]) -> Optional[Dict]:
        """Ensure job_query has required fields."""
        if v is not None:
            required = {'keywords', 'location'}
            if not required.issubset(v.keys()):
                raise ValueError(f"job_query missing required fields: {required - v.keys()}")
        return v
    
    model_config = {"extra": "allow"}


def create_initial_state(current_step: str = "resume_upload",resume_data: Optional[Dict] = None) -> JobMittrState:
    """Factory function to create initial state with defaults.
    Args:
        current_step: Starting workflow stage
        resume_data: Optional pre-loaded resume data
    Returns:
        Initialized JobMittrState ready for graph execution
    """
    return JobMittrState(
        resume_data=resume_data,
        job_query=None,
        job_results=[],
        selected_job=None,
        match_analysis=None,
        interview_questions=[],
        interview_session=None,
        current_step=current_step,
        error=None,
        messages=[],
        user_preferences={}
    )


def validate_state(state: JobMittrState) -> tuple[bool, Optional[str]]:
    """Validate state integrity using Pydantic.
    Args:
        state: State to validate
    Returns:
        (is_valid, error_message) tuple
    """
    try:
        JobMittrStateValidator(**state)
        return True, None
    except Exception as e:
        return False, str(e)