"""Interview header component - displays progress and metadata."""

import streamlit as st
from models.interview import InterviewSessionState
from ui_utils import COLORS


class InterviewHeader:
    """Renders interview session header with progress."""
    
    def render(self, session: InterviewSessionState):
        """Render header with gradient and progress bar."""
        if not session:
            return
        
        # Header with gradient
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
        padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 3px 10px rgba(0,0,0,0.15);'>
            <h2 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
            🎙️ Live Interview: {session.job_title}</h2>
            <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
            {session.company_name} | {session.interview_type}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        progress = session.progress_percentage / 100
        st.markdown(f"""
        <div style="background-color: {COLORS['primary']}; color: white; 
        padding: 10px 15px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
        <h4 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
        Progress: {len(session.responses)}/{len(session.questions)} Questions Completed</h4>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress)