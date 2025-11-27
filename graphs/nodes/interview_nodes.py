"""Interview preparation nodes for LangGraph workflow.
These nodes handle question generation, session management, and feedback loop.
"""

from typing import Dict, Any, List
from datetime import datetime
from graphs.state import JobMittrState
from tools.executor import execute_tool
from models.interview import InterviewSessionState, InterviewQuestionResponse


def generate_questions_node(state: JobMittrState) -> JobMittrState:
    """Generate interview questions based on selected job.
    Expects:
    - state["selected_job"]: Job data
    - state["user_preferences"]["question_count"]: Number of questions (optional)
    Updates state["interview_questions"] with generated questions.
    Args:
        state: Current workflow state
    Returns:
        Updated state with interview_questions
    """
    selected_job = state.get("selected_job")
    
    if not selected_job:
        return {
            **state,
            "error": "No job selected for interview preparation",
            "interview_questions": [],
            "current_step": "job_selection"
        }
    
    # Get question count from preferences or default to 10
    user_prefs = state.get("user_preferences", {})
    question_count = user_prefs.get("question_count", 10)
    
    try:
        # Generate questions using tool
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
    """Initialize live interview session with generated questions.
    Expects:
    - state["interview_questions"]: Generated questions
    - state["selected_job"]: Job data
    Creates and stores InterviewSessionState in state["interview_session"].
    Args:
        state: Current workflow state
    Returns:
        Updated state with interview_session
    """
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
    
    # Get interview type from preferences
    user_prefs = state.get("user_preferences", {})
    interview_type = user_prefs.get("interview_type", "Technical Interview")
    
    # Create session state
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
    
    # Convert Pydantic model to dict for state storage
    session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": session_dict,
        "current_step": "interview_active",
        "error": None
    }


def conduct_question_node(state: JobMittrState) -> JobMittrState:
    """Conduct single question: generate audio, wait for response, transcribe, provide feedback.
    Args:
        state: Current workflow state
    Returns:
        Updated state with new response added
    """
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return {
            **state,
            "error": "No active interview session",
            "current_step": "interview_prep"
        }
    
    # Reconstruct session state
    session = InterviewSessionState(**session_dict)
    
    if session.current_question_index >= len(session.questions):
        return {
            **state,
            "error": "Question index out of bounds",
            "current_step": "interview_complete"
        }
    
    current_q = session.questions[session.current_question_index]
    
    # Step 1: Generate TTS audio (optional - can be done in UI)
    try:
        audio_result = execute_tool("generate_question_audio", {
            "question_text": current_q.get("question", ""),
            "question_type": current_q.get("category", "General")
        })
        
        if not audio_result.get("success"):
            # Non-blocking - continue without audio
            pass
    except Exception:
        pass  # Audio generation is optional
    
    # Step 2: Get user audio response from state
    user_audio = state.get("user_audio_response")
    
    if not user_audio:
        # No response yet - wait for user input
        # In real workflow, this would be handled by human-in-the-loop
        return {
            **state,
            "error": None,
            "current_step": "awaiting_response",
            "messages": ["Waiting for candidate audio response..."]
        }
    
    # Step 3: Transcribe audio
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
    
    # Step 4: Generate feedback
    try:
        feedback_result = execute_tool("generate_interview_feedback", {
            "question": current_q.get("question", ""),
            "question_type": current_q.get("category", "General"),
            "candidate_response": transcribed_text
        })
        
        if not feedback_result.get("success"):
            # Provide fallback feedback
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
    
    # Step 5: Create response object
    from models.interview import InterviewFeedback
    feedback = InterviewFeedback(**feedback_data)
    
    response = InterviewQuestionResponse(
        question_id=session.current_question_index,
        question_text=current_q.get("question", ""),
        transcribed_text=transcribed_text,
        time_taken_seconds=None,  # Can be tracked separately
        feedback=feedback.to_formatted_string(),
        confidence_score=feedback.confidence_score,
        accuracy_score=feedback.accuracy_score,
        timestamp=datetime.now()
    )
    
    # Append to session responses
    session.responses.append(response)
    
    # Update session dict
    updated_session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": updated_session_dict,
        "current_step": "interview_active",
        "user_audio_response": None,  # Clear for next question
        "error": None
    }


def advance_question_node(state: JobMittrState) -> JobMittrState:
    """Advance to next question in interview session.
    Increments current_question_index.
    Args:
        state: Current workflow state
    Returns:
        Updated state with incremented index
    """
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return {
            **state,
            "error": "No active interview session",
            "current_step": "interview_prep"
        }
    
    session = InterviewSessionState(**session_dict)
    
    # Increment question index
    session.current_question_index += 1
    
    # Update session dict
    updated_session_dict = session.model_dump()
    
    return {
        **state,
        "interview_session": updated_session_dict,
        "current_step": "interview_active",
        "error": None
    }


def finalize_interview_node(state: JobMittrState) -> JobMittrState:
    """Finalize interview session - mark as complete and generate summary.
    Args:
        state: Current workflow state
    Returns:
        Updated state with finalized session
    """
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return {
            **state,
            "error": "No active interview session to finalize",
            "current_step": "interview_prep"
        }
    
    session = InterviewSessionState(**session_dict)
    
    # Mark session as inactive
    session.is_active = False
    session.session_end_time = datetime.now()
    
    # Calculate summary metrics
    avg_confidence = session.average_confidence
    avg_accuracy = session.average_accuracy
    
    # Update session dict
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