
import streamlit as st
import pandas as pd
from langchain_core.messages import HumanMessage

from ui_utils import format_job_description, COLORS
from utils.job_storage import save_job_to_local, load_saved_jobs
from graphs.streamlit_adapter import (
    invoke_graph_sync,
    stream_to_streamlit,
    get_or_create_thread_id,
    display_state_summary
)


COMMON_JOB_TITLES = [
    "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
    "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "DevOps Engineer", "Python Developer"
]

LOCATIONS = [
    "Remote", "New York, NY", "San Francisco, CA", "Seattle, WA",
    "Austin, TX", "Boston, MA", "Bangalore, India", "London, UK"
]


def render_job_search_tab(graph):
    
    st.header("Job Search")

    search_tabs = st.tabs(["📄 Resume-Based Search", "🔍 Custom Search"])

    with search_tabs[0]:
        _render_resume_based_search(graph)

    with search_tabs[1]:
        _render_custom_search(graph)

    if st.session_state.get("job_results"):
        _render_job_results(graph)


def _render_resume_based_search(graph):
    if st.session_state.get("resume_data"):
        st.subheader("Find Jobs Matching Your Resume")
        
        skills_preview = ", ".join(st.session_state.resume_data.get("skills", [])[:5])
        if skills_preview:
            st.markdown(f"""
            <div style="background-color: {COLORS["secondary"]}; color: white; 
            padding: 10px; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0;"><strong>Top Skills:</strong> {skills_preview}</p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            location = st.selectbox("Location:", LOCATIONS, index=0, key="resume_search_location")

        with col2:
            if st.button("Search Jobs", key="resume_based_search"):
                _execute_graph_job_search(graph, location=location, resume_based=True)
    else:
        st.warning("Please upload your resume first.")


def _render_custom_search(graph):
    with st.form("job_search_form"):
        st.subheader("Search Criteria")

        col1, col2 = st.columns(2)

        with col1:
            keywords = st.selectbox("Job Title:", COMMON_JOB_TITLES, key="job_titles")

        with col2:
            location = st.selectbox("Location:", LOCATIONS, key="locations")

        with st.expander("⚙️ Advanced Filters", expanded=False):
            job_count = st.slider("Number of jobs:", 3, 20, 5, key="job_count")

        submit_search = st.form_submit_button("Search Jobs")

    if submit_search:
        _execute_graph_job_search(graph, keywords=keywords, location=location, count=job_count)


def _execute_graph_job_search(graph, location="Remote", keywords=None, resume_based=False, count=10):
    with st.spinner("🔄 Searching jobs via LangGraph..."):
        try:
            if resume_based:
                skills = st.session_state.resume_data.get("skills", [])
                search_keywords = " ".join(skills[:3])
            else:
                search_keywords = keywords or "Software Engineer"

            thread_id = get_or_create_thread_id("job_search")
            
            state = {
                "resume_data": st.session_state.get("resume_data"),
                "job_query": {
                    "keywords": search_keywords,
                    "location": location,
                    "platform": "LinkedIn",
                    "count": count
                },
                "job_results": [],
                "current_step": "job_search",
                "messages": [HumanMessage(content=f"Find {search_keywords} jobs in {location}")]
            }

            final_state = None
            for state_update in stream_to_streamlit(graph, state, thread_id):
                final_state = state_update
                
                if state_update.get("job_results"):
                    st.session_state.job_results = state_update["job_results"]

            if final_state:
                display_state_summary(final_state)
                
                if final_state.get("error"):
                    st.error(f"Search failed: {final_state['error']}")
                else:
                    jobs_count = len(final_state.get("job_results", []))
                    st.success(f"✅ Found {jobs_count} jobs!")
                    st.rerun()

        except Exception as e:
            st.error(f"Search error: {str(e)}")


def _render_job_results(graph):
    st.subheader(f"Job Results ({len(st.session_state.job_results)})")

    job_df = pd.DataFrame([
        {
            "Title": job.get("title", "Unknown"),
            "Company": job.get("company", "Unknown"),
            "Location": "Remote"
        }
        for job in st.session_state.job_results
    ])

    st.dataframe(job_df, use_container_width=True, hide_index=True)

    if st.session_state.job_results:
        _render_job_details(graph)


def _render_job_details(graph):
    """Render selected job with graph-powered analysis."""
    st.markdown("### Job Details")
    
    selected_index = st.selectbox(
        "Select a job to view details:",
        range(len(st.session_state.job_results)),
        format_func=lambda i: f"{st.session_state.job_results[i].get('title', 'Unknown')} at {st.session_state.job_results[i].get('company', 'Unknown')}",
        key="job_selection"
    )

    if selected_index is not None:
        selected_job = st.session_state.job_results[selected_index]
        st.session_state.selected_job = selected_job

        # Job header
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h3 style='color: white; margin: 0;'>{selected_job.get('title', 'Unknown')}</h3>
            <p style='color: white; margin: 0.5rem 0 0 0;'>{selected_job.get('company', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)

        if selected_job.get('description'):
            st.subheader("Job Description")
            st.markdown(format_job_description(selected_job['description']), unsafe_allow_html=True)

        if st.session_state.get("resume_data"):
            _render_match_analysis_via_graph(selected_job, graph)

        _render_job_actions(selected_job)


def _render_match_analysis_via_graph(job, graph):
    """Execute match analysis through graph."""
    with st.expander("📊 Resume Match Analysis", expanded=True):
        if st.button("Analyze Match", key="analyze_match_btn"):
            with st.spinner("🔄 Analyzing via LangGraph..."):
                try:
                    thread_id = get_or_create_thread_id("match_analysis")
                    
                    state = {
                        "resume_data": st.session_state.resume_data,
                        "selected_job": job,
                        "current_step": "match_analysis",
                        "messages": [HumanMessage(content="Analyze resume-job match")]
                    }

                    result_state = invoke_graph_sync(graph, state, thread_id)
                    
                    if result_state.get("match_analysis"):
                        match_data = result_state["match_analysis"]
                        match_score = match_data.get("match_score", 0)

                        st.markdown(f"""
                        <div style="text-align: center; margin: 20px 0;">
                            <div style="background-color: {COLORS["primary"]}; display: inline-block; 
                            padding: 10px 20px; border-radius: 20px;">
                                <span style="color: white; font-size: 1.5rem; font-weight: bold;">
                                Match Score: {match_score}%</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        for match in match_data.get("key_matches", []):
                            st.success(f"✅ {match}")
                        for gap in match_data.get("gaps", []):
                            st.warning(f"⚠️ {gap}")

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")


def _render_job_actions(job):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Job", key="save_job_btn"):
            save_job_to_local(job)
            st.session_state.saved_jobs = load_saved_jobs()
            st.success("Job saved!")
    
    with col2:
        if st.button("Prepare for Interview", key="prepare_interview_btn"):
            st.session_state.active_tab = 2
            st.rerun()