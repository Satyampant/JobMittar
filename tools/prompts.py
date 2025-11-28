
from config import get_settings

def get_agent_prompts():
    settings = get_settings()
    return {
        "job_search": settings.prompts.job_search_agent,
        "match_analysis": settings.prompts.match_analysis_agent,
        "interview_prep": settings.prompts.interview_prep_agent,
        "interview": settings.prompts.interview_agent 
    }

AGENT_PROMPTS = get_agent_prompts()