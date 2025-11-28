import streamlit as st
import pandas as pd
import os
import json
import tempfile
import asyncio
from datetime import datetime, timedelta
from typing import Optional

# Create necessary directories
os.makedirs("saved_jobs", exist_ok=True)
os.makedirs("saved_interviews", exist_ok=True)

# Import new backend components
from parsers.file_reader import read_resume_file
from parsers.resume_extractor import extract_resume
from tools.executor import execute_tool
from models.resume import Resume
from models.job import Job
from models.interview import Interview, InterviewQuestion, InterviewSessionState
from config import get_settings

# Import UI utilities
from ui_utils import (
    display_formatted_analysis,
    display_resume_analysis_summary,
    display_extracted_information,
    format_job_description,
    # display_matching_skills,
    apply_styling,
    COLORS
)

# Import job storage utilities
from utils.job_storage import (
    save_job_to_local,
    load_saved_jobs,
    remove_saved_job
)

from ui.tabs import (
    render_resume_analysis_tab,
    render_job_search_tab,
    render_interview_prep_tab,
    render_saved_jobs_tab
)

# Load settings
settings = get_settings()

# Set page configuration
st.set_page_config(
    page_title="Professional Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling 
apply_styling()

# Application header with gradient 
st.markdown(f"""
<div style='text-align:center; padding: 2rem 0; 
background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]}, {COLORS["accent2"]}); 
border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 6px 20px rgba(255, 184, 28, 0.4);'>
    <h1 style='color: #1A1D23; font-size: 2.8rem; margin-bottom: 0.5rem; 
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1); font-weight: 700;'>
    💼 A Smarter Way to Get Hired</h1>
    <h5 style='color: #1A1D23; font-size: 1.2rem; margin-bottom: 0.5rem;'>
    Analyze your resume, find the right roles, and practice interviews — all in one place.</h5>
    <p style='color: #1A1D23; font-size: 1.2rem; font-weight: 600; margin: 0.5rem 2rem; 
    text-shadow: 1px 1px 2px rgba(0,0,0,0.05);'>
    <span style='background-color: rgba(0,0,0,0.1); padding: 6px 14px; border-radius: 20px; margin: 0 5px;'>
    🚀 Targeted Job Discovery</span> 
    <span style='background-color: rgba(0,0,0,0.1); padding: 6px 14px; border-radius: 20px; margin: 0 5px;'>
    📝 Resume Power-Up</span> 
    <span style='background-color: rgba(0,0,0,0.1); padding: 6px 14px; border-radius: 20px; margin: 0 5px;'>
    🎙️ Interview preparation</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {}
if "job_results" not in st.session_state:
    st.session_state.job_results = []
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = load_saved_jobs()

# Create main navigation tabs
tabs = st.tabs([
    "📄 Resume Analysis", 
    "🔍 Job Search", 
    "🎯 Interview Preparation", 
    "💼 Saved Jobs"
])

# Tab 1: Resume Analysis
with tabs[0]:
    render_resume_analysis_tab()

# Tab 2: Job Search 
with tabs[1]:
    render_job_search_tab()

# Tab 3: Interview Preparation 
with tabs[2]:
    render_interview_prep_tab()
        
# Tab 4: Saved Jobs
with tabs[3]:
    render_saved_jobs_tab()

# Footer
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
    color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Professional Job Search Assistant | Built with Streamlit | © {datetime.now().year}</p>
    </div>""",
    unsafe_allow_html=True
)
