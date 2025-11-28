
from typing import Dict, Any
from graphs.state import JobMittrState
from parsers.resume_extractor import extract_resume
from tools.executor import execute_tool
from models.resume import Resume


def parse_resume_node(state: JobMittrState) -> JobMittrState:
    raw_text = state.get("resume_data", {}).get("raw_text", "")
    
    if not raw_text:
        return {
            **state,
            "error": "No resume text provided for parsing",
            "current_step": "resume_upload"
        }
    
    try:
        resume: Resume = extract_resume(raw_text)
        
        from graphs.utils import convert_pydantic_to_dict
        resume_dict = convert_pydantic_to_dict(resume)
        
        resume_dict["raw_text"] = raw_text
        
        return {
            **state,
            "resume_data": resume_dict,
            "current_step": "resume_analysis",
            "error": None
        }
    
    except Exception as e:
        return {
            **state,
            "error": f"Resume parsing failed: {str(e)}",
            "current_step": "resume_upload"
        }


def analyze_resume_node(state: JobMittrState) -> JobMittrState:
    resume_data = state.get("resume_data", {})
    
    if not resume_data or "name" not in resume_data:
        return {
            **state,
            "error": "Resume data not available for analysis",
            "current_step": "resume_upload"
        }
    
    try:
        result = execute_tool("analyze_resume_quality", {
            "resume_data": resume_data
        })
        
        if result.get("success"):
            resume_data["analysis"] = result["result"]
            
            return {
                **state,
                "resume_data": resume_data,
                "current_step": "resume_analysis",
                "error": None
            }
        else:
            resume_data["analysis"] = {
                "overall_assessment": "Analysis unavailable",
                "strengths": ["Resume parsed successfully"],
                "weaknesses": ["Could not generate detailed analysis"],
                "content_improvements": [],
                "format_suggestions": [],
                "ats_optimization": []
            }
            
            return {
                **state,
                "resume_data": resume_data,
                "current_step": "resume_analysis",
                "error": None 
            }
    
    except Exception as e:
        resume_data["analysis"] = {
            "overall_assessment": f"Analysis error: {str(e)}",
            "strengths": ["Resume data extracted"],
            "weaknesses": ["Analysis tool unavailable"],
            "content_improvements": [],
            "format_suggestions": [],
            "ats_optimization": []
        }
        
        return {
            **state,
            "resume_data": resume_data,
            "current_step": "resume_analysis",
            "error": None  
        }


def validate_resume_node(state: JobMittrState) -> JobMittrState:
    resume_data = state.get("resume_data", {})
    
    missing_fields = []
    
    if not resume_data.get("name"):
        missing_fields.append("name")
    
    if not resume_data.get("email"):
        missing_fields.append("email")
    
    if not resume_data.get("skills") or len(resume_data.get("skills", [])) == 0:
        missing_fields.append("skills (at least 1 skill required)")
    
    if missing_fields:
        return {
            **state,
            "error": f"Resume validation failed. Missing: {', '.join(missing_fields)}",
            "current_step": "resume_upload"
        }
    
    return {
        **state,
        "current_step": "job_search", 
        "error": None
    }