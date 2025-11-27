"""Refactored Interview UI - thin coordinator delegating to specialized components."""

import streamlit as st
import base64
from typing import Dict, Any

from components.interview.session import InterviewSessionController
from components.interview.header import InterviewHeader
from components.interview.question_card import QuestionCard
from components.interview.recorder import ResponseRecorder
from components.interview.feedback_display import FeedbackDisplay
from components.interview.navigation import NavigationButtons
from components.interview.report import FinalReport


class InterviewUI:
    """Main UI coordinator - delegates to specialized components (thin layer)."""
    
    def __init__(self):
        self.controller = InterviewSessionController()
        self.header = InterviewHeader()
        self.question_card = QuestionCard()
        self.recorder = ResponseRecorder()
        self.feedback_display = FeedbackDisplay()
        self.navigation = NavigationButtons()
        self.report = FinalReport()
    
    def start_interview_session(
        self, 
        job_data: Dict[str, Any], 
        questions: list,
        interview_type: str = "Technical Interview"
    ):
        """Initialize interview session via controller."""
        self.controller.start_session(job_data, questions, interview_type)
    
    def render_interview_header(self):
        """Render header component."""
        self.header.render(st.session_state.interview_session)
    
    def render_current_question(self):
        """Render question card component."""
        session = st.session_state.interview_session
        if not session or session.current_question_index >= len(session.questions):
            return
        
        current_q = session.questions[session.current_question_index]
        
        self.question_card.render(
            question=current_q,
            question_number=session.current_question_index + 1,
            total_questions=len(session.questions),
            on_play_audio=self._play_question_audio
        )
    
    def render_response_recorder(self):
        """Render recorder component."""
        self.recorder.render(on_audio_recorded=self._process_audio_response)
    
    def render_navigation_buttons(self):
        """Render navigation component."""
        session = st.session_state.interview_session
        
        self.navigation.render(
            session=session,
            on_previous=self._navigate_previous,
            on_next=self._navigate_next,
            on_finish=self.render_final_report
        )
    
    def render_final_report(self):
        """Render final report component."""
        self.controller.finish_session()
        self.report.render(st.session_state.interview_session)
    
    # Private helper methods (callbacks)
    
    def _play_question_audio(self, question_text: str, question_type: str, volume: float):
        """Generate and play question audio."""
        try:
            with st.spinner("Generating audio..."):
                audio_bytes = self.controller.generate_question_audio(question_text, question_type)
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            audio_html = f"""
            <audio id="question-audio" autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("question-audio");
                if (audio) {{
                    audio.volume = {volume};
                }}
            </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to generate audio: {str(e)}")
    
    def _process_audio_response(self, audio_bytes: bytes):
        """Process audio response via controller."""
        with st.spinner("Transcribing your response..."):
            try:
                result = self.controller.process_audio_response(audio_bytes)
                
                st.markdown("**Your Transcribed Response:**")
                st.write(result['transcribed_text'])
                
                # Display feedback
                with st.spinner("Analyzing your response..."):
                    self.feedback_display.render(result['feedback'])
                
            except Exception as e:
                st.error(f"Error processing response: {str(e)}")
    
    def _navigate_previous(self):
        """Navigate to previous question."""
        session = st.session_state.interview_session
        self.controller.navigate_to_question(session.current_question_index - 1)
        st.rerun()
    
    def _navigate_next(self):
        """Navigate to next question."""
        session = st.session_state.interview_session
        self.controller.navigate_to_question(session.current_question_index + 1)
        st.rerun()