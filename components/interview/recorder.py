"""Audio recorder component - captures candidate responses."""

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from ui_utils import COLORS


class ResponseRecorder:
    """Renders audio recorder for candidate responses."""
    
    def render(self, on_audio_recorded: callable):
        """Render recorder with instructions."""
        st.markdown("### 🎤 Your Response")
        st.markdown(f"""
        <div style="background-color: {COLORS['card_bg']}; padding: 15px; 
        border-radius: 8px; margin-bottom: 15px; border-left: 3px solid {COLORS['primary']};">
        <p style="color: {COLORS['text']};">Click <strong style="color: {COLORS['primary']}">
        Start Recording</strong> to begin your answer. 
        Click <strong style="color: {COLORS['primary']}">Stop Recording</strong> when you're done.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recorder (unchanged)
        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            key=st.session_state.recorder_key
        )
        
        if audio:
            st.audio(audio['bytes'])
            on_audio_recorded(audio['bytes'])