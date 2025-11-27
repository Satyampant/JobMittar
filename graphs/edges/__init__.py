"""Routing logic for LangGraph conditional edges.

Edge functions determine the next node based on current state.
They enable dynamic workflow branching without manual if/else chains.
"""

from typing import Literal
from graphs.state import JobMittrState


def route_after_resume(
    state: JobMittrState
) -> Literal["job_search", "error"]:
    """Determine next step after resume processing.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    if state.get("error"):
        return "error"
    if state.get("resume_data"):
        return "job_search"
    return "error"


def route_after_search(
    state: JobMittrState
) -> Literal["select_job", "no_results_end", "error"]:
    """Determine next step after job search.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    if state.get("error"):
        return "error"
    
    job_results = state.get("job_results", [])
    
    # No results found
    if not job_results or len(job_results) == 0:
        return "no_results_end"
    
    # Results available - proceed to selection
    return "select_job"


def route_after_job_search(
    state: JobMittrState
) -> Literal["job_selection", "error", "retry_search"]:
    """Legacy routing - kept for backward compatibility.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    if state.get("error"):
        return "error"
    
    job_results = state.get("job_results", [])
    if not job_results:
        return "retry_search"
    
    return "job_selection"


def route_after_selection(
    state: JobMittrState
) -> Literal["match_analysis", "interview_prep", "error"]:
    """Determine next step after job selection.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    if state.get("error"):
        return "error"
    
    selected_job = state.get("selected_job")
    if not selected_job:
        return "error"
    
    # Check if user wants analysis or interview prep
    user_prefs = state.get("user_preferences", {})
    next_action = user_prefs.get("next_action", "analysis")
    
    if next_action == "interview":
        return "interview_prep"
    return "match_analysis"


def route_after_match_analysis(
    state: JobMittrState
) -> Literal["interview_prep", "end", "error"]:
    """Determine next step after match analysis.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    if state.get("error"):
        return "error"
    
    match_analysis = state.get("match_analysis")
    if not match_analysis:
        return "error"
    
    # Check if user wants to proceed to interview prep
    user_prefs = state.get("user_preferences", {})
    proceed_to_interview = user_prefs.get("proceed_to_interview", False)
    
    if proceed_to_interview:
        return "interview_prep"
    
    # End workflow after analysis
    return "end"


def route_after_interview_prep(
    state: JobMittrState
) -> Literal["interview_active", "error"]:
    """Determine if interview can start.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    if state.get("error"):
        return "error"
    
    questions = state.get("interview_questions", [])
    if not questions:
        return "error"
    
    return "interview_active"


__all__ = [
    "route_after_resume",
    "route_after_search",
    "route_after_job_search",
    "route_after_selection",
    "route_after_match_analysis",
    "route_after_interview_prep",
]