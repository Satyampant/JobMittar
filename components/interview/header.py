import streamlit as st
from models.interview import InterviewSessionState
from ui_utils import COLORS


class InterviewHeader:
    
    def render(self, session: InterviewSessionState):
        if not session:
            return
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["tertiary"]}); 
        padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; 
        box-shadow: 0 4px 16px rgba(108, 99, 255, 0.4);'>
            <h2 style='color: white; margin: 0; font-weight: 700; 
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
            🎙️ Live Interview: {session.job_title}</h2>
            <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; 
            font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
            {session.company_name} | {session.interview_type}</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress = session.progress_percentage / 100
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['tertiary']}); 
        color: white; padding: 12px 18px; border-radius: 8px; margin-bottom: 1rem; 
        box-shadow: 0 3px 10px rgba(108, 99, 255, 0.3);">
        <h4 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
        Progress: {len(session.responses)}/{len(session.questions)} Questions Completed</h4>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress)
