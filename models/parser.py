"""Instructor-based LLM output parser for structured data extraction."""

import instructor
from groq import Groq
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class LLMParser:
    """Parse LLM outputs into validated Pydantic models using Instructor."""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = instructor.from_groq(Groq(api_key=api_key), mode=instructor.Mode.JSON)
        self.model = model
    
    def parse(self, prompt: str, response_model: Type[T], context: str = "") -> T:
        """Extract structured data from LLM response."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        return self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}],
            response_model=response_model
        )
