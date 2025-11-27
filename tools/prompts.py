"""Agent prompt templates loaded from configuration.

This module provides agent-level prompts for autonomous decision-making.
For execution prompts (actual LLM calls), see config YAML files.
"""

from config import get_settings

def get_agent_prompts():
    """Load agent decision-making prompts from configuration."""
    settings = get_settings()
    return {
        "job_search": settings.prompts.job_search_agent,
        "match_analysis": settings.prompts.match_analysis_agent,
        "interview_prep": settings.prompts.interview_prep_agent,
        "interview": settings.prompts.interview_agent 
    }

# Backward compatibility
AGENT_PROMPTS = get_agent_prompts()