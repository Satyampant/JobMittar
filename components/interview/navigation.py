"""Navigation buttons component - question traversal."""

import streamlit as st
from models.interview import InterviewSessionState


class NavigationButtons:
    """Renders navigation controls for interview session."""
    
    def render(
        self, 
        session: InterviewSessionState,
        on_previous: callable,
        on_next: callable,
        on_finish: callable
    ):
        """Render previous/next/finish buttons."""
        if not session:
            return
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button(
                "⬅️ Previous Question",
                disabled=session.current_question_index == 0,
                key="prev_btn"
            ):
                on_previous()
        
        with col2:
            if st.button(
                "➡️ Next Question",
                disabled=session.current_question_index >= len(session.questions) - 1,
                key="next_btn"
            ):
                on_next()
        
        with col3:
            if st.button("✅ Finish Interview", key="finish_btn"):
                on_finish()