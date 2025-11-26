"""Interview service facade wrapping tool execution for convenience."""

import base64
from typing import Dict, Any
from tools.executor import execute_tool
from models.interview import InterviewFeedback


class InterviewService:
    """Facade for interview-related tools - provides convenience API."""
    
    def __init__(self):
        """Initialize service - tools are executed via executor."""
        pass
    
    def generate_question_audio(
        self, 
        question_text: str, 
        question_type: str = "Technical"
    ) -> bytes:
        """Generate TTS audio for interview question.
        
        Args:
            question_text: The question to convert to speech
            question_type: Type of question (Technical, Behavioral, etc.)
            
        Returns:
            Audio bytes in MP3 format
        """
        result = execute_tool("generate_question_audio", {
            "question_text": question_text,
            "question_type": question_type
        })
        
        if not result["success"]:
            raise Exception(f"Audio generation failed: {result.get('error')}")
        
        return result["result"]
    
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe audio response using Deepgram.
        
        Args:
            audio_bytes: Audio data in bytes
            
        Returns:
            Transcribed text
        """
        # Encode audio as base64 for tool parameter
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        result = execute_tool("transcribe_candidate_response", {
            "audio_bytes": audio_b64
        })
        
        if not result["success"]:
            raise Exception(f"Transcription failed: {result.get('error')}")
        
        return result["result"]
    
    def generate_feedback(
        self, 
        question: str, 
        question_type: str,
        candidate_response: str
    ) -> InterviewFeedback:
        """Generate AI feedback for candidate's response.
        
        Args:
            question: The interview question
            question_type: Type of question (Technical, Behavioral, etc.)
            candidate_response: Candidate's transcribed response
            
        Returns:
            Structured InterviewFeedback object
        """
        result = execute_tool("generate_interview_feedback", {
            "question": question,
            "question_type": question_type,
            "candidate_response": candidate_response
        })
        
        if not result["success"]:
            # Return fallback feedback
            return InterviewFeedback(
                evaluation=f"Unable to generate detailed feedback: {result.get('error')}",
                strengths=["Response was recorded"],
                weaknesses=["Feedback generation encountered an error"],
                suggestions=["Try answering again with more detail"],
                confidence_score=5.0,
                accuracy_score=5.0
            )
        
        # Convert dict result to InterviewFeedback object
        return InterviewFeedback(**result["result"])
    
    def encode_audio_base64(self, audio_bytes: bytes) -> str:
        """Encode audio bytes to base64 for HTML embedding.
        
        Args:
            audio_bytes: Audio data in bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(audio_bytes).decode("utf-8")