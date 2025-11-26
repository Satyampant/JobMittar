"""Tool execution engine with configuration-driven settings."""

from typing import Dict, Any
import base64
import instructor
from groq import Groq
from config import get_settings
from models.interview import Interview, InterviewQuestion, InterviewFeedback
from models.skills import JobMatchAnalysis

class ToolExecutionError(Exception):
    """Custom exception for tool execution failures."""
    pass

def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with parameters and handle errors."""
    handlers = {
        "search_jobs": _execute_serp_search,
        "analyze_job_match": _execute_match_analysis,
        "generate_interview_questions": _execute_question_generation,
        "generate_question_audio": _execute_audio_generation,
        "transcribe_candidate_response": _execute_transcription,
        "generate_interview_feedback": _execute_feedback_generation
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
    """Execute match analysis using config prompts and Instructor."""
    settings = get_settings()
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    # Extract data
    resume_skills = params['resume_data'].get('skills', [])
    resume_experience = params['resume_data'].get('experience', [])
    job_title = params['job_data'].get('title', 'Unknown Position')
    job_description = params['job_data'].get('description', 'No description')
    job_requirements = params['job_data'].get('requirements', 'Not specified')
    
    # Format prompt from config with variables
    prompt = settings.prompts.job_match_analysis.format(
        resume_skills=', '.join(resume_skills) if resume_skills else 'None listed',
        resume_experience='; '.join(resume_experience[:3]) if resume_experience else 'None listed',
        job_title=job_title,
        job_description=job_description[:1000],
        job_requirements=str(job_requirements)[:500]
    )
    
    try:
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
    """Execute question generation using config prompts and Instructor."""
    settings = get_settings()
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    job = params['job_data']
    count = params.get('question_count', 10)
    job_title = job.get('title', 'Unknown Position')
    company_name = job.get('company', 'Unknown Company')
    job_description = job.get('description', 'No description available')
    
    # Get required skills if available
    required_skills = 'Not specified'
    if isinstance(job.get('requirements'), dict):
        skills = job['requirements'].get('required_skills', [])
        if skills:
            required_skills = ', '.join(skills)
    
    # Format prompt from config with variables
    prompt = settings.prompts.interview_questions_generation.format(
        question_count=count,
        job_title=job_title,
        company_name=company_name,
        job_description=job_description[:800],
        required_skills=required_skills
    )
    
    try:
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
                'tips': q.tips
            }
            for q in result.questions
        ]
        
    except Exception as e:
        raise ToolExecutionError(f"Failed to generate interview questions: {str(e)}")
    

def _execute_audio_generation(params: Dict[str, Any]) -> bytes:
    """Execute audio generation using Groq TTS with config prompts."""
    from groq import Groq
    import tempfile
    import os
    
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)
    
    question_text = params['question_text']
    question_type = params.get('question_type', 'General')
    
    # Use centralized prompt from config
    prompt = settings.prompts.interview_audio_generation.format(
        question_type=question_type,
        question_text=question_text
    )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        temp_path = tmp_file.name
    
    try:
        response = client.audio.speech.create(
            model="playai-tts",
            voice="Deedee-PlayAI",
            input=prompt,
            response_format="mp3"
        )
        response.write_to_file(temp_path)
        
        with open(temp_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        return audio_bytes
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _execute_transcription(params: Dict[str, Any]) -> str:
    """Execute audio transcription using Deepgram."""
    import requests
    import tempfile
    import os
    
    settings = get_settings()
    
    # Decode base64 audio if provided as string
    audio_data = params.get('audio_bytes')
    if isinstance(audio_data, str):
        audio_data = base64.b64decode(audio_data)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(audio_data)
        tmpfile_path = tmpfile.name
    
    try:
        url = "https://api.deepgram.com/v1/listen"
        
        headers = {
            "Authorization": f"Token {settings.deepgram_api_key}",
            "Content-Type": "audio/mpeg"
        }
        
        params_dg = {
            "model": "nova-2",
            "smart_format": "true",
            "language": "en"
        }
        
        with open(tmpfile_path, "rb") as audio_file:
            response = requests.post(
                url,
                headers=headers,
                params=params_dg,
                data=audio_file
            )
        
        if response.status_code != 200:
            raise ToolExecutionError(f"Deepgram API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        try:
            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        except (KeyError, IndexError) as e:
            raise ToolExecutionError(f"Could not extract transcript: {str(e)}")
        
        if not transcript or not transcript.strip():
            return "No speech detected. Please try speaking louder and clearer."
        
        return transcript
        
    finally:
        if os.path.exists(tmpfile_path):
            try:
                os.remove(tmpfile_path)
            except:
                pass


def _execute_feedback_generation(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute feedback generation using Groq LLM with config prompts."""
    settings = get_settings()
    client = instructor.from_groq(
        Groq(api_key=settings.groq_api_key), 
        mode=instructor.Mode.JSON
    )
    
    question = params['question']
    question_type = params['question_type']
    candidate_response = params['candidate_response']
    
    # Determine interviewer type
    interviewer_type_map = {
        'Technical': 'Technical Expert',
        'Behavioral': 'Manager or Team Lead',
        'Situational': 'Manager or Team Lead',
        'General': 'HR Recruiter'
    }
    interviewer_type = interviewer_type_map.get(question_type, 'HR Recruiter')
    
    # Use centralized prompt from config
    prompt = settings.prompts.interview_feedback_generation.format(
        interviewer_type=interviewer_type,
        question=question,
        candidate_response=candidate_response
    )
    
    try:
        feedback: InterviewFeedback = client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": prompt}],
            response_model=InterviewFeedback,
            max_tokens=settings.api.max_tokens,
            temperature=0.5
        )
        
        return feedback.model_dump()
        
    except Exception as e:
        # Return fallback feedback
        return {
            "evaluation": f"Unable to generate detailed feedback: {str(e)}",
            "strengths": ["Response was recorded"],
            "weaknesses": ["Feedback generation encountered an error"],
            "suggestions": ["Try answering again with more detail"],
            "confidence_score": 5.0,
            "accuracy_score": 5.0
        }