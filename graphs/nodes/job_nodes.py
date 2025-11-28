
from typing import Dict, Any
from graphs.state import JobMittrState
from tools.executor import execute_tool


def search_jobs_node(state: JobMittrState) -> JobMittrState:
    
    job_query = state.get("job_query", {})
    
    if not job_query or not job_query.get("keywords") or not job_query.get("location"):
        return {
            **state,
            "error": "Job query missing required fields (keywords, location)",
            "job_results": [],
            "current_step": "job_search"
        }
    
    keywords = job_query.get("keywords")
    location = job_query.get("location")
    platform = job_query.get("platform", "LinkedIn")
    count = job_query.get("count", 10)
    
    try:
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
    job_results = state.get("job_results", [])
    
    if not job_results:
        return {
            **state,
            "error": "No job results available for selection",
            "selected_job": None,
            "current_step": "job_search"
        }
    
    user_prefs = state.get("user_preferences", {})
    job_index = user_prefs.get("job_index", 0)
    
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
                "error": None  
            }
    
    except Exception as e:
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
            "error": None  
        }