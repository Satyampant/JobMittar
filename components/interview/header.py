"""Interview header component - displays progress and metadata."""

import streamlit as st
from models.interview import InterviewSessionState
from ui_utils import COLORS


class InterviewHeader:
    """Renders interview session header with progress."""
    
    def render(self, session: InterviewSessionState):
        """Render header with gold gradient and progress bar."""
        if not session:
            return
        
        # Header with gold gradient
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
        padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; 
        box-shadow: 0 4px 16px rgba(255, 184, 28, 0.4);'>
            <h2 style='color: #1A1D23; margin: 0; font-weight: 700; 
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);'>
            🎙️ Live Interview: {session.job_title}</h2>
            <p style='color: #1A1D23; font-size: 1.1rem; margin: 0.5rem 0 0 0; 
            font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.05);'>
            {session.company_name} | {session.interview_type}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator with gold
        progress = session.progress_percentage / 100
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}); 
        color: #1A1D23; padding: 12px 18px; border-radius: 8px; margin-bottom: 1rem; 
        box-shadow: 0 3px 10px rgba(255, 184, 28, 0.3);">
        <h4 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.05);">
        Progress: {len(session.responses)}/{len(session.questions)} Questions Completed</h4>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress)
