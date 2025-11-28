import streamlit as st
from models.interview import InterviewFeedback
from ui_utils import COLORS


class FeedbackDisplay:
    
    def render(self, feedback: InterviewFeedback):
        st.markdown(f"""
        <div style="background-color: {COLORS['card_bg']}; border-radius: 10px; padding: 20px; 
        margin-top: 20px; border-left: 4px solid {COLORS['secondary']}; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
            <h3 style="color: {COLORS['secondary']}; margin-top: 0;">🤖 AI Feedback</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent1']}); 
            color: white; padding: 15px; border-radius: 8px; text-align: center; 
            box-shadow: 0 3px 10px rgba(108, 99, 255, 0.4);">
                <h4 style="margin: 0; color: white; font-weight: 600;">Confidence</h4>
                <h2 style="margin: 10px 0; color: white; font-weight: 700;">
                {feedback.confidence_score}/10</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLORS['tertiary']}, {COLORS['accent2']}); 
            color: white; padding: 15px; border-radius: 8px; text-align: center; 
            box-shadow: 0 3px 10px rgba(74, 144, 226, 0.4);">
                <h4 style="margin: 0; color: white; font-weight: 600;">Accuracy</h4>
                <h2 style="margin: 10px 0; color: white; font-weight: 700;">
                {feedback.accuracy_score}/10</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed feedback
        st.markdown(feedback.to_formatted_string())