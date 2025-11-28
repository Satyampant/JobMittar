
from typing import Any, Dict, List
from datetime import datetime, date
from pydantic import BaseModel


def convert_pydantic_to_dict(model: BaseModel) -> Dict[str, Any]:
    data = {}
    
    for field_name, field_value in model.model_dump().items():
        if isinstance(field_value, (datetime, date)):
            data[field_name] = field_value.isoformat()
        
        elif isinstance(field_value, list):
            data[field_name] = [
                _convert_item(item) for item in field_value
            ]
        
        elif isinstance(field_value, BaseModel):
            data[field_name] = convert_pydantic_to_dict(field_value)
        
        else:
            data[field_name] = field_value
    
    return data


def _convert_item(item: Any) -> Any:
    if isinstance(item, BaseModel):
        return convert_pydantic_to_dict(item)
    elif isinstance(item, (datetime, date)):
        return item.isoformat()
    else:
        return item


def extract_contact_info(resume_dict: Dict[str, Any]) -> Dict[str, str]:
    return {
        "email": resume_dict.get("email", ""),
        "phone": resume_dict.get("phone", "")
    }


def format_skills_list(skills: List[Any]) -> List[str]:
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