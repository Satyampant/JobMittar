"""Interview Preparation tab handler."""

import streamlit as st

from tools.executor import execute_tool
from components.interview_ui import InterviewUI
from ui_utils import COLORS


def render_interview_prep_tab():
    """Render the Interview Preparation tab."""
    st.header("Interview Preparation")

    if st.session_state.get("selected_job"):
        # Check if interview session is active
        if st.session_state.get('interview_session') and st.session_state.interview_session.is_active:
            _render_active_interview()
        else:
            _render_interview_setup()
    else:
        st.info("Please select a job from the Job Search tab to prepare for an interview.")


def _render_active_interview():
    """Render active interview session."""
    interview_ui = InterviewUI()
    
    interview_ui.render_interview_header()
    interview_ui.render_current_question()
    interview_ui.render_response_recorder()
    interview_ui.render_navigation_buttons()


def _render_interview_setup():
    """Render interview setup interface."""
    selected_job = st.session_state.selected_job

    st.markdown(f"""
    <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
    padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.15);'>
        <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
        Prepare for: {selected_job.get('title', 'Unknown')}</h3>
        <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
        {selected_job.get('company', 'Unknown')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        _render_setup_controls()

    with col2:
        _render_interview_tips()

    # Display generated questions if available
    if st.session_state.get('interview_questions') and not st.session_state.get('interview_session'):
        _render_review_mode_questions()


def _render_setup_controls():
    """Render interview setup controls."""
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

    if generate_btn:
        _generate_interview_questions(num_questions)
    
    if start_live_btn:
        _start_live_interview(interview_type, num_questions)


def _render_interview_tips():
    """Render interview tips."""
    st.subheader("Quick Tips")
    st.markdown(f"""
    <div style="background-color: {COLORS["primary"]}; color: white; padding: 15px; 
    border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; font-weight: 600; margin-bottom: 10px; color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.2);">
    Interview Tips:</h4>
    <ul style="margin-bottom: 0; padding-left: 20px;">
    <li>Research the company thoroughly</li>
    <li>Prepare specific examples using STAR method</li>
    <li>Practice your technical skills</li>
    <li>Prepare questions for the interviewer</li>
    <li><strong>NEW:</strong> Try the live interview mode for realistic practice!</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def _generate_interview_questions(num_questions: int):
    """Generate interview questions for review."""
    with st.spinner("Generating interview questions..."):
        try:
            result = execute_tool("generate_interview_questions", {
                "job_data": st.session_state.selected_job,
                "resume_data": st.session_state.get("resume_data"),
                "question_count": num_questions
            })

            if result["success"]:
                questions = result["result"]
                st.session_state.interview_questions = {
                    'job': st.session_state.selected_job,
                    'type': st.session_state.interview_type,
                    'questions': questions
                }
                st.rerun()
            else:
                st.error(f"Failed to generate questions: {result.get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")


def _start_live_interview(interview_type: str, num_questions: int):
    """Start live interview session."""
    with st.spinner("Preparing your live interview..."):
        try:
            # Generate questions if not already generated
            if not st.session_state.get('interview_questions'):
                result = execute_tool("generate_interview_questions", {
                    "job_data": st.session_state.selected_job,
                    "resume_data": st.session_state.get("resume_data"),
                    "question_count": num_questions
                })

                if result["success"]:
                    questions = result["result"]
                else:
                    st.error("Failed to generate questions for live interview")
                    return
            else:
                questions = st.session_state.interview_questions['questions']
            
            # Initialize live interview session
            interview_ui = InterviewUI()
            interview_ui.start_interview_session(
                job_data=st.session_state.selected_job,
                questions=questions,
                interview_type=interview_type
            )
            st.success("Live interview session started!")
            st.rerun()
        
        except Exception as e:
            st.error(f"Error starting live interview: {str(e)}")
            st.info("Make sure you have DEEPGRAM_API_KEY set in your .env file")


def _render_review_mode_questions():
    """Render generated questions in review mode."""
    interview_data = st.session_state.interview_questions

    st.markdown(f"""
    <div style="background-color: {COLORS["secondary"]}; color: white; 
    padding: 10px 15px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
    <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
    {interview_data['type']} Questions (Review Mode)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 These questions are in review mode. Click 'Start Live Interview' above to practice with voice recording and AI feedback!")

    for i, question in enumerate(interview_data['questions'], 1):
        question_text = question.get('question', 'Question not available')
        with st.expander(f"❓ Question {i}: {question_text[:80]}...", expanded=i==1):
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