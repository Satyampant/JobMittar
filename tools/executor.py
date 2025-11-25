"""Tool execution engine with configuration-driven settings."""

from typing import Dict, Any
from groq import Groq
from config import get_settings

class ToolExecutionError(Exception):
    """Custom exception for tool execution failures."""
    pass

def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with parameters and handle errors."""
    handlers = {
        "search_jobs": _execute_serp_search,
        "analyze_job_match": _execute_match_analysis,
        "generate_interview_questions": _execute_question_generation
    }
    
    handler = handlers.get(tool_name)
    if not handler:
        raise ToolExecutionError(f"Unknown tool: {tool_name}")
    
    try:
        return {"success": True, "result": handler(parameters)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _execute_serp_search(params: Dict[str, Any]) -> list:
    """Execute SERP API job search using configuration."""
    import requests
    settings = get_settings()
    
    response = requests.get("https://serpapi.com/search", params={
        "engine": settings.api.serp_engine,
        "q": f"{params['keywords']} jobs in {params['location']}",
        "api_key": settings.serpapi_api_key
    })
    data = response.json()
    
    if "error" in data:
        raise ToolExecutionError(f"SERP API error: {data['error']}")
    
    return [{"title": job.get("title"), "company": job.get("company_name"), 
             "description": job.get("description", ""), "url": job.get("apply_link", {}).get("link")} 
            for job in data.get("jobs_results", [])[:params.get("count", 5)]]

def _execute_match_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Groq LLM match analysis using configuration."""
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)
    
    prompt = f"""Analyze resume-job match. Resume skills: {params['resume_data'].get('skills', [])}. 
Job: {params['job_data'].get('title', '')} - {params['job_data'].get('description', '')}.
Return JSON: {{"match_score": 0-100, "key_matches": [], "gaps": [], "recommendations": []}}"""
    
    response = client.chat.completions.create(
        model=settings.api.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.api.temperature,
        max_tokens=settings.api.max_tokens
    )
    
    import json
    return json.loads(response.choices[0].message.content)

def _execute_question_generation(params: Dict[str, Any]) -> list:
    """Execute Groq LLM question generation using configuration."""
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)
    job = params['job_data']
    count = params.get('question_count', 10)
    
    prompt = f"""Generate {count} interview questions for {job.get('title', '')} at {job.get('company', '')}.
Return JSON array: [{{"question": "", "context": "", "tips": "", "suggested_answer": ""}}]"""
    
    response = client.chat.completions.create(
        model=settings.api.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.api.temperature,
        max_tokens=settings.api.max_tokens
    )
    
    import json
    return json.loads(response.choices[0].message.content)
