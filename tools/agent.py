"""Autonomous agent with tool-calling decision logic."""

from typing import Dict, Any, List
import json
import os
from groq import Groq
from .definitions import TOOL_REGISTRY
from .executor import execute_tool, ToolExecutionError
from .prompts import AGENT_PROMPTS

class AutonomousAgent:
    """Agent that autonomously decides which tools to use."""
    
    def __init__(self, agent_type: str = "job_search"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.agent_type = agent_type
        self.tools = [TOOL_REGISTRY[name] for name in TOOL_REGISTRY]
    
    def decide_and_execute(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Let agent decide which tool to use and execute it."""
        tool_call = self._decide_tool(user_request, context or {})
        if tool_call:
            return execute_tool(tool_call["tool"], tool_call["parameters"])
        return {"success": False, "error": "No tool selected"}
    
    def _decide_tool(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to decide which tool to call."""
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": AGENT_PROMPTS[self.agent_type]},
                {"role": "user", "content": f"Request: {request}\nContext: {json.dumps(context)}"}
            ],
            tools=self.tools,
            tool_choice="auto",
            temperature=0.1
        )
        
        if response.choices[0].message.tool_calls:
            call = response.choices[0].message.tool_calls[0]
            return {"tool": call.function.name, "parameters": json.loads(call.function.arguments)}
        return None
