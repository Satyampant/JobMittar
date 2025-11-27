"""Interview session orchestration - handles business logic."""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
import time

from models.interview import InterviewSessionState, InterviewQuestionResponse
from tools.interview_service import InterviewService


class InterviewSessionController:
    """Orchestrates interview session workflow - business logic layer."""
    
    def __init__(self):
        self.service = InterviewService()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables."""
        if "interview_session" not in st.session_state:
            st.session_state.interview_session = None
        if "current_question_start_time" not in st.session_state:
            st.session_state.current_question_start_time = None
        if "audio_volume" not in st.session_state:
            st.session_state.audio_volume = 1.0
        if "recorder_key" not in st.session_state:
            st.session_state.recorder_key = "recorder_0"
    
    def start_session(
        self, 
        job_data: Dict[str, Any], 
        questions: List[Dict[str, Any]],
        interview_type: str = "Technical Interview"
    ):
        """Initialize a new interview session."""
        session = InterviewSessionState(
            job_title=job_data.get('title', 'Unknown Position'),
            company_name=job_data.get('company', 'Unknown Company'),
            interview_type=interview_type,
            questions=questions,
            responses=[],
            current_question_index=0,
            session_start_time=datetime.now(),
            is_active=True
        )
        st.session_state.interview_session = session
        st.session_state.recorder_key = "recorder_0"
        st.session_state.current_question_start_time = None
    
    def generate_question_audio(self, question_text: str, question_type: str) -> bytes:
        """Generate TTS audio for question."""
        return self.service.generate_question_audio(question_text, question_type)
    
    def process_audio_response(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Process audio response: transcribe + generate feedback."""
        session = st.session_state.interview_session
        if not session:
            raise ValueError("No active interview session")
        
        current_q = session.questions[session.current_question_index]
        
        # Start timer if not already started
        if st.session_state.current_question_start_time is None:
            st.session_state.current_question_start_time = time.time()
        
        # Transcribe audio
        transcribed_text = self.service.transcribe_audio(audio_bytes)
        
        # Calculate time taken
        time_taken = None
        if st.session_state.current_question_start_time:
            time_taken = time.time() - st.session_state.current_question_start_time
        
        # Generate AI feedback
        feedback = self.service.generate_feedback(
            question=current_q.get('question', ''),
            question_type=current_q.get('category', 'General'),
            candidate_response=transcribed_text
        )
        
        # Create response object
        response = InterviewQuestionResponse(
            question_id=session.current_question_index,
            question_text=current_q.get('question', ''),
            transcribed_text=transcribed_text,
            time_taken_seconds=time_taken,
            feedback=feedback.to_formatted_string(),
            confidence_score=feedback.confidence_score,
            accuracy_score=feedback.accuracy_score,
            timestamp=datetime.now()
        )
        
        # Update session
        session.responses.append(response)
        
        return {
            'transcribed_text': transcribed_text,
            'feedback': feedback
        }
    
    def navigate_to_question(self, index: int):
        """Navigate to specific question."""
        session = st.session_state.interview_session
        if session and 0 <= index < len(session.questions):
            session.current_question_index = index
            st.session_state.recorder_key = f"recorder_{index}"
            st.session_state.current_question_start_time = None
    
    def finish_session(self):
        """Mark session as complete."""
        session = st.session_state.interview_session
        if session:
            session.session_end_time = datetime.now()
            session.is_active = False