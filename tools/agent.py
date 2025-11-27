"""Autonomous agent with tool-calling decision logic and interview orchestration."""

from typing import Dict, Any, List, Optional
import json
import os
from groq import Groq
from .definitions import TOOL_REGISTRY
from .executor import execute_tool, ToolExecutionError
from config import get_settings


class AutonomousAgent:
    """Agent that autonomously decides which tools to use, including interview tools."""
    
    def __init__(self, agent_type: str = "job_search"):
        """Initialize agent with specific type.
        
        Args:
            agent_type: Type of agent (job_search, match_analysis, interview_prep, interview)
        """
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)
        self.agent_type = agent_type
        self.model = settings.api.groq_model
        
        # Dynamically load all available tools from registry
        self.tools = [TOOL_REGISTRY[name] for name in TOOL_REGISTRY]
        
        # Load agent-specific prompt
        self.system_prompt = self._get_agent_prompt()
    
    def _get_agent_prompt(self) -> str:
        """Get agent-specific system prompt from configuration."""
        settings = get_settings()
        prompt_map = {
            "job_search": settings.prompts.job_search_agent,
            "match_analysis": settings.prompts.match_analysis_agent,
            "interview_prep": settings.prompts.interview_prep_agent,
            "interview": settings.prompts.interview_agent
        }
        return prompt_map.get(self.agent_type, settings.prompts.job_search_agent)
    
    def decide_and_execute(
        self, 
        user_request: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Let agent decide which tool to use and execute it.
        
        Args:
            user_request: User's request or query
            context: Additional context for decision making
            
        Returns:
            Execution result with success status and data
        """
        tool_call = self._decide_tool(user_request, context or {})
        if tool_call:
            try:
                return execute_tool(tool_call["tool"], tool_call["parameters"])
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No tool selected by agent"}
    
    def _decide_tool(self, request: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to decide which tool to call based on request and context.
        
        Args:
            request: User request text
            context: Context dictionary with relevant information
            
        Returns:
            Dictionary with tool name and parameters, or None
        """
        try:
            # Construct context-aware message
            context_str = json.dumps(context, indent=2) if context else "No additional context"
            user_message = f"Request: {request}\n\nContext:\n{context_str}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                tools=self.tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1000
            )
            
            # Extract tool call if present
            if response.choices[0].message.tool_calls:
                call = response.choices[0].message.tool_calls[0]
                return {
                    "tool": call.function.name,
                    "parameters": json.loads(call.function.arguments)
                }
            
            return None
            
        except Exception as e:
            print(f"Agent decision error: {str(e)}")
            return None
    
    def orchestrate_interview_session(
        self, 
        job_data: Dict[str, Any],
        question_count: int = 10
    ) -> Dict[str, Any]:
        """Orchestrate a complete interview session autonomously.
        
        This method demonstrates the agent's ability to chain multiple tools
        to accomplish a complex workflow.
        
        Args:
            job_data: Job information for interview context
            question_count: Number of questions to generate
            
        Returns:
            Complete interview session data
        """
        session_data = {
            "job": job_data,
            "questions": [],
            "status": "initialized"
        }
        
        # Step 1: Generate interview questions
        questions_result = self.decide_and_execute(
            f"Generate {question_count} interview questions for {job_data.get('title', 'this position')}",
            context={"job_data": job_data, "question_count": question_count}
        )
        
        if not questions_result.get("success"):
            return {"success": False, "error": "Failed to generate questions", "session": session_data}
        
        session_data["questions"] = questions_result.get("result", [])
        session_data["status"] = "questions_generated"
        
        return {"success": True, "session": session_data}
    
    def process_interview_response(
        self,
        question: str,
        question_type: str,
        audio_bytes: bytes
    ) -> Dict[str, Any]:
        """Process a candidate's interview response using multiple tools.
        
        Args:
            question: The interview question
            question_type: Type of question (Technical, Behavioral, etc.)
            audio_bytes: Audio response from candidate
            
        Returns:
            Complete processing result with transcription and feedback
        """
        import base64
        
        # Step 1: Transcribe audio
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        transcription_result = self.decide_and_execute(
            "Transcribe this candidate's interview response",
            context={"audio_bytes": audio_b64}
        )
        
        if not transcription_result.get("success"):
            return {"success": False, "error": "Transcription failed"}
        
        transcribed_text = transcription_result.get("result", "")
        
        # Step 2: Generate feedback
        feedback_result = self.decide_and_execute(
            "Analyze and provide feedback on this interview response",
            context={
                "question": question,
                "question_type": question_type,
                "candidate_response": transcribed_text
            }
        )
        
        if not feedback_result.get("success"):
            return {
                "success": True,
                "transcription": transcribed_text,
                "feedback": None,
                "warning": "Feedback generation failed"
            }
        
        return {
            "success": True,
            "transcription": transcribed_text,
            "feedback": feedback_result.get("result")
        }