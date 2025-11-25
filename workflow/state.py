from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class JobSearchState(TypedDict):
    """Centralized state for job search workflow"""
    # Resume data
    resume_text: Optional[str]
    resume_parsed: Optional[Dict[str, Any]]
    skills: List[str]
    experience: List[str]
    
    # Job search parameters
    search_keywords: Optional[str]
    location: Optional[str]
    platforms: List[str]
    
    # Job results
    jobs: List[Dict[str, Any]]
    selected_job: Optional[Dict[str, Any]]
    match_analysis: Optional[Dict[str, Any]]
    
    # Interview preparation
    interview_questions: Optional[List[Dict[str, Any]]]
    interview_type: Optional[str]
    
    # Workflow metadata
    status: WorkflowStatus
    current_step: str
    error: Optional[str]
    timestamp: datetime
    checkpoint_id: Optional[str]
