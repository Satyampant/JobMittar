"""Tool execution engine with configuration-driven settings."""

from typing import Dict, Any
from groq import Groq
from config import get_settings

import instructor
from models.interview import InterviewQuestion
from pydantic import BaseModel, Field
from typing import List

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
    """Execute Groq LLM match analysis using Instructor for structured output."""
    import instructor
    from groq import Groq
    from pydantic import BaseModel, Field
    from typing import List
    
    settings = get_settings()
    
    # Create Instructor client
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    # Define structured response model
    class MatchAnalysis(BaseModel):
        """Resume-job match analysis result."""
        match_score: float = Field(..., ge=0, le=100, description="Overall match percentage")
        key_matches: List[str] = Field(
            default_factory=list, 
            description="Key matching qualifications"
        )
        gaps: List[str] = Field(
            default_factory=list, 
            description="Missing qualifications or skill gaps"
        )
        recommendations: List[str] = Field(
            default_factory=list, 
            description="Actionable recommendations to improve match"
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
2. Key matching qualifications
3. Skill gaps or missing requirements
4. Specific recommendations to improve the match"""
    
    try:
        result = client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": prompt}],
            response_model=MatchAnalysis,
            max_tokens=settings.api.max_tokens,
            temperature=settings.api.temperature
        )
        
        return result.model_dump()
        
    except Exception as e:
        raise ToolExecutionError(f"Match analysis failed: {str(e)}")

def _execute_question_generation(params: Dict[str, Any]) -> list:
    """Execute Groq LLM question generation using Instructor for structured output."""
    
    settings = get_settings()
    
    # Create Instructor client (same pattern as resume_extractor.py)
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    job = params['job_data']
    count = params.get('question_count', 10)
    
    # Define response model for list of questions
    class InterviewQuestionsList(BaseModel):
        """Container for multiple interview questions."""
        questions: List[InterviewQuestion] = Field(
            ..., 
            min_length=1, 
            description="List of interview questions"
        )
    
    # Construct prompt
    prompt = f"""Generate {count} high-quality interview questions for the position of {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}.

Job Description: {job.get('description', 'No description available')[:500]}

For each question, provide:
- The question text
- Category (Technical, Behavioral, Situational, or General)
- Difficulty level (Easy, Medium, or Hard)
- A suggested answer approach
- Key points to cover in the answer"""
    
    try:
        # Use Instructor to get structured output
        result = client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": prompt}],
            response_model=InterviewQuestionsList,
            max_tokens=settings.api.max_tokens,
            temperature=settings.api.temperature
        )
        
        # Convert Pydantic models to dicts for compatibility with UI
        return [q.model_dump() for q in result.questions]
        
    except Exception as e:
        raise ToolExecutionError(f"Failed to generate interview questions: {str(e)}")