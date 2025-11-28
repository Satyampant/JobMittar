
import base64
from typing import Dict, Any
from tools.executor import execute_tool
from models.interview import InterviewFeedback


class InterviewService:
    
    def __init__(self):
        pass
    
    def generate_question_audio(self, question_text: str, question_type: str = "Technical") -> bytes:
        result = execute_tool("generate_question_audio", {
            "question_text": question_text,
            "question_type": question_type
        })
        
        if not result["success"]:
            raise Exception(f"Audio generation failed: {result.get('error')}")
        
        return result["result"]
    
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        result = execute_tool("transcribe_candidate_response", {
            "audio_bytes": audio_b64
        })
        
        if not result["success"]:
            raise Exception(f"Transcription failed: {result.get('error')}")
        
        return result["result"]
    
    def generate_feedback(self, question: str, question_type: str,candidate_response: str) -> InterviewFeedback:

        result = execute_tool("generate_interview_feedback", {
            "question": question,
            "question_type": question_type,
            "candidate_response": candidate_response
        })
        
        if not result["success"]:
            return InterviewFeedback(
                evaluation=f"Unable to generate detailed feedback: {result.get('error')}",
                strengths=["Response was recorded"],
                weaknesses=["Feedback generation encountered an error"],
                suggestions=["Try answering again with more detail"],
                confidence_score=5.0,
                accuracy_score=5.0
            )
        
        return InterviewFeedback(**result["result"])
    
    def encode_audio_base64(self, audio_bytes: bytes) -> str:
        return base64.b64encode(audio_bytes).decode("utf-8")