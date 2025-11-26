"""Interactive interview UI component maintaining JobMittar design consistency."""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from streamlit_mic_recorder import mic_recorder
import time

from models.interview import InterviewSessionState, InterviewQuestionResponse, InterviewFeedback
from tools.interview_service import InterviewService
from ui_utils import COLORS


class InterviewUI:
    """Interactive interview interface component."""
    
    def __init__(self):
        self.service = InterviewService()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize or reset interview session state."""
        if "interview_session" not in st.session_state:
            st.session_state.interview_session = None
        if "current_question_start_time" not in st.session_state:
            st.session_state.current_question_start_time = None
        if "audio_volume" not in st.session_state:
            st.session_state.audio_volume = 1.0
        if "recorder_key" not in st.session_state:
            st.session_state.recorder_key = "recorder_0"
    
    def start_interview_session(
        self, 
        job_data: Dict[str, Any], 
        questions: list,
        interview_type: str = "Technical Interview"
    ):
        """Initialize a new interview session.
        
        Args:
            job_data: Selected job information
            questions: List of interview questions
            interview_type: Type of interview
        """
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
    
    def render_interview_header(self):
        """Render interview header with progress."""
        session = st.session_state.interview_session
        if not session:
            return
        
        # Header with gradient (matching JobMittar style)
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
        padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 3px 10px rgba(0,0,0,0.15);'>
            <h2 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
            🎙️ Live Interview: {session.job_title}</h2>
            <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
            {session.company_name} | {session.interview_type}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = session.progress_percentage / 100
        st.markdown(f"""
        <div style="background-color: {COLORS['primary']}; color: white; 
        padding: 10px 15px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
        <h4 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
        Progress: {len(session.responses)}/{len(session.questions)} Questions Completed</h4>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress)
    
    def render_current_question(self):
        """Render current question with audio playback."""
        session = st.session_state.interview_session
        if not session or session.current_question_index >= len(session.questions):
            return
        
        current_q = session.questions[session.current_question_index]
        question_text = current_q.get('question', 'Question not available')
        question_category = current_q.get('category', 'General')
        
        # Question card (matching JobMittar card style)
        st.markdown(f"""
        <div style="background-color: #111111; border-radius: 10px; padding: 20px; 
        margin-bottom: 20px; border-left: 4px solid {COLORS['accent3']};">
            <h3 style="color: {COLORS['primary']}; margin-top: 0;">
            Question {session.current_question_index + 1} of {len(session.questions)}</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #333;">{question_text}</p>
            <span style="background-color: {COLORS['secondary']}; color: white; 
            padding: 5px 12px; border-radius: 15px; font-weight: bold;">
            {question_category}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Audio controls
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("### Audio Settings")
            st.session_state.audio_volume = st.slider(
                "Volume", 0.0, 1.0, st.session_state.audio_volume, 0.1,
                key=f"volume_{session.current_question_index}"
            )
        
        with col2:
            st.markdown("### ")
            if st.button("🔊 Play Question", key=f"play_{session.current_question_index}"):
                self._play_question_audio(question_text, question_category)
    
    def _play_question_audio(self, question_text: str, question_type: str):
        """Generate and play question audio."""
        try:
            with st.spinner("Generating audio..."):
                audio_bytes = self.service.generate_question_audio(
                    question_text, question_type
                )
                audio_base64 = self.service.encode_audio_base64(audio_bytes)
            
            audio_html = f"""
            <audio id="question-audio" autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("question-audio");
                if (audio) {{
                    audio.volume = {st.session_state.audio_volume};
                }}
            </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to generate audio: {str(e)}")
    
    def render_response_recorder(self):
        """Render voice recorder for candidate response."""
        session = st.session_state.interview_session
        if not session:
            return
        
        st.markdown("### 🎤 Your Response")
        st.markdown(f"""
        <div style="background-color: {COLORS['panel_bg']}; padding: 15px; 
        border-radius: 8px; margin-bottom: 15px;">
        <p>Click <strong>Start Recording</strong> to begin your answer. 
        Click <strong>Stop Recording</strong> when you're done.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recorder
        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            key=st.session_state.recorder_key
        )
        
        if audio:
            # Start timer if not already started
            if st.session_state.current_question_start_time is None:
                st.session_state.current_question_start_time = time.time()
            
            # Show audio playback
            st.audio(audio['bytes'])
            
            # Process response
            self._process_audio_response(audio['bytes'])
    
    def _process_audio_response(self, audio_bytes: bytes):
        """Process audio response and generate feedback."""
        session = st.session_state.interview_session
        current_q = session.questions[session.current_question_index]
        
        with st.spinner("Transcribing your response..."):
            try:
                # Transcribe audio
                transcribed_text = self.service.transcribe_audio(audio_bytes)
                
                st.markdown("**Your Transcribed Response:**")
                st.write(transcribed_text)
                
                # Calculate time taken
                time_taken = None
                if st.session_state.current_question_start_time:
                    time_taken = time.time() - st.session_state.current_question_start_time
                
                # Generate AI feedback
                with st.spinner("Analyzing your response..."):
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
                
                # Display feedback
                self._render_feedback(feedback)
                
            except Exception as e:
                st.error(f"Error processing response: {str(e)}")
    
    def _render_feedback(self, feedback):
        """Render AI feedback in JobMittar style."""
        st.markdown(f"""
        <div style="background-color: #111111; border-radius: 10px; padding: 20px; 
        margin-top: 20px; border-left: 4px solid {COLORS['success']};">
            <h3 style="color: {COLORS['success']}; margin-top: 0;">🤖 AI Feedback</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Scores
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background-color: {COLORS['primary']}; color: white; 
            padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin: 0; color: white;">Confidence</h4>
                <h2 style="margin: 10px 0; color: white;">{feedback.confidence_score}/10</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color: {COLORS['secondary']}; color: white; 
            padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin: 0; color: white;">Accuracy</h4>
                <h2 style="margin: 10px 0; color: white;">{feedback.accuracy_score}/10</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed feedback
        st.markdown(feedback.to_formatted_string())
    
    def render_navigation_buttons(self):
        """Render navigation buttons."""
        session = st.session_state.interview_session
        if not session:
            return
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button(
                "⬅️ Previous Question",
                disabled=session.current_question_index == 0,
                key="prev_btn"
            ):
                session.current_question_index -= 1
                st.session_state.recorder_key = f"recorder_{session.current_question_index}"
                st.session_state.current_question_start_time = None
                st.rerun()
        
        with col2:
            if st.button(
                "➡️ Next Question",
                disabled=session.current_question_index >= len(session.questions) - 1,
                key="next_btn"
            ):
                session.current_question_index += 1
                st.session_state.recorder_key = f"recorder_{session.current_question_index}"
                st.session_state.current_question_start_time = None
                st.rerun()
        
        with col3:
            if st.button("✅ Finish Interview", key="finish_btn"):
                self.render_final_report()
    
    def render_final_report(self):
        """Render final interview report with scores and graphs."""
        session = st.session_state.interview_session
        if not session:
            return
        
        session.session_end_time = datetime.now()
        session.is_active = False
        
        st.success("🎉 Interview Completed!")
        
        # Average scores
        avg_confidence = session.average_confidence
        avg_accuracy = session.average_accuracy
        
        if avg_confidence and avg_accuracy:
            st.markdown(f"""
            <div style="background-color: {COLORS['primary']}; color: white; 
            padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.15);">
                <h3 style="margin: 0; color: white;">Overall Performance</h3>
                <p style="font-size: 1.2rem; margin: 10px 0; color: white;">
                <strong>Average Confidence:</strong> {avg_confidence:.1f}/10 | 
                <strong>Average Accuracy:</strong> {avg_accuracy:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Performance chart
            self._render_performance_chart(session)
        
        # Detailed responses
        with st.expander("📋 Detailed Responses", expanded=False):
            for i, response in enumerate(session.responses, 1):
                st.markdown(f"### Question {i}")
                st.write(f"**Question:** {response.question_text}")
                st.write(f"**Your Response:** {response.transcribed_text}")
                st.write(f"**Time Taken:** {response.time_taken_formatted}")
                st.markdown(f"**Feedback:**\n{response.feedback}")
                st.markdown("---")
        
        # Download report
        self._render_download_button(session)
    
    def _render_performance_chart(self, session: InterviewSessionState):
        """Render performance chart using Plotly."""
        labels = [f"Q{i+1}" for i in range(len(session.responses))]
        confidence_data = [r.confidence_score for r in session.responses]
        accuracy_data = [r.accuracy_score for r in session.responses]
        
        fig = go.Figure(data=[
            go.Bar(
                name="Confidence",
                x=labels,
                y=confidence_data,
                marker_color=COLORS["primary"],
                text=confidence_data,
                textposition="auto"
            ),
            go.Bar(
                name="Accuracy",
                x=labels,
                y=accuracy_data,
                marker_color=COLORS["accent3"],
                text=accuracy_data,
                textposition="auto"
            )
        ])
        
        fig.update_layout(
            barmode="group",
            yaxis=dict(range=[0, 10], title="Score", gridcolor="#e5e7eb"),
            xaxis=dict(title="Questions"),
            title=dict(
                text="Interview Performance Scores",
                x=0.5,
                xanchor="center"
            ),
            template="plotly_white",
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_download_button(self, session: InterviewSessionState):
        """Render download button for interview report."""
        report = self._generate_markdown_report(session)
        
        st.download_button(
            label="📥 Download Interview Report",
            data=report.encode("utf-8"),
            file_name=f"interview_report_{session.job_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            key="download_interview_report"
        )
    
    def _generate_markdown_report(self, session: InterviewSessionState) -> str:
        """Generate markdown report."""
        report = f"""# Interview Report

**Position:** {session.job_title}
**Company:** {session.company_name}
**Interview Type:** {session.interview_type}
**Date:** {session.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}

---

## Overall Performance

- **Average Confidence Score:** {session.average_confidence:.1f}/10
- **Average Accuracy Score:** {session.average_accuracy:.1f}/10
- **Questions Answered:** {len(session.responses)}/{len(session.questions)}

---

## Detailed Responses

"""
        
        for i, response in enumerate(session.responses, 1):
            report += f"""### Question {i}

**Question:** {response.question_text}

**Your Response:**
{response.transcribed_text}

**Time Taken:** {response.time_taken_formatted}

**Scores:**
- Confidence: {response.confidence_score}/10
- Accuracy: {response.accuracy_score}/10

**AI Feedback:**
{response.feedback}

---

"""
        
        return report