"""Resume Analysis tab handler."""

import streamlit as st
import tempfile
import os
from typing import Dict, Any

from parsers.file_reader import read_resume_file
from parsers.resume_extractor import extract_resume
from models.resume import Resume
from ui_utils import (
    display_formatted_analysis,
    display_resume_analysis_summary,
    display_extracted_information,
    COLORS
)


def render_resume_analysis_tab():
    """Render the Resume Analysis tab."""
    st.header("Resume Analysis")

    # Create two columns for upload options
    col1, col2 = st.columns(2)

    with col1:
        _render_upload_section()

    with col2:
        _render_tips_section()

    # Display resume analysis results
    if st.session_state.get("resume_data"):
        _render_analysis_results()
    else:
        _render_empty_state()


def _render_upload_section():
    """Render resume upload section."""
    st.subheader("Upload Resume")
    st.markdown(f"""
    <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <p style="margin-bottom: 10px;">Upload your resume in PDF, DOCX, or TXT format.</p>
    <p>We'll analyze your resume and extract key information to help you find matching jobs.</p>
    </div>
    """, unsafe_allow_html=True)

    # Resume file uploader
    resume_file = st.file_uploader(
        "Upload your resume", 
        type=["pdf", "txt", "docx"], 
        key="resume_uploader"
    )

    if resume_file is not None:
        _process_resume_file(resume_file)


def _process_resume_file(resume_file):
    """Process uploaded resume file."""
    with st.spinner("Analyzing your resume..."):
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=f".{resume_file.name.split('.')[-1]}"
            ) as temp_file:
                temp_file.write(resume_file.getbuffer())
                temp_path = temp_file.name

            # Read file using backend file reader
            extracted_text = read_resume_file(temp_path)

            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

            if extracted_text:
                # Parse resume using Pydantic-based extractor
                resume: Resume = extract_resume(extracted_text)

                # Convert Pydantic model to dict for session state
                resume_dict = {
                    "name": resume.name,
                    "email": resume.email,
                    "phone": resume.phone,
                    "summary": resume.summary,
                    "skills": [skill.name for skill in resume.skills],
                    "education": [f"{edu.degree} from {edu.institution}" for edu in resume.education],
                    "experience": [f"{exp.position} at {exp.company}: {exp.description}" for exp in resume.experience],
                    "raw_text": extracted_text,
                    "contact_info": {"email": resume.email, "phone": resume.phone or ""}
                }

                # Generate analysis
                analysis = _generate_resume_analysis(resume)
                resume_dict["analysis"] = analysis

                # Store in session state
                st.session_state.resume_data = resume_dict

                st.success("Resume analysis complete! Review the extracted information and analysis below.")
            else:
                st.error("Could not extract text from the uploaded file.")

        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")
            st.info("If the error persists, try uploading a different file format.")


def _generate_resume_analysis(resume: Resume) -> Dict[str, Any]:
    """Generate AI-powered analysis from resume data using backend tool."""
    from tools.executor import execute_tool
    
    # Convert Resume model to dict for tool execution
    resume_dict = {
        "name": resume.name,
        "email": resume.email,
        "phone": resume.phone,
        "summary": resume.summary,
        "skills": [skill.name for skill in resume.skills],
        "education": [f"{edu.degree} from {edu.institution}" for edu in resume.education],
        "experience": [f"{exp.position} at {exp.company}: {exp.description}" for exp in resume.experience]
    }
    
    result = execute_tool("analyze_resume_quality", {"resume_data": resume_dict})
    
    if result.get("success"):
        return result["result"]
    else:
        # Fallback analysis if tool fails
        return {
            "overall_assessment": "Unable to generate detailed analysis at this time.",
            "strengths": ["Resume uploaded successfully"],
            "weaknesses": ["Analysis unavailable"],
            "content_improvements": ["Try uploading again"],
            "format_suggestions": ["Ensure resume is in a supported format"],
            "ats_optimization": ["Use standard section headings"]
        }


def _render_tips_section():
    """Render resume tips section."""
    st.subheader("Resume Tips")
    st.markdown(f"""
    <div style="background-color: {COLORS["accent1"]}; color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: white;">Key Resume Components:</h4>
    <ul style="margin-bottom: 0;">
    <li><strong>Clear contact information</strong> - Make it easy for employers to reach you</li>
    <li><strong>Relevant skills section</strong> - Highlight technical and soft skills</li>
    <li><strong>Quantified achievements</strong> - Use numbers to demonstrate impact</li>
    <li><strong>ATS-friendly format</strong> - Use standard headings and keywords</li>
    <li><strong>Consistent formatting</strong> - Maintain professional appearance</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # ATS optimization tips
    st.markdown(f"""
    <div style="background-color: {COLORS["secondary"]}; color: white; padding: 15px; border-radius: 8px; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: white;">ATS Optimization Tips:</h4>
    <ul style="margin-bottom: 0;">
    <li>Use keywords from the job description</li>
    <li>Avoid tables, headers/footers, and images</li>
    <li>Use standard section headings</li>
    <li>Submit in PDF format when possible</li>
    <li>Keep formatting simple and clean</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def _render_analysis_results():
    """Display resume analysis results."""
    st.markdown("---")

    # Create tabs for different views
    resume_tabs = st.tabs(["Summary", "Skills & Experience", "Analysis", "Raw Text"])

    with resume_tabs[0]:
        display_resume_analysis_summary(st.session_state.resume_data)

    with resume_tabs[1]:
        display_extracted_information(st.session_state.resume_data)

    with resume_tabs[2]:
        if "analysis" in st.session_state.resume_data:
            display_formatted_analysis(st.session_state.resume_data["analysis"])
        else:
            st.info("No detailed analysis available. Please re-upload your resume.")

    with resume_tabs[3]:
        if "raw_text" in st.session_state.resume_data:
            st.text_area(
                "Extracted Text", 
                st.session_state.resume_data["raw_text"], 
                height=400, 
                disabled=True
            )
        else:
            st.info("Raw text not available.")


def _render_empty_state():
    """Render empty state when no resume is uploaded."""
    st.markdown(f"""
    <div style="background-color: {COLORS["background"]}; padding: 20px; border-radius: 8px; 
    border: 1px dashed {COLORS["primary"]}; text-align: center; margin-top: 30px;">
    <img src="https://img.icons8.com/fluency/96/000000/resume.png" 
    style="width: 64px; height: 64px; margin-bottom: 15px;">
    <h3 style="color: {COLORS["primary"]};">No Resume Uploaded</h3>
    <p>Upload your resume using the file uploader above to see the analysis.</p>
    </div>
    """, unsafe_allow_html=True)