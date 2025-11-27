"""LLM-based resume extraction with configuration-driven prompts."""

import instructor
from groq import Groq
from models.resume import Resume
from config import get_settings


def extract_resume(resume_text: str) -> Resume:
    """Extract structured resume data using LLM with configuration."""
    settings = get_settings()
    client = instructor.from_groq(Groq(api_key=settings.groq_api_key), mode=instructor.Mode.JSON)
    
    try:
        return client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": f"{settings.prompts.resume_extraction}\n\nResume:\n{resume_text}"}],
            response_model=Resume,
            max_tokens=settings.api.max_tokens,
            temperature=0.3
        )
    except Exception:
        return Resume(name="Unknown", email="unknown@email.com", phone=None, 
                     summary="Failed to parse resume", skills=[], education=[], experience=[])
