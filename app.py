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
    display_matching_skills,
    apply_styling,
    COLORS
)

# Import job storage utilities
from utils.job_storage import (
    save_job_to_local,
    load_saved_jobs,
    remove_saved_job
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

# Apply custom styling (maintains legacy visual design)
apply_styling()

# Application header with gradient (maintains legacy design)
st.markdown(f"""
<div style='text-align:center; padding: 1.5rem 0; 
background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}, {COLORS["tertiary"]}); 
border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
    <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
    Professional Job Search Assistant</h1>
    <p style='color: white; font-size: 1.2rem; font-weight: 500; margin: 0.5rem 2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    AI-powered job search</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Resume analysis</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Interview preparation</span>
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

# Create main navigation tabs (maintains legacy layout)
tabs = st.tabs([
    "📄 Resume Analysis", 
    "🔍 Job Search", 
    "🎯 Interview Preparation", 
    "💼 Saved Jobs"
])

# Common job titles and locations (from legacy)
common_job_titles = [
    "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
    "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "DevOps Engineer", "UX Designer", "AI Engineer",
    "Cloud Architect", "Database Administrator", "Project Manager", "Business Analyst",
    "Java Developer", "Python Developer", "React Developer", "Android Developer",
    "iOS Developer", "Node.js Developer", "Data Engineer", "Blockchain Developer",
    "Cybersecurity Analyst", "Quality Assurance Engineer"
]

locations = [
    "Remote",
    "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
    "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Atlanta, GA", "Denver, CO",
    "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Delhi, India",
    "Pune, India", "Chennai, India", "London, UK", "Berlin, Germany", "Toronto, Canada"
]

# Tab 1: Resume Analysis (maintains legacy visual design)
with tabs[0]:
    st.header("Resume Analysis")

    # Create two columns for upload options
    col1, col2 = st.columns(2)

    with col1:
        # Resume upload section
        st.subheader("Upload Resume")
        st.markdown(f"""
        <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <p style="margin-bottom: 10px;">Upload your resume in PDF, DOCX, or TXT format.</p>
        <p>We'll analyze your resume and extract key information to help you find matching jobs.</p>
        </div>
        """, unsafe_allow_html=True)

        # Resume file uploader
        resume_file = st.file_uploader("Upload your resume", type=["pdf", "txt", "docx"], key="resume_uploader")

        # Process uploaded resume using NEW BACKEND
        if resume_file is not None:
            with st.spinner("Analyzing your resume..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(resume_file.getbuffer())
                        temp_path = temp_file.name

                    # Read file using NEW backend file reader
                    extracted_text = read_resume_file(temp_path)

                    # Clean up temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

                    if extracted_text:
                        # Parse resume using NEW Pydantic-based extractor
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

                        # Generate analysis using the resume data
                        analysis = f"""
OVERALL ASSESSMENT

Strengths:
• {len(resume.skills)} technical skills identified
• {len(resume.experience)} work experiences documented
• Clear contact information provided

Weaknesses:
• Consider adding more quantifiable achievements
• Expand skill descriptions with proficiency levels

CONTENT IMPROVEMENTS
• Use action verbs to describe responsibilities
• Include metrics and results where possible
• Organize skills by category

FORMAT SUGGESTIONS
• Maintain consistent formatting throughout
• Use clear section headings
• Keep to 1-2 pages maximum

ATS OPTIMIZATION
• Include relevant keywords from job descriptions
• Use standard fonts and formatting
• Save as PDF to maintain formatting
"""

                        resume_dict["analysis"] = analysis

                        # Store in session state
                        st.session_state.resume_data = resume_dict

                        st.success("Resume analysis complete! Review the extracted information and analysis below.")
                    else:
                        st.error("Could not extract text from the uploaded file.")

                except Exception as e:
                    st.error(f"Error analyzing resume: {str(e)}")
                    st.info("If the error persists, try uploading a different file format or check if the resume is properly formatted.")

    with col2:
        # Resume tips (maintains legacy design)
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

    # Display resume analysis results (maintains legacy visual style)
    if "resume_data" in st.session_state and st.session_state.resume_data:
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
                st.info("No detailed analysis available. Please re-upload your resume to generate an analysis.")

        with resume_tabs[3]:
            if "raw_text" in st.session_state.resume_data:
                st.text_area("Extracted Text", st.session_state.resume_data["raw_text"], height=400, disabled=True)
            else:
                st.info("Raw text not available.")

    else:
        # No resume uploaded message
        st.markdown(f"""
        <div style="background-color: {COLORS["background"]}; padding: 20px; border-radius: 8px; border: 1px dashed {COLORS["primary"]}; text-align: center; margin-top: 30px;">
        <img src="https://img.icons8.com/fluency/96/000000/resume.png" style="width: 64px; height: 64px; margin-bottom: 15px;">
        <h3 style="color: {COLORS["primary"]};">No Resume Uploaded</h3>
        <p>Upload your resume using the file uploader above to see the analysis.</p>
        </div>
        """, unsafe_allow_html=True)

# Tab 2: Job Search (NEW backend integration)
with tabs[1]:
    st.header("Job Search")

    # Search tabs
    search_tabs = st.tabs(["📄 Resume-Based Search", "🔍 Custom Search"])

    # Resume-Based Search
    with search_tabs[0]:
        if st.session_state.resume_data:
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
                default_location = st.selectbox("Location:", locations, index=0, key="resume_search_location")

            with col2:
                resume_search_button = st.button("Search Jobs", key="resume_based_search")

            if resume_search_button:
                with st.spinner("Searching for jobs..."):
                    try:
                        # Extract keywords from resume
                        skills = st.session_state.resume_data.get("skills", [])
                        search_keywords = " ".join(skills[:3])  # Use top 3 skills

                        # Use NEW backend tool executor
                        result = execute_tool("search_jobs", {
                            "keywords": search_keywords,
                            "location": default_location,
                            "platform": "LinkedIn",
                            "count": 10
                        })

                        if result["success"]:
                            jobs = result["result"]
                            st.session_state.job_results = jobs
                            st.success(f"Found {len(jobs)} jobs matching your resume!")
                            st.rerun()
                        else:
                            st.error(f"Job search failed: {result.get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Error searching for jobs: {str(e)}")
        else:
            st.warning("Please upload your resume in the Resume Analysis tab first.")

    # Custom Search Tab
    with search_tabs[1]:
        with st.form("job_search_form"):
            st.subheader("Search Criteria")

            col1, col2 = st.columns(2)

            with col1:
                keywords = st.selectbox("Job Title:", common_job_titles, key="job_titles")

            with col2:
                location = st.selectbox("Location:", locations, key="locations")

            # Advanced filters
            with st.expander("Advanced Filters", expanded=False):
                selected_platforms = st.multiselect(
                    "Job Platforms:",
                    options=["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "Monster"],
                    default=["LinkedIn", "Indeed"],
                    key="platforms"
                )

                job_count = st.slider("Jobs per platform:", 3, 20, 5, key="job_count")

            submit_search = st.form_submit_button("Search Jobs")

        if submit_search:
            with st.spinner(f"Searching for {keywords} jobs in {location}..."):
                all_jobs = []
                for platform in selected_platforms:
                    try:
                        # Use NEW backend tool executor
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

    # Display job results (maintains legacy visual design)
    if st.session_state.job_results:
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

        # Job selection
        if st.session_state.job_results:
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

                # Job header (maintains legacy styling)
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.2);'>
                    <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>{selected_job.get('title', 'Unknown')}</h3>
                    <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{selected_job.get('company', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Job description
                if selected_job.get('description'):
                    st.subheader("Job Description")
                    st.markdown(format_job_description(selected_job['description']), unsafe_allow_html=True)

                # Match analysis using NEW backend
                if st.session_state.resume_data:
                    with st.expander("Resume Match Analysis", expanded=True):
                        with st.spinner("Analyzing match..."):
                            try:
                                result = execute_tool("analyze_job_match", {
                                    "resume_data": st.session_state.resume_data,
                                    "job_data": selected_job
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

                # Job actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Job", key="save_job_btn"):
                        save_job_to_local(selected_job)
                        st.session_state.saved_jobs = load_saved_jobs()
                        st.success("Job saved successfully!")
                with col2:
                    if st.button("Prepare for Interview", key="prepare_interview_btn"):
                        st.session_state.active_tab = 2
                        st.rerun()

# Tab 3: Interview Preparation (NEW backend integration)
# Tab 3: Interview Preparation (UPDATED with Interactive Interview)
with tabs[2]:
    st.header("Interview Preparation")

    if st.session_state.selected_job:
        selected_job = st.session_state.selected_job

        st.markdown(f"""
        <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
        padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.15);'>
            <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>Prepare for: {selected_job.get('title', 'Unknown')}</h3>
            <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{selected_job.get('company', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Check if interview session is active
        if st.session_state.get('interview_session') and st.session_state.interview_session.is_active:
            # Render active interview session
            from components.interview_ui import InterviewUI
            
            interview_ui = InterviewUI()
            interview_ui.render_interview_header()
            interview_ui.render_current_question()
            interview_ui.render_response_recorder()
            interview_ui.render_navigation_buttons()
        else:
            # Setup new interview
            col1, col2 = st.columns(2)

            with col1:
                interview_type = st.radio(
                    "Select interview preparation type:",
                    ["Technical Interview", "Behavioral Interview", "Coding Interview"],
                    key="interview_type"
                )

                num_questions = st.slider("Number of questions:", 5, 20, 10, key="num_interview_questions")

                # Two modes: Generate and Review OR Start Live Interview
                mode_col1, mode_col2 = st.columns(2)
                
                with mode_col1:
                    generate_btn = st.button("📝 Generate Questions", key="generate_interview_btn")
                
                with mode_col2:
                    start_live_btn = st.button("🎙️ Start Live Interview", key="start_live_interview_btn")

            with col2:
                st.subheader("Quick Tips")
                st.markdown(f"""
                <div style="background-color: {COLORS["primary"]}; color: white; padding: 15px; 
                border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0; font-weight: 600; margin-bottom: 10px; color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.2);">Interview Tips:</h4>
                <ul style="margin-bottom: 0; padding-left: 20px;">
                <li>Research the company thoroughly</li>
                <li>Prepare specific examples using STAR method</li>
                <li>Practice your technical skills</li>
                <li>Prepare questions for the interviewer</li>
                <li><strong>NEW:</strong> Try the live interview mode for realistic practice!</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

            # Generate questions for review
            if generate_btn:
                with st.spinner("Generating interview questions..."):
                    try:
                        result = execute_tool("generate_interview_questions", {
                            "job_data": selected_job,
                            "resume_data": st.session_state.resume_data,
                            "question_count": num_questions
                        })

                        if result["success"]:
                            questions = result["result"]
                            st.session_state.interview_questions = {
                                'job': selected_job,
                                'type': interview_type,
                                'questions': questions
                            }
                            st.rerun()
                        else:
                            st.error(f"Failed to generate questions: {result.get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Error generating questions: {str(e)}")
            
            # Start live interview
            if start_live_btn:
                with st.spinner("Preparing your live interview..."):
                    try:
                        # Generate questions if not already generated
                        if not st.session_state.get('interview_questions'):
                            result = execute_tool("generate_interview_questions", {
                                "job_data": selected_job,
                                "resume_data": st.session_state.resume_data,
                                "question_count": num_questions
                            })

                            if result["success"]:
                                questions = result["result"]
                            else:
                                st.error("Failed to generate questions for live interview")
                                questions = None
                        else:
                            questions = st.session_state.interview_questions['questions']
                        
                        if questions:
                            # Initialize live interview session
                            from components.interview_ui import InterviewUI
                            
                            interview_ui = InterviewUI()
                            interview_ui.start_interview_session(
                                job_data=selected_job,
                                questions=questions,
                                interview_type=interview_type
                            )
                            st.success("Live interview session started!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error starting live interview: {str(e)}")
                        st.info("Make sure you have DEEPGRAM_API_KEY set in your .env file")

            # Display generated questions for review (non-live mode)
            if st.session_state.get('interview_questions') and not st.session_state.get('interview_session'):
                interview_data = st.session_state.interview_questions

                st.markdown(f"""
                <div style="background-color: {COLORS["secondary"]}; color: white; 
                padding: 10px 15px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{interview_data['type']} Questions (Review Mode)</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("💡 These questions are in review mode. Click 'Start Live Interview' above to practice with voice recording and AI feedback!")

                for i, question in enumerate(interview_data['questions'], 1):
                    question_text = question.get('question', 'Question not available')
                    with st.expander(f"Question {i}: {question_text[:80]}...", expanded=i==1):
                        st.markdown(f"""
                        <div style="background-color: {COLORS["primary"]}; color: white; 
                        padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question_text}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        if question.get('suggested_answer'):
                            st.markdown("**Suggested Answer:**")
                            st.write(question['suggested_answer'])

                        if question.get('tips'):
                            st.markdown("**Tips:**")
                            st.write(question['tips'])

                        st.text_area("Your Notes:", key=f"note_{i}", height=100)

    else:
        st.info("Please select a job from the Job Search tab to prepare for an interview.")
        
# Tab 4: Saved Jobs (maintains legacy design)
with tabs[3]:
    st.header("Saved Jobs")

    st.session_state.saved_jobs = load_saved_jobs()

    if not st.session_state.saved_jobs:
        st.info("You haven't saved any jobs yet.")
    else:
        st.markdown(f"""
        <div style="background-color: {COLORS["primary"]}; color: white; 
        padding: 10px 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
        <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">You have {len(st.session_state.saved_jobs)} saved jobs</h3>
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

# Footer (maintains legacy design)
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
    color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Professional Job Search Assistant | Built with Streamlit | © {datetime.now().year}</p>
    </div>""",
    unsafe_allow_html=True
)
