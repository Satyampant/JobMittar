"""Resume Analysis tab - LangGraph integrated version."""

import streamlit as st
import tempfile
import os
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from parsers.file_reader import read_resume_file
from ui_utils import (
    display_formatted_analysis,
    display_resume_analysis_summary,
    display_extracted_information,
    COLORS
)
from graphs.streamlit_adapter import (
    invoke_graph_sync,
    stream_to_streamlit,
    get_or_create_thread_id,
    display_state_summary
)


def render_resume_analysis_tab(graph):
    """Render Resume Analysis tab with LangGraph integration.
    
    Args:
        graph: Compiled master orchestration graph
    """
    st.header("Resume Analysis")

    col1, col2 = st.columns(2)

    with col1:
        _render_upload_section(graph)

    with col2:
        _render_tips_section()

    # Display results from graph state
    if st.session_state.get("resume_data"):
        _render_analysis_results()
    else:
        _render_empty_state()


def _render_upload_section(graph):
    """Render resume upload with graph processing."""
    st.subheader("Upload Resume")
    st.markdown(f"""
    <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <p style="margin-bottom: 10px;">Upload your resume in PDF, DOCX, or TXT format.</p>
    <p>LangGraph will orchestrate parsing → analysis → validation.</p>
    </div>
    """, unsafe_allow_html=True)

    resume_file = st.file_uploader(
        "Upload your resume", 
        type=["pdf", "txt", "docx"], 
        key="resume_uploader"
    )

    if resume_file is not None:
        _process_resume_with_graph(resume_file, graph)


def _process_resume_with_graph(resume_file, graph):
    """Process resume using LangGraph orchestration."""
    with st.spinner("🔄 Processing resume through LangGraph..."):
        try:
            # Extract text
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=f".{resume_file.name.split('.')[-1]}"
            ) as temp_file:
                temp_file.write(resume_file.getbuffer())
                temp_path = temp_file.name

            extracted_text = read_resume_file(temp_path)
            
            try:
                os.unlink(temp_path)
            except:
                pass

            if not extracted_text:
                st.error("Could not extract text from file.")
                return

            # Create initial state for graph
            thread_id = get_or_create_thread_id("resume")
            
            initial_state = {
                "resume_data": {"raw_text": extracted_text},
                "job_results": [],
                "current_step": "resume_upload",
                "messages": [HumanMessage(content="Process my resume")],
                "user_preferences": {"auto_job_search": False}  # Prevent auto job search
            }

            # USE INVOKE INSTEAD OF STREAM - THIS IS THE FIX
            final_state = invoke_graph_sync(graph, initial_state, thread_id)

            # Check for errors
            if final_state.get("error"):
                st.error(f"Processing failed: {final_state['error']}")
                return
            
            # Update session state
            if final_state.get("resume_data"):
                st.session_state.resume_data = final_state["resume_data"]
                st.success("✅ Resume analysis complete!")
                st.rerun()
            else:
                st.error("Resume processing completed but no data was extracted.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("If error persists, try a different file format.")

def _render_tips_section():
    """Render resume tips (unchanged)."""
    st.subheader("Resume Tips")
    st.markdown(f"""
    <div style="background-color: {COLORS["accent1"]}; color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: white;">Key Resume Components:</h4>
    <ul style="margin-bottom: 0;">
    <li><strong>Clear contact information</strong></li>
    <li><strong>Relevant skills section</strong></li>
    <li><strong>Quantified achievements</strong></li>
    <li><strong>ATS-friendly format</strong></li>
    <li><strong>Consistent formatting</strong></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def _render_analysis_results():
    """Display analysis results from session state."""
    st.markdown("---")

    resume_tabs = st.tabs(["Summary", "Skills & Experience", "Analysis", "Raw Text"])

    with resume_tabs[0]:
        display_resume_analysis_summary(st.session_state.resume_data)

    with resume_tabs[1]:
        display_extracted_information(st.session_state.resume_data)

    with resume_tabs[2]:
        if "analysis" in st.session_state.resume_data:
            display_formatted_analysis(st.session_state.resume_data["analysis"])
        else:
            st.info("No detailed analysis available.")

    with resume_tabs[3]:
        if "raw_text" in st.session_state.resume_data:
            st.text_area(
                "Extracted Text", 
                st.session_state.resume_data["raw_text"], 
                height=400, 
                disabled=True
            )


def _render_empty_state():
    """Render empty state."""
    st.markdown(f"""
    <div style="background-color: {COLORS["background"]}; padding: 20px; border-radius: 8px; 
    border: 1px dashed {COLORS["primary"]}; text-align: center; margin-top: 30px;">
    <h3 style="color: {COLORS["primary"]};">No Resume Uploaded</h3>
    <p>Upload your resume to begin LangGraph-powered analysis.</p>
    </div>
    """, unsafe_allow_html=True)