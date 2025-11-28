
from typing import Dict, Any
from groq import Groq
from langchain_core.messages import HumanMessage, AIMessage
from graphs.state import JobMittrState
from config import get_settings


def intent_classifier_node(state: JobMittrState) -> JobMittrState:
    messages = state.get("messages", [])
    
    if state.get("current_step") == "resume_upload":
        user_prefs = state.get("user_preferences", {})
        if not user_prefs.get("auto_job_search", False):
            return {
                **state,
                "current_step": "resume_upload",
                "error": None
            }

    if not messages:
        return {
            **state,
            "current_step": "resume_upload",
            "error": None
        }
    
    last_message = messages[-1] if messages else None
    if not last_message or not hasattr(last_message, 'content'):
        return {
            **state,
            "current_step": "resume_upload",
            "error": None
        }
    
    user_input = last_message.content
    
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)
    
    classification_prompt = f"""You are an intent classifier for a job search assistant. 
Classify the following user input into ONE of these intents:
- "resume_analysis": User wants to upload/analyze their resume
- "job_search": User wants to search for jobs
- "interview_prep": User wants interview preparation/practice

User input: "{user_input}"

Respond with ONLY the intent category, nothing else."""

    try:
        response = client.chat.completions.create(
            model=settings.api.groq_model,
            messages=[{"role": "user", "content": classification_prompt}],
            max_tokens=50,
            temperature=0.1
        )
        
        intent = response.choices[0].message.content.strip().lower()
        
        # Map intent to workflow step
        intent_map = {
            "resume_analysis": "resume_upload",
            "job_search": "job_search",
            "interview_prep": "interview_prep"
        }
        
        current_step = intent_map.get(intent, "resume_upload")
        
        return {
            **state,
            "current_step": current_step,
            "error": None,
            "messages": messages + [AIMessage(content=f"Intent classified as: {intent}")]
        }
    
    except Exception as e:
        # Fallback to resume upload on error
        return {
            **state,
            "current_step": "resume_upload",
            "error": f"Intent classification failed: {str(e)}"
        }


def error_handler_node(state: JobMittrState) -> JobMittrState:
    error = state.get("error")
    
    if not error:
        return state
    
    messages = state.get("messages", [])
    error_message = AIMessage(content=f"⚠️ Error occurred: {error}")
    
    return {
        **state,
        "error": None,  # Clear error
        "messages": messages + [error_message]
    }


def workflow_complete_node(state: JobMittrState) -> JobMittrState:
    messages = state.get("messages", [])
    current_step = state.get("current_step", "unknown")
    
    summary_parts = []
    
    if state.get("resume_data"):
        summary_parts.append("✅ Resume analyzed")
    
    if state.get("job_results"):
        summary_parts.append(f"✅ Found {len(state['job_results'])} jobs")
    
    if state.get("selected_job"):
        summary_parts.append("✅ Job selected")
    
    if state.get("match_analysis"):
        match_score = state["match_analysis"].get("match_score", 0)
        summary_parts.append(f"✅ Match analysis complete ({match_score}%)")
    
    if state.get("interview_questions"):
        summary_parts.append(f"✅ Generated {len(state['interview_questions'])} interview questions")
    
    session = state.get("interview_session")
    if session and not session.get("is_active", True):
        summary_parts.append("✅ Interview session completed")
    
    summary = "\n".join(summary_parts) if summary_parts else "Workflow completed"
    
    completion_message = AIMessage(
        content=f"🎉 **Workflow Complete!**\n\n{summary}\n\nWhat would you like to do next?"
    )
    
    return {
        **state,
        "messages": messages + [completion_message],
        "current_step": "complete"
    }