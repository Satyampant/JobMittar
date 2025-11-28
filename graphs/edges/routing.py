"""Enhanced routing logic for master orchestration graph."""

from typing import Literal
from graphs.state import JobMittrState


def route_by_intent(state: JobMittrState) -> Literal["parse_resume", "search_jobs", "generate_questions", "error"]:
    """Route based on classified user intent.
    
    Args:
        state: Current workflow state with current_step set by intent classifier
        
    Returns:
        Next node name based on intent
    """
    current_step = state.get("current_step", "resume_upload")
    
    if state.get("error"):
        return "error"
    
    # Route based on current step
    if current_step == "resume_upload":
        return "parse_resume"
    elif current_step == "job_search":
        # Check if resume exists, otherwise require it first
        if state.get("resume_data"):
            return "search_jobs"
        else:
            return "parse_resume"  # Auto-require resume first
    elif current_step == "interview_prep":
        # Check if job is selected
        if state.get("selected_job"):
            return "generate_questions"
        elif state.get("resume_data"):
            return "search_jobs"  # Need job selection first
        else:
            return "parse_resume"  # Need everything
    
    return "error"


def route_after_resume(state: JobMittrState) -> Literal["job_search", "complete", "error"]:
    """Route after resume processing completes.
    
    Args:
        state: Current workflow state after resume analysis
        
    Returns:
        Next step: auto-trigger job search or end
    """
    if state.get("error"):
        return "error"
    
    if not state.get("resume_data"):
        return "error"
    
    # Check user preferences for next action
    user_prefs = state.get("user_preferences", {})
    auto_job_search = user_prefs.get("auto_job_search", True)
    
    if auto_job_search and state.get("job_query"):
        return "job_search"
    
    # Resume complete, await user action
    return "complete"


def route_after_job_selection(state: JobMittrState) -> Literal["analyze_match", "generate_questions", "complete", "error"]:
    """Route after job selection based on user preference.
    
    Args:
        state: Current workflow state after job selection
        
    Returns:
        Next step based on user preference
    """
    if state.get("error"):
        return "error"
    
    if not state.get("selected_job"):
        return "error"
    
    # Check user preferences
    user_prefs = state.get("user_preferences", {})
    next_action = user_prefs.get("next_action", "analysis")
    
    if next_action == "interview":
        return "generate_questions"
    elif next_action == "analysis":
        return "analyze_match"
    
    # Default to analysis
    return "analyze_match"


def route_after_match_analysis(state: JobMittrState) -> Literal["generate_questions", "complete", "error"]:
    """Route after match analysis completes.
    
    Args:
        state: Current workflow state after match analysis
        
    Returns:
        Next step: interview prep or end
    """
    if state.get("error"):
        return "error"
    
    if not state.get("match_analysis"):
        return "error"
    
    # Check if user wants interview prep
    user_prefs = state.get("user_preferences", {})
    proceed_to_interview = user_prefs.get("proceed_to_interview", False)
    
    if proceed_to_interview:
        return "generate_questions"
    
    return "complete"


def route_from_intent_classifier(state: JobMittrState) -> Literal["parse_resume", "search_jobs", "generate_questions", "error"]:
    """Route from intent classifier to appropriate subgraph entry.
    
    Args:
        state: State after intent classification
        
    Returns:
        Entry point for the appropriate subgraph
    """
    return route_by_intent(state)


def route_to_completion_or_error(state: JobMittrState) -> Literal["complete", "error"]:
    """Final routing to completion or error handling.
    
    Args:
        state: Current workflow state
        
    Returns:
        Either complete or error
    """
    if state.get("error"):
        return "error"
    return "complete"