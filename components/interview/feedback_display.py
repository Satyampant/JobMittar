"""Feedback display component - shows AI evaluation."""

import streamlit as st
from models.interview import InterviewFeedback
from ui_utils import COLORS


class FeedbackDisplay:
    """Renders AI feedback for candidate responses."""
    
    def render(self, feedback: InterviewFeedback):
        """Display structured feedback with scores."""
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