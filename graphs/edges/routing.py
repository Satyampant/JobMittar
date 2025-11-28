
from typing import Literal
from graphs.state import JobMittrState


def route_by_intent(state: JobMittrState) -> Literal["parse_resume", "search_jobs", "generate_questions", "error"]:
    current_step = state.get("current_step", "resume_upload")
    
    if state.get("error"):
        return "error"
    
    if current_step == "resume_upload":
        return "parse_resume"
    elif current_step == "job_search":
        if state.get("resume_data"):
            return "search_jobs"
        else:
            return "parse_resume"  
    elif current_step == "interview_prep":
        if state.get("selected_job"):
            return "generate_questions"
        elif state.get("resume_data"):
            return "search_jobs"  
        else:
            return "parse_resume"  
    
    return "error"


def route_after_resume(state: JobMittrState) -> Literal["job_search", "complete", "error"]:
    if state.get("error"):
        return "error"
    
    if not state.get("resume_data"):
        return "error"
    
    user_prefs = state.get("user_preferences", {})
    auto_job_search = user_prefs.get("auto_job_search", False)  
    
    if auto_job_search and state.get("job_query"):
        return "job_search"
    
    return "complete"

def route_after_job_selection(state: JobMittrState) -> Literal["analyze_match", "generate_questions", "complete", "error"]:
    if state.get("error"):
        return "error"
    
    if not state.get("selected_job"):
        return "error"
    
    user_prefs = state.get("user_preferences", {})
    next_action = user_prefs.get("next_action", "analysis")
    
    if next_action == "interview":
        return "generate_questions"
    elif next_action == "analysis":
        return "analyze_match"
    
    return "analyze_match"


def route_after_match_analysis(state: JobMittrState) -> Literal["generate_questions", "complete", "error"]:
    if state.get("error"):
        return "error"
    
    if not state.get("match_analysis"):
        return "error"
    
    user_prefs = state.get("user_preferences", {})
    proceed_to_interview = user_prefs.get("proceed_to_interview", False)
    
    if proceed_to_interview:
        return "generate_questions"
    
    return "complete"


def route_from_intent_classifier(state: JobMittrState) -> Literal["parse_resume", "search_jobs", "generate_questions", "error"]:
    return route_by_intent(state)


def route_to_completion_or_error(state: JobMittrState) -> Literal["complete", "error"]:
    if state.get("error"):
        return "error"
    return "complete"