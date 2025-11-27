"""Resume processing nodes for LangGraph workflow.
These nodes handle the resume upload → parse → analyze → validate pipeline.
"""

from typing import Dict, Any
from graphs.state import JobMittrState
from parsers.resume_extractor import extract_resume
from tools.executor import execute_tool
from models.resume import Resume


def parse_resume_node(state: JobMittrState) -> JobMittrState:
    """Parse raw resume text into structured Resume model.
    Expects state["resume_data"]["raw_text"] to be set.
    Updates state["resume_data"] with parsed fields.
    Args:
        state: Current workflow state with raw_text   
    Returns:
        Updated state with parsed resume data
    """
    raw_text = state.get("resume_data", {}).get("raw_text", "")
    
    if not raw_text:
        return {
            **state,
            "error": "No resume text provided for parsing",
            "current_step": "resume_upload"
        }
    
    try:
        # Using existing resume extractor (returns Pydantic Resume model)
        resume: Resume = extract_resume(raw_text)
        
        # Convert to dict for state storage (avoid Pydantic serialization issues)
        from graphs.utils import convert_pydantic_to_dict
        resume_dict = convert_pydantic_to_dict(resume)
        
        # Preserve raw_text
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
    """Generate AI-powered quality analysis of parsed resume.
    Expects state["resume_data"] to contain parsed fields.
    Adds analysis to state["resume_data"]["analysis"].
    Args:
        state: Current workflow state with parsed resume
    Returns:
        Updated state with resume analysis
    """
    resume_data = state.get("resume_data", {})
    
    if not resume_data or "name" not in resume_data:
        return {
            **state,
            "error": "Resume data not available for analysis",
            "current_step": "resume_upload"
        }
    
    try:
        # Call existing analysis tool
        result = execute_tool("analyze_resume_quality", {
            "resume_data": resume_data
        })
        
        if result.get("success"):
            # Add analysis to resume data
            resume_data["analysis"] = result["result"]
            
            return {
                **state,
                "resume_data": resume_data,
                "current_step": "resume_analysis",
                "error": None
            }
        else:
            # Analysis failed but resume is still usable
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
                "error": None  # Don't block workflow
            }
    
    except Exception as e:
        # Fallback analysis on error
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
            "error": None  # Don't block workflow
        }


def validate_resume_node(state: JobMittrState) -> JobMittrState:
    """Validate resume has required fields for downstream operations.
    Checks for: name, email, skills (at least 1).
    Sets error state if validation fails.
    Args:
        state: Current workflow state with parsed resume
    Returns:
        Updated state with validation status
    """
    resume_data = state.get("resume_data", {})
    
    # Check required fields
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
    
    # Validation passed
    return {
        **state,
        "current_step": "job_search",  # Ready for next stage
        "error": None
    }