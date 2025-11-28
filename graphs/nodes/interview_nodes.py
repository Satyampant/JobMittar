
from typing import Dict, Any, List
from datetime import datetime
from graphs.state import JobMittrState
from tools.executor import execute_tool
from models.interview import InterviewSessionState, InterviewQuestionResponse


def generate_questions_node(state: JobMittrState) -> JobMittrState:
    selected_job = state.get("selected_job")
    
    if not selected_job:
        return {
            **state,
            "error": "No job selected for interview preparation",
            "interview_questions": [],
            "current_step": "job_selection"
        }
    
    user_prefs = state.get("user_preferences", {})
    question_count = user_prefs.get("question_count", 10)
    
    try:
        result = execute_tool("generate_interview_questions", {
            "job_data": selected_job,
            "resume_data": state.get("resume_data"),
            "question_count": question_count
        })
        
        if result.get("success"):
            questions = result["result"]
            
            return {
                **state,
                "interview_questions": questions,
                "current_step": "interview_setup",
                "error": None
            }
        else:
            return {
                **state,
                "error": f"Question generation failed: {result.get('error', 'Unknown error')}",
                "interview_questions": [],
                "current_step": "interview_prep"
            }
    
    except Exception as e:
        return {
            **state,
            "error": f"Question generation error: {str(e)}",
            "interview_questions": [],
            "current_step": "interview_prep"
        }


def initialize_interview_session_node(state: JobMittrState) -> JobMittrState:
    questions = state.get("interview_questions", [])
    selected_job = state.get("selected_job")
    
    if not questions:
        return {
            **state,
            "error": "No interview questions available for session",
            "interview_session": None,
            "current_step": "interview_prep"
        }
    
    if not selected_job:
        return {
            **state,
            "error": "No job selected for interview session",
            "interview_session": None,
            "current_step": "job_selection"
        }
    
    user_prefs = state.get("user_preferences", {})
    interview_type = user_prefs.get("interview_type", "Technical Interview")
    
    session = InterviewSessionState(
        job_title=selected_job.get("title", "Unknown Position"),
        company_name=selected_job.get("company", "Unknown Company"),
        interview_type=interview_type,
        questions=questions,
        responses=[],
        current_question_index=0,
        session_start_time=datetime.now(),
        is_active=True
    )
    
    session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": session_dict,
        "current_step": "interview_active",
        "error": None
    }


def conduct_question_node(state: JobMittrState) -> JobMittrState:
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
        
        if not audio_result.get("success"):
            pass
    except Exception:
        pass  
    
    user_audio = state.get("user_audio_response")
    
    if not user_audio:
        return {
            **state,
            "error": None,
            "current_step": "awaiting_response",
            "messages": ["Waiting for candidate audio response..."]
        }
    
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


def advance_question_node(state: JobMittrState) -> JobMittrState:
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return {
            **state,
            "error": "No active interview session",
            "current_step": "interview_prep"
        }
    
    session = InterviewSessionState(**session_dict)
    
    session.current_question_index += 1
    
    updated_session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": updated_session_dict,
        "current_step": "interview_active",
        "error": None
    }


def finalize_interview_node(state: JobMittrState) -> JobMittrState:
    
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return {
            **state,
            "error": "No active interview session to finalize",
            "current_step": "interview_prep"
        }
    
    session = InterviewSessionState(**session_dict)
    
    session.is_active = False
    session.session_end_time = datetime.now()
    
    avg_confidence = session.average_confidence
    avg_accuracy = session.average_accuracy
    
    updated_session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": updated_session_dict,
        "current_step": "interview_complete",
        "error": None,
        "messages": [
            f"Interview completed! {len(session.responses)}/{len(session.questions)} questions answered.",
            f"Average Confidence: {avg_confidence:.1f}/10" if avg_confidence else "No confidence scores",
            f"Average Accuracy: {avg_accuracy:.1f}/10" if avg_accuracy else "No accuracy scores"
        ]
    }