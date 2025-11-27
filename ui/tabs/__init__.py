"""Tab handler modules for main application tabs."""

from .resume_analysis import render_resume_analysis_tab
from .job_search import render_job_search_tab
from .interview_prep import render_interview_prep_tab
from .saved_jobs import render_saved_jobs_tab

__all__ = [
    'render_resume_analysis_tab',
    'render_job_search_tab',
    'render_interview_prep_tab',
    'render_saved_jobs_tab'
]