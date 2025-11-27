"""Job Search tab handler."""

import streamlit as st
import pandas as pd

from tools.executor import execute_tool
from ui_utils import format_job_description, COLORS
from utils.job_storage import save_job_to_local, load_saved_jobs


# Common job titles and locations
COMMON_JOB_TITLES = [
    "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
    "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "DevOps Engineer", "UX Designer", "AI Engineer",
    "Cloud Architect", "Database Administrator", "Project Manager", "Business Analyst",
    "Java Developer", "Python Developer", "React Developer", "Android Developer",
    "iOS Developer", "Node.js Developer", "Data Engineer", "Blockchain Developer",
    "Cybersecurity Analyst", "Quality Assurance Engineer"
]

LOCATIONS = [
    "Remote",
    "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
    "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Atlanta, GA", "Denver, CO",
    "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Delhi, India",
    "Pune, India", "Chennai, India", "London, UK", "Berlin, Germany", "Toronto, Canada"
]


def render_job_search_tab():
    """Render the Job Search tab."""
    st.header("Job Search")

    # Search tabs
    search_tabs = st.tabs(["📄 Resume-Based Search", "🔍 Custom Search"])

    with search_tabs[0]:
        _render_resume_based_search()

    with search_tabs[1]:
        _render_custom_search()

    # Display job results
    if st.session_state.get("job_results"):
        _render_job_results()


def _render_resume_based_search():
    """Render resume-based search section."""
    if st.session_state.get("resume_data"):
        st.subheader("Find Jobs Matching Your Resume")
        
        skills_preview = ", ".join(st.session_state.resume_data.get("skills", [])[:5])
        if skills_preview:
            st.markdown(f"""
            <div style="background-color: {COLORS["secondary"]}; color: white; 
            padding: 10px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
            <span style="font-weight: bold;">Top Skills:</span> {skills_preview}</p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            location = st.selectbox("Location:", LOCATIONS, index=0, key="resume_search_location")

        with col2:
            search_button = st.button("Search Jobs", key="resume_based_search")

        if search_button:
            _execute_resume_based_search(location)
    else:
        st.warning("Please upload your resume in the Resume Analysis tab first.")


def _execute_resume_based_search(location: str):
    """Execute resume-based job search."""
    with st.spinner("Searching for jobs..."):
        try:
            # Extract keywords from resume
            skills = st.session_state.resume_data.get("skills", [])
            search_keywords = " ".join(skills[:3])  # Use top 3 skills

            # Use backend tool executor
            result = execute_tool("search_jobs", {
                "keywords": search_keywords,
                "location": location,
                "platform": "LinkedIn",
                "count": 10
            })

            if result["success"]:
                jobs = result["result"]
                st.session_state.job_results = jobs
                st.success(f"Found {len(jobs)} jobs matching your resume!")
                st.rerun()
            else:
                st.error(f"Job search failed: {result.get('error', 'Unknown error')}. Try for some other location.")

        except Exception as e:
            st.error(f"Error searching for jobs: {str(e)}")


def _render_custom_search():
    """Render custom job search section."""
    with st.form("job_search_form"):
        st.subheader("Search Criteria")

        col1, col2 = st.columns(2)

        with col1:
            keywords = st.selectbox("Job Title:", COMMON_JOB_TITLES, key="job_titles")

        with col2:
            location = st.selectbox("Location:", LOCATIONS, key="locations")

        # Advanced filters
        with st.expander("⚙️ Advanced Filters", expanded=False):
            selected_platforms = st.multiselect(
                "Job Platforms:",
                options=["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "Monster"],
                default=["LinkedIn", "Indeed"],
                key="platforms"
            )

            job_count = st.slider("Jobs per platform:", 3, 20, 5, key="job_count")

        submit_search = st.form_submit_button("Search Jobs")

    if submit_search:
        _execute_custom_search(keywords, location, selected_platforms, job_count)


def _execute_custom_search(keywords: str, location: str, platforms: list, job_count: int):
    """Execute custom job search across platforms."""
    with st.spinner(f"Searching for {keywords} jobs in {location}..."):
        all_jobs = []
        for platform in platforms:
            try:
                result = execute_tool("search_jobs", {
                    "keywords": keywords,
                    "location": location,
                    "platform": platform,
                    "count": job_count
                })

                if result["success"]:
                    all_jobs.extend(result["result"])
            except Exception as e:
                st.error(f"Error searching {platform}: {str(e)}")

        st.session_state.job_results = all_jobs
        if all_jobs:
            st.success(f"Found {len(all_jobs)} jobs!")


def _render_job_results():
    """Display job search results."""
    st.subheader(f"Job Results ({len(st.session_state.job_results)})")

    # Create dataframe for display
    job_df = pd.DataFrame([
        {
            "Title": job.get("title", "Unknown"),
            "Company": job.get("company", "Unknown"),
            "Location": "Remote",
            "Platform": "LinkedIn"
        }
        for job in st.session_state.job_results
    ])

    st.dataframe(job_df, use_container_width=True, hide_index=True)

    # Job selection and details
    if st.session_state.job_results:
        _render_job_details()


def _render_job_details():
    """Render selected job details."""
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
        padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.2);'>
            <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
            {selected_job.get('title', 'Unknown')}</h3>
            <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
            {selected_job.get('company', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Job description
        if selected_job.get('description'):
            st.subheader("Job Description")
            st.markdown(format_job_description(selected_job['description']), unsafe_allow_html=True)

        # Match analysis
        if st.session_state.get("resume_data"):
            _render_match_analysis(selected_job)

        # Job actions
        _render_job_actions(selected_job)


def _render_match_analysis(job):
    """Render resume-job match analysis."""
    with st.expander("📊 Resume Match Analysis", expanded=True):
        with st.spinner("Analyzing match..."):
            try:
                result = execute_tool("analyze_job_match", {
                    "resume_data": st.session_state.resume_data,
                    "job_data": job
                })

                if result["success"]:
                    match_data = result["result"]
                    match_score = match_data.get("match_score", 0)

                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="background-color: {COLORS["primary"]}; display: inline-block; padding: 10px 20px; 
                        border-radius: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                            <span style="color: white; font-size: 1.5rem; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                            Match Score: {match_score}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display matches and gaps
                    for match in match_data.get("key_matches", []):
                        st.success(f"✅ {match}")
                    for gap in match_data.get("gaps", []):
                        st.warning(f"⚠️ {gap}")

            except Exception as e:
                st.error(f"Match analysis failed: {str(e)}")


def _render_job_actions(job):
    """Render job action buttons."""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Job", key="save_job_btn"):
            save_job_to_local(job)
            st.session_state.saved_jobs = load_saved_jobs()
            st.success("Job saved successfully!")
    
    with col2:
        if st.button("Prepare for Interview", key="prepare_interview_btn"):
            st.session_state.active_tab = 2
            st.rerun()