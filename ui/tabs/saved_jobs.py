"""Saved Jobs tab handler."""

import streamlit as st
import pandas as pd

from utils.job_storage import load_saved_jobs
from ui_utils import COLORS


def render_saved_jobs_tab():
    """Render the Saved Jobs tab."""
    st.header("Saved Jobs")

    # Reload saved jobs
    st.session_state.saved_jobs = load_saved_jobs()

    if not st.session_state.saved_jobs:
        _render_empty_state()
    else:
        _render_saved_jobs_list()


def _render_empty_state():
    """Render empty state when no jobs are saved."""
    st.info("You haven't saved any jobs yet.")


def _render_saved_jobs_list():
    """Render list of saved jobs."""
    st.markdown(f"""
    <div style="background-color: {COLORS["primary"]}; color: white; 
    padding: 10px 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
    <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
    You have {len(st.session_state.saved_jobs)} saved jobs</h3>
    </div>
    """, unsafe_allow_html=True)

    # Display saved jobs table
    saved_jobs_df = pd.DataFrame([
        {
            "Title": job.get("title", "Unknown"),
            "Company": job.get("company", "Unknown"),
            "Date Saved": job.get("date_saved", "Recent")
        }
        for job in st.session_state.saved_jobs
    ])

    st.dataframe(saved_jobs_df, use_container_width=True, hide_index=True)