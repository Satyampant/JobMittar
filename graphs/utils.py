"""Graph utility functions for state management and serialization."""

from typing import Any, Dict, List
from datetime import datetime, date
from pydantic import BaseModel


def convert_pydantic_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to plain dict for state storage.
    
    Handles nested models and special types (datetime, date).
    Prevents Pydantic serialization issues in LangGraph state.
    
    Args:
        model: Pydantic model instance
        
    Returns:
        Plain dict representation
    """
    data = {}
    
    for field_name, field_value in model.model_dump().items():
        # Handle datetime/date objects
        if isinstance(field_value, (datetime, date)):
            data[field_name] = field_value.isoformat()
        
        # Handle list of Pydantic models (e.g., skills, education)
        elif isinstance(field_value, list):
            data[field_name] = [
                _convert_item(item) for item in field_value
            ]
        
        # Handle nested Pydantic models
        elif isinstance(field_value, BaseModel):
            data[field_name] = convert_pydantic_to_dict(field_value)
        
        # Plain values
        else:
            data[field_name] = field_value
    
    return data


def _convert_item(item: Any) -> Any:
    """Helper to convert list items."""
    if isinstance(item, BaseModel):
        return convert_pydantic_to_dict(item)
    elif isinstance(item, (datetime, date)):
        return item.isoformat()
    else:
        return item


def extract_contact_info(resume_dict: Dict[str, Any]) -> Dict[str, str]:
    """Extract contact info into standardized format.
    
    Args:
        resume_dict: Parsed resume dictionary
        
    Returns:
        Contact info dict with email and phone
    """
    return {
        "email": resume_dict.get("email", ""),
        "phone": resume_dict.get("phone", "")
    }


def format_skills_list(skills: List[Any]) -> List[str]:
    """Format skills from various formats to simple string list.
    
    Handles:
    - List of Skill objects (with name field)
    - List of dicts (with 'name' key)
    - List of strings
    
    Args:
        skills: Skills in various formats
        
    Returns:
        List of skill name strings
    """
    formatted = []
    
    for skill in skills:
        if isinstance(skill, dict):
            formatted.append(skill.get("name", str(skill)))
        elif isinstance(skill, str):
            formatted.append(skill)
        elif hasattr(skill, "name"):
            formatted.append(skill.name)
        else:
            formatted.append(str(skill))
    
    return formatted


def format_education_list(education: List[Any]) -> List[str]:
    """Format education entries to readable strings.
    
    Args:
        education: Education entries in various formats
        
    Returns:
        List of formatted education strings
    """
    formatted = []
    
    for edu in education:
        if isinstance(edu, dict):
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            formatted.append(f"{degree} from {institution}")
        elif isinstance(edu, str):
            formatted.append(edu)
        elif hasattr(edu, "degree") and hasattr(edu, "institution"):
            formatted.append(f"{edu.degree} from {edu.institution}")
        else:
            formatted.append(str(edu))
    
    return formatted


def format_experience_list(experience: List[Any]) -> List[str]:
    """Format work experience entries to readable strings.
    
    Args:
        experience: Experience entries in various formats
        
    Returns:
        List of formatted experience strings
    """
    formatted = []
    
    for exp in experience:
        if isinstance(exp, dict):
            position = exp.get("position", "")
            company = exp.get("company", "")
            description = exp.get("description", "")
            formatted.append(f"{position} at {company}: {description}")
        elif isinstance(exp, str):
            formatted.append(exp)
        elif hasattr(exp, "position") and hasattr(exp, "company"):
            desc = exp.description if hasattr(exp, "description") else ""
            formatted.append(f"{exp.position} at {exp.company}: {desc}")
        else:
            formatted.append(str(exp))
    
    return formatted