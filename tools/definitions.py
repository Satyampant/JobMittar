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

# Interview Audio Generation Tool
generate_audio_tool = {
    "name": "generate_question_audio",
    "description": "Generate text-to-speech audio for an interview question using Groq TTS. Returns audio bytes in MP3 format.",
    "parameters": {
        "type": "object",
        "properties": {
            "question_text": {"type": "string", "description": "The interview question to convert to speech"},
            "question_type": {"type": "string", "enum": ["Technical", "Behavioral", "Situational", "General"], "default": "General", "description": "Type of interview question"}
        },
        "required": ["question_text"]
    }
}

# Audio Transcription Tool
transcribe_audio_tool = {
    "name": "transcribe_candidate_response",
    "description": "Transcribe candidate's audio response to text using Deepgram. Accepts audio bytes and returns transcribed text.",
    "parameters": {
        "type": "object",
        "properties": {
            "audio_bytes": {"type": "string", "description": "Base64-encoded audio data in MP3/WAV format"},
        },
        "required": ["audio_bytes"]
    }
}

# Interview Feedback Generation Tool
generate_feedback_tool = {
    "name": "generate_interview_feedback",
    "description": "Generate AI-powered feedback for a candidate's interview response using Groq LLM. Returns structured feedback with scores and suggestions.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The interview question that was asked"},
            "question_type": {"type": "string", "enum": ["Technical", "Behavioral", "Situational", "General"], "description": "Type of interview question"},
            "candidate_response": {"type": "string", "description": "Candidate's transcribed response text"}
        },
        "required": ["question", "question_type", "candidate_response"]
    }
}

# Tool Registry for dynamic lookup
TOOL_REGISTRY = {
    "search_jobs": search_jobs_tool,
    "analyze_job_match": analyze_match_tool,
    "generate_interview_questions": generate_questions_tool,
    "generate_question_audio": generate_audio_tool,
    "transcribe_candidate_response": transcribe_audio_tool,
    "generate_interview_feedback": generate_feedback_tool
}
