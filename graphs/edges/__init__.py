"""Routing logic for LangGraph conditional edges.
"""

from typing import Literal
from graphs.state import JobMittrState


def route_after_resume(state: JobMittrState) -> Literal["job_search", "error"]:
    if state.get("error"):
        return "error"
    if state.get("resume_data"):
        return "job_search"
    return "error"


def route_after_search(state: JobMittrState) -> Literal["select_job", "no_results_end", "error"]:
    if state.get("error"):
        return "error"
    
    job_results = state.get("job_results", [])
    
    # No results found
    if not job_results or len(job_results) == 0:
        return "no_results_end"
    
    # Results available - proceed to selection
    return "select_job"


def route_after_job_search(state: JobMittrState) -> Literal["job_selection", "error", "retry_search"]:
    if state.get("error"):
        return "error"
    
    job_results = state.get("job_results", [])
    if not job_results:
        return "retry_search"
    
    return "job_selection"


def route_after_selection(state: JobMittrState) -> Literal["match_analysis", "interview_prep", "error"]:
    if state.get("error"):
        return "error"
    
    selected_job = state.get("selected_job")
    if not selected_job:
        return "error"
    
    # Checking if user wants analysis or interview prep
    user_prefs = state.get("user_preferences", {})
    next_action = user_prefs.get("next_action", "analysis")
    
    if next_action == "interview":
        return "interview_prep"
    return "match_analysis"


def route_after_match_analysis(state: JobMittrState) -> Literal["interview_prep", "end", "error"]:
    if state.get("error"):
        return "error"
    
    match_analysis = state.get("match_analysis")
    if not match_analysis:
        return "error"
    
    # Checking if user wants to proceed to interview prep
    user_prefs = state.get("user_preferences", {})
    proceed_to_interview = user_prefs.get("proceed_to_interview", False)
    
    if proceed_to_interview:
        return "interview_prep"
    
    # End workflow after analysis
    return "end"


def route_after_interview_prep(state: JobMittrState) -> Literal["interview_active", "error"]:
    if state.get("error"):
        return "error"
    
    questions = state.get("interview_questions", [])
    if not questions:
        return "error"
    
    return "interview_active"


def route_interview_progress(state: JobMittrState) -> Literal["conduct_question", "advance_question", "finalize_interview", "error"]:
    
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return "error"
    
    from models.interview import InterviewSessionState
    
    try:
        session = InterviewSessionState(**session_dict)
    except Exception:
        return "error"
    
    # Check if all questions answered
    if session.current_question_index >= len(session.questions):
        return "finalize_interview"
    
    # Check if response exists for current question
    if len(session.responses) > session.current_question_index:
        # Response exists, advance to next question
        return "advance_question"
    
    # Continue with current question (awaiting response)
    return "conduct_question"


def route_after_conduct(state: JobMittrState) -> Literal["await_input", "check_progress", "error"]:
    current_step = state.get("current_step", "")
    
    # If awaiting response, pause workflow (human-in-the-loop)
    if current_step == "awaiting_response":
        return "await_input"
    
    # If error occurred
    if state.get("error"):
        return "error"
    
    # If response processed, check progress to determine next step
    return "check_progress"

__all__ = [
    "route_after_resume",
    "route_after_search",
    "route_after_job_search",
    "route_after_selection",
    "route_after_match_analysis",
    "route_after_interview_prep",
    "route_interview_progress", 
    "route_after_conduct"
]