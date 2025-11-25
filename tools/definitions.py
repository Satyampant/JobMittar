"""Tool definitions for external API interactions."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    """Schema for tool definition compatible with LLM function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]
    
# SERP API Job Search Tool
search_jobs_tool = {
    "name": "search_jobs",
    "description": "Search for jobs using SERP API. Returns real job listings with titles, companies, descriptions, and application URLs.",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {"type": "string", "description": "Job title or keywords (e.g., 'Python Developer', 'Data Scientist')"},
            "location": {"type": "string", "description": "Job location (e.g., 'Remote', 'San Francisco, CA')"},
            "platform": {"type": "string", "enum": ["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "Monster"], "description": "Job platform to search"},
            "count": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5, "description": "Number of jobs to return"}
        },
        "required": ["keywords", "location"]
    }
}

# Job Match Analysis Tool
analyze_match_tool = {
    "name": "analyze_job_match",
    "description": "Analyze how well a resume matches a job description using Groq LLM. Returns match score, matching skills, gaps, and recommendations.",
    "parameters": {
        "type": "object",
        "properties": {
            "resume_data": {"type": "object", "description": "Parsed resume with skills, experience, and education"},
            "job_data": {"type": "object", "description": "Job listing with title, company, description, and requirements"}
        },
        "required": ["resume_data", "job_data"]
    }
}

# Interview Questions Generation Tool
generate_questions_tool = {
    "name": "generate_interview_questions",
    "description": "Generate interview questions using Groq LLM based on job description and resume. Returns structured questions with context, tips, and suggested answers.",
    "parameters": {
        "type": "object",
        "properties": {
            "job_data": {"type": "object", "description": "Job listing information"},
            "resume_data": {"type": "object", "description": "Parsed resume data (optional)"},
            "question_count": {"type": "integer", "minimum": 5, "maximum": 20, "default": 10, "description": "Number of questions to generate"}
        },
        "required": ["job_data"]
    }
}

# Tool Registry for dynamic lookup
TOOL_REGISTRY = {
    "search_jobs": search_jobs_tool,
    "analyze_job_match": analyze_match_tool,
    "generate_interview_questions": generate_questions_tool
}
