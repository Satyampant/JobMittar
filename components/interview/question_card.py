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
        
        # Question card
        st.markdown(f"""
        <div style="background-color: #111111; border-radius: 10px; padding: 20px; 
        margin-bottom: 20px; border-left: 4px solid {COLORS['accent3']};">
            <h3 style="color: {COLORS['primary']}; margin-top: 0;">
            Question {question_number} of {total_questions}</h3>
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
            volume = st.slider(
                "Volume", 0.0, 1.0, st.session_state.audio_volume, 0.1,
                key=f"volume_{question_number}"
            )
            st.session_state.audio_volume = volume
        
        with col2:
            st.markdown("### ")
            if st.button("🔊 Play Question", key=f"play_{question_number}"):
                on_play_audio(question_text, question_category, volume)