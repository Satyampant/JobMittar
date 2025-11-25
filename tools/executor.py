"""Tool execution engine with configuration-driven settings."""

from typing import Dict, Any
import instructor
from groq import Groq
from config import get_settings
from models.interview import Interview, InterviewQuestion
from models.skills import JobMatchAnalysis

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
    """Execute match analysis using Instructor with JobMatchAnalysis model."""
    settings = get_settings()
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    resume_skills = params['resume_data'].get('skills', [])
    job_title = params['job_data'].get('title', 'Unknown Position')
    job_description = params['job_data'].get('description', 'No description')
    
    prompt = f"""Analyze the match between this resume and job posting.

Resume Skills: {', '.join(resume_skills)}
Job Title: {job_title}
Job Description: {job_description[:1000]}

Provide:
1. An overall match score (0-100)
2. Key matching qualifications (list of strings)
3. Skill gaps or missing requirements (list of strings)
4. Specific recommendations to improve the match (list of strings)"""
    
    try:
        # Use the existing JobMatchAnalysis model from models.skills
        result = client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": prompt}],
            response_model=JobMatchAnalysis,
            max_tokens=settings.api.max_tokens,
            temperature=settings.api.temperature
        )
        
        return result.model_dump()
        
    except Exception as e:
        raise ToolExecutionError(f"Match analysis failed: {str(e)}")

def _execute_question_generation(params: Dict[str, Any]) -> list:
    """Execute question generation using Instructor with Interview model."""
    settings = get_settings()
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    job = params['job_data']
    count = params.get('question_count', 10)
    job_title = job.get('title', 'Unknown Position')
    company_name = job.get('company', 'Unknown Company')
    
    prompt = f"""Generate an interview preparation session with {count} high-quality questions.

Job Title: {job_title}
Company: {company_name}
Job Description: {job.get('description', 'No description available')[:500]}

Create an Interview object with:
- job_title: "{job_title}"
- company_name: "{company_name}"
- questions: List of {count} InterviewQuestion objects, each with:
  * question: The interview question text (at least 10 characters)
  * category: One of (Technical, Behavioral, Situational, General)
  * difficulty: One of (Easy, Medium, Hard)
  * suggested_answer: A suggested approach or answer
  * key_points: List of key points to cover"""
    
    try:
        # Use the Interview model which contains List[InterviewQuestion]
        result: Interview = client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": prompt}],
            response_model=Interview,
            max_tokens=settings.api.max_tokens,
            temperature=settings.api.temperature
        )
        
        # Return list of questions as dicts for compatibility with app.py
        return [
            {
                'question': q.question,
                'category': q.category,
                'difficulty': q.difficulty,
                'suggested_answer': q.suggested_answer,
                'tips': q.tips  # Uses the @property we added
            }
            for q in result.questions
        ]
        
    except Exception as e:
        raise ToolExecutionError(f"Failed to generate interview questions: {str(e)}")