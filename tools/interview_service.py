"""Interview service for real-time speech interaction and AI feedback."""

import os
import tempfile
import base64
from typing import Dict, Any, Optional
from groq import Groq
from deepgram import DeepgramClient
from config import get_settings
from models.interview_session import InterviewFeedback
import instructor


class InterviewService:
    """Service for managing interview interactions with speech and AI feedback."""
    
    def __init__(self):
        self.settings = get_settings()
        self.groq_client = Groq(api_key=self.settings.groq_api_key)
        self.deepgram_api_key = self.settings.deepgram_api_key
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
        self.deepgram_client = DeepgramClient(api_key=self.deepgram_api_key)
        self.instructor_client = instructor.from_groq(
            self.groq_client, 
            mode=instructor.Mode.JSON
        )
    
    def generate_question_audio(
        self, 
        question_text: str, 
        question_type: str = "Technical"
    ) -> bytes:
        """Generate TTS audio for interview question using Groq.
        
        Args:
            question_text: The question to convert to speech
            question_type: Type of question (Technical, Behavioral, etc.)
            
        Returns:
            Audio bytes in MP3 format
        """
        voice = "Deedee-PlayAI"
        model = "playai-tts"
        response_format = "mp3"
        
        prompt = f"This is a {question_type} question: {question_text}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        try:
            response = self.groq_client.audio.speech.create(
                model=model,
                voice=voice,
                input=prompt,
                response_format=response_format
            )
            response.write_to_file(temp_path)
            
            with open(temp_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            return audio_bytes
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe audio response using Deepgram.
        
        Args:
            audio_bytes: Audio data in bytes
            
        Returns:
            Transcribed text
        """
        import requests
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile.write(audio_bytes)
            tmpfile_path = tmpfile.name
        
        try:
            # Use Deepgram REST API directly (works with all SDK versions)
            url = "https://api.deepgram.com/v1/listen"
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "audio/mpeg"
            }
            
            params = {
                "model": "nova-2",
                "smart_format": "true",
                "language": "en"
            }
            
            with open(tmpfile_path, "rb") as audio_file:
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    data=audio_file
                )
            
            if response.status_code != 200:
                raise Exception(f"Deepgram API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Extract transcript
            try:
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
            except (KeyError, IndexError) as e:
                raise Exception(f"Could not extract transcript from response: {str(e)}")
            
            if not transcript or not transcript.strip():
                return "No speech detected. Please try speaking louder and clearer."
            
            return transcript
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during transcription: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
        finally:
            if os.path.exists(tmpfile_path):
                try:
                    os.remove(tmpfile_path)
                except:
                    pass
    
    def generate_feedback(
        self, 
        question: str, 
        question_type: str,
        candidate_response: str
    ) -> InterviewFeedback:
        """Generate AI feedback for candidate's response using Instructor.
        
        Args:
            question: The interview question
            question_type: Type of question (Technical, Behavioral, etc.)
            candidate_response: Candidate's transcribed response
            
        Returns:
            Structured InterviewFeedback object
        """
        # Determine interviewer type
        interviewer_type_map = {
            'Technical': 'Technical Expert',
            'Behavioral': 'Manager or Team Lead',
            'Situational': 'Manager or Team Lead',
            'General': 'HR Recruiter'
        }
        interviewer_type = interviewer_type_map.get(question_type, 'HR Recruiter')
        
        prompt = f"""
You are an experienced {interviewer_type} interviewer assessing a candidate's answer.

**Question:** {question}
**Candidate Response:** {candidate_response}

⚠️ Important: Do not be biased in your evaluation. Focus only on the quality, clarity, and correctness of the response.

Your task:
1. Evaluate the overall quality of the response.
2. Highlight strengths and positive aspects (provide 2-3 specific strengths).
3. Identify specific weaknesses or missing points (provide 2-3 specific weaknesses).
4. Suggest clear, actionable improvements (provide 2-3 specific suggestions).
5. Provide a **Confidence Score** (0-10) for how confidently the response was delivered.
6. Provide an **Accuracy Score** (0-10) for how factually correct the response is.

Provide a structured evaluation with:
- evaluation: Overall assessment (50-200 characters)
- strengths: List of 2-3 specific strengths
- weaknesses: List of 2-3 specific weaknesses
- suggestions: List of 2-3 actionable improvements
- confidence_score: Score from 0-10
- accuracy_score: Score from 0-10
"""
        
        try:
            feedback = self.instructor_client.chat.completions.create(
                model=self.settings.api.groq_model,
                messages=[{"role": "user", "content": prompt}],
                response_model=InterviewFeedback,
                max_tokens=self.settings.api.max_tokens,
                temperature=0.5
            )
            return feedback
        except Exception as e:
            # Fallback feedback if parsing fails
            return InterviewFeedback(
                evaluation=f"Unable to generate detailed feedback: {str(e)}",
                strengths=["Response was recorded"],
                weaknesses=["Feedback generation encountered an error"],
                suggestions=["Try answering again with more detail"],
                confidence_score=5.0,
                accuracy_score=5.0
            )
    
    def encode_audio_base64(self, audio_bytes: bytes) -> str:
        """Encode audio bytes to base64 for HTML embedding.
        
        Args:
            audio_bytes: Audio data in bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(audio_bytes).decode("utf-8")