"""Question card component - displays current question with audio."""

import streamlit as st
from typing import Dict, Any
from ui_utils import COLORS


class QuestionCard:
    """Renders current interview question with audio controls."""
    
    def render(
        self, 
        question: Dict[str, Any], 
        question_number: int, 
        total_questions: int,
        on_play_audio: callable
    ):
        """Render question card with audio playback."""
        question_text = question.get('question', 'Question not available')
        question_category = question.get('category', 'General')
        
        # Question card with gold accent
        st.markdown(f"""
        <div style="background-color: {COLORS['card_bg']}; border-radius: 10px; 
        padding: 20px; margin-bottom: 20px; border-left: 4px solid {COLORS['primary']}; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
            <h3 style="color: {COLORS['primary']}; margin-top: 0; font-weight: 600;">
            Question {question_number} of {total_questions}</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: {COLORS['text']};">
            {question_text}</p>
            <span style="background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}); 
            color: #1A1D23; padding: 6px 14px; border-radius: 15px; font-weight: bold; 
            box-shadow: 0 2px 6px rgba(255, 184, 28, 0.3);">
            {question_category}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Audio controls remain the same
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("### Audio Settings")
            volume = st.slider(
                "Volume", 0.0, 1.0, st.session_state.audio_volume, 0.1,
                key=f"volume_{question_number}"
            )
            st.session_state.audio_volume = volume
        
        with col2:
            st.markdown("### ")
            if st.button("🔊 Play Question", key=f"play_{question_number}"):
                on_play_audio(question_text, question_category, volume)
