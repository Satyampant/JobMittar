
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import base64
import tempfile
from graphs.state import JobMittrState
from tools.executor import execute_tool
from models.interview import InterviewSessionState, InterviewQuestionResponse


AUDIO_DIR = Path("saved_interviews/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def _save_audio_to_disk(audio_bytes: bytes, question_id: int, thread_id: str) -> str:
    filename = f"{thread_id}_q{question_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    filepath = AUDIO_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(audio_bytes)
    
    return str(filepath)


def _load_audio_from_disk(audio_path: str) -> bytes:
    with open(audio_path, "rb") as f:
        return f.read()


def conduct_question_node_v2(state: JobMittrState) -> JobMittrState:
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return {
            **state,
            "error": "No active interview session",
            "current_step": "interview_prep"
        }
    
    session = InterviewSessionState(**session_dict)
    
    if session.current_question_index >= len(session.questions):
        return {
            **state,
            "error": "Question index out of bounds",
            "current_step": "interview_complete"
        }
    
    current_q = session.questions[session.current_question_index]
    
    try:
        audio_result = execute_tool("generate_question_audio", {
            "question_text": current_q.get("question", ""),
            "question_type": current_q.get("category", "General")
        })
        
        if audio_result.get("success"):
            thread_id = state.get("thread_id", "default")
            audio_path = _save_audio_to_disk(
                audio_result["result"],
                session.current_question_index,
                thread_id
            )
    except Exception:
        pass  # Non-blocking
    
    user_audio = state.get("user_audio_response")
    
    if not user_audio:
        return {
            **state,
            "error": None,
            "current_step": "awaiting_response",
            "messages": ["Waiting for candidate audio response..."]
        }
    
    thread_id = state.get("thread_id", "default")
    user_audio_path = _save_audio_to_disk(
        user_audio if isinstance(user_audio, bytes) else base64.b64decode(user_audio),
        session.current_question_index,
        thread_id
    )
    
    try:
        transcribe_result = execute_tool("transcribe_candidate_response", {
            "audio_bytes": user_audio
        })
        
        if not transcribe_result.get("success"):
            return {
                **state,
                "error": f"Transcription failed: {transcribe_result.get('error')}",
                "current_step": "interview_active"
            }
        
        transcribed_text = transcribe_result["result"]
    
    except Exception as e:
        return {
            **state,
            "error": f"Transcription error: {str(e)}",
            "current_step": "interview_active"
        }
    
    try:
        feedback_result = execute_tool("generate_interview_feedback", {
            "question": current_q.get("question", ""),
            "question_type": current_q.get("category", "General"),
            "candidate_response": transcribed_text
        })
        
        if not feedback_result.get("success"):
            feedback_data = {
                "evaluation": "Unable to generate detailed feedback",
                "strengths": ["Response recorded"],
                "weaknesses": ["Feedback unavailable"],
                "suggestions": ["Try again"],
                "confidence_score": 5.0,
                "accuracy_score": 5.0
            }
        else:
            feedback_data = feedback_result["result"]
    
    except Exception as e:
        feedback_data = {
            "evaluation": f"Feedback error: {str(e)}",
            "strengths": ["Response transcribed"],
            "weaknesses": ["Feedback generation failed"],
            "suggestions": ["Continue to next question"],
            "confidence_score": 5.0,
            "accuracy_score": 5.0
        }
    
    from models.interview import InterviewFeedback
    feedback = InterviewFeedback(**feedback_data)
    
    response = InterviewQuestionResponse(
        question_id=session.current_question_index,
        question_text=current_q.get("question", ""),
        audio_response_path=user_audio_path, 
        transcribed_text=transcribed_text,
        time_taken_seconds=None,
        feedback=feedback.to_formatted_string(),
        confidence_score=feedback.confidence_score,
        accuracy_score=feedback.accuracy_score,
        timestamp=datetime.now()
    )
    
    session.responses.append(response)
    
    updated_session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": updated_session_dict,
        "current_step": "interview_active",
        "user_audio_response": None,  
        "error": None
    }


from graphs.nodes.interview_nodes import (
    generate_questions_node,
    initialize_interview_session_node,
    advance_question_node,
    finalize_interview_node
)


__all__ = [
    'generate_questions_node',
    'initialize_interview_session_node',
    'conduct_question_node_v2',
    'advance_question_node',
    'finalize_interview_node'
]
