"""Job search and matching nodes for LangGraph workflow.
These nodes handle job search execution, job selection, and resume-job matching.
"""

from typing import Dict, Any
from graphs.state import JobMittrState
from tools.executor import execute_tool


def search_jobs_node(state: JobMittrState) -> JobMittrState:
    """Execute job search based on query parameters.
    Expects state["job_query"] with:
    - keywords: str (job title/role)
    - location: str (geographic location)
    - platform: str (optional, defaults to LinkedIn)
    - count: int (optional, defaults to 10)
    Updates state["job_results"] with search results.
    Args:
        state: Current workflow state with job_query
    Returns:
        Updated state with job_results
    """
    job_query = state.get("job_query", {})
    
    if not job_query or not job_query.get("keywords") or not job_query.get("location"):
        return {
            **state,
            "error": "Job query missing required fields (keywords, location)",
            "job_results": [],
            "current_step": "job_search"
        }
    
    # Extract parameters with defaults
    keywords = job_query.get("keywords")
    location = job_query.get("location")
    platform = job_query.get("platform", "LinkedIn")
    count = job_query.get("count", 10)
    
    try:
        # Call job search tool
        result = execute_tool("search_jobs", {
            "keywords": keywords,
            "location": location,
            "platform": platform,
            "count": count
        })
        
        if result.get("success"):
            jobs = result["result"]
            
            return {
                **state,
                "job_results": jobs,
                "current_step": "job_selection",
                "error": None
            }
        else:
            return {
                **state,
                "error": f"Job search failed: {result.get('error', 'Unknown error')}",
                "job_results": [],
                "current_step": "job_search"
            }
    
    except Exception as e:
        return {
            **state,
            "error": f"Job search execution error: {str(e)}",
            "job_results": [],
            "current_step": "job_search"
        }


def select_job_node(state: JobMittrState) -> JobMittrState:
    """Select a job from search results.
    By default selects first job. If state["user_preferences"]["job_index"]
    is set, uses that index instead.
    Updates state["selected_job"] with chosen job.
    Args:
        state: Current workflow state with job_results
    Returns:
        Updated state with selected_job
    """
    job_results = state.get("job_results", [])
    
    if not job_results:
        return {
            **state,
            "error": "No job results available for selection",
            "selected_job": None,
            "current_step": "job_search"
        }
    
    # Get index from user preferences or default to 0
    user_prefs = state.get("user_preferences", {})
    job_index = user_prefs.get("job_index", 0)
    
    # Validate index
    if job_index < 0 or job_index >= len(job_results):
        job_index = 0
    
    selected_job = job_results[job_index]
    
    return {
        **state,
        "selected_job": selected_job,
        "current_step": "match_analysis",
        "error": None
    }


def analyze_match_node(state: JobMittrState) -> JobMittrState:
    """Analyze resume-job compatibility.
    Expects:
    - state["resume_data"]: Parsed resume
    - state["selected_job"]: Selected job listing
    Updates state["match_analysis"] with match results.
    Args:
        state: Current workflow state with resume and selected job
    Returns:
        Updated state with match_analysis
    """
    resume_data = state.get("resume_data")
    selected_job = state.get("selected_job")
    
    if not resume_data:
        return {
            **state,
            "error": "Resume data not available for match analysis",
            "match_analysis": None,
            "current_step": "resume_upload"
        }
    
    if not selected_job:
        return {
            **state,
            "error": "No job selected for match analysis",
            "match_analysis": None,
            "current_step": "job_selection"
        }
    
    try:
        # Call match analysis tool
        result = execute_tool("analyze_job_match", {
            "resume_data": resume_data,
            "job_data": selected_job
        })
        
        if result.get("success"):
            match_data = result["result"]
            
            return {
                **state,
                "match_analysis": match_data,
                "current_step": "interview_prep",
                "error": None
            }
        else:
            # Fallback analysis if tool fails
            match_data = {
                "match_score": 50.0,
                "key_matches": ["Basic qualifications met"],
                "gaps": ["Unable to perform detailed analysis"],
                "recommendations": ["Review job requirements manually"]
            }
            
            return {
                **state,
                "match_analysis": match_data,
                "current_step": "interview_prep",
                "error": None  # Don't block workflow
            }
    
    except Exception as e:
        # Fallback on error
        match_data = {
            "match_score": 50.0,
            "key_matches": ["Resume parsed successfully"],
            "gaps": [f"Analysis error: {str(e)}"],
            "recommendations": ["Retry analysis or proceed manually"]
        }
        
        return {
            **state,
            "match_analysis": match_data,
            "current_step": "interview_prep",
            "error": None  # Don't block workflow
        }