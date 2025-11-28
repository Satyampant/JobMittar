"""Interview Preparation tab - LangGraph integrated with checkpointing."""

import streamlit as st
from datetime import datetime

from ui_utils import apply_styling, COLORS

# Import graph compilation
from graphs.compiled_graphs_sync import compile_master_graph_sync

# Import refactored tab renderers with graph support
from ui.tabs.resume_analysis_refactored import render_resume_analysis_tab
from ui.tabs.job_search_refactored import render_job_search_tab
from ui.tabs.interview_prep_refactored import render_interview_prep_tab
from ui.tabs.saved_jobs import render_saved_jobs_tab

# Load and compile graph once at startup
@st.cache_resource
def get_compiled_graph():
    """Compile graph once and cache it."""
    return compile_master_graph_sync()

# Set page configuration
st.set_page_config(
    page_title="Professional Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_styling()

# Application header
st.markdown(f"""
<div style='text-align:center; padding: 1.5rem 0; 
background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}, {COLORS["tertiary"]}); 
border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
    <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
    Professional Job Search Assistant</h1>
    <p style='color: white; font-size: 1.2rem; font-weight: 500; margin: 0.5rem 2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    LangGraph-powered orchestration</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Persistent checkpoints</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Intelligent routing</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "job_results" not in st.session_state:
    st.session_state.job_results = []
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None
if "saved_jobs" not in st.session_state:
    from utils.job_storage import load_saved_jobs
    st.session_state.saved_jobs = load_saved_jobs()

# Compile graph (cached)
graph = get_compiled_graph()

# Create main navigation tabs
tabs = st.tabs([
    "📄 Resume Analysis", 
    "🔍 Job Search", 
    "🎯 Interview Preparation", 
    "💼 Saved Jobs"
])

# Tab 1: Resume Analysis (with graph)
with tabs[0]:
    render_resume_analysis_tab(graph)

# Tab 2: Job Search (with graph)
with tabs[1]:
    render_job_search_tab(graph)

# Tab 3: Interview Preparation (with graph)
with tabs[2]:
    render_interview_prep_tab(graph)
        
# Tab 4: Saved Jobs (no graph needed)
with tabs[3]:
    render_saved_jobs_tab()

# Footer
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
    color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
    JobMittar v2.0 - LangGraph Edition | Built with Streamlit | © {datetime.now().year}</p>
    </div>""",
    unsafe_allow_html=True
)