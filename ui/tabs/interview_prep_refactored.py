
import streamlit as st
from langchain_core.messages import HumanMessage

from components.interview_ui import InterviewUI
from ui_utils import COLORS
from graphs.streamlit_adapter import (
    invoke_graph_sync,
    stream_to_streamlit,
    get_or_create_thread_id,
    display_state_summary
)


def render_interview_prep_tab(graph):
    
    st.header("Interview Preparation")

    if st.session_state.get("selected_job"):
        if st.session_state.get('interview_session') and st.session_state.interview_session.get('is_active'):
            _render_active_interview_with_graph(graph)
        else:
            _render_interview_setup(graph)
    else:
        st.info("Please select a job from the Job Search tab first.")


def _render_active_interview_with_graph(graph):
    """Render active interview using graph with checkpoint resumption."""
    st.info("🎙️ **Live Interview Session** - Powered by LangGraph with checkpoint persistence")
    
    interview_ui = InterviewUI()
    
    interview_ui.render_interview_header()
    interview_ui.render_current_question()
    interview_ui.render_response_recorder()
    interview_ui.render_navigation_buttons()
    
    thread_id = get_or_create_thread_id("interview")
    with st.expander("🔧 Debug Info"):
        st.write(f"Thread ID: {thread_id}")
        st.write(f"Checkpoint enabled: {graph.checkpointer is not None}")


def _render_interview_setup(graph):
    selected_job = st.session_state.selected_job

    st.markdown(f"""
    <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h3 style='color: white; margin: 0;'>Prepare for: {selected_job.get('title', 'Unknown')}</h3>
        <p style='color: white; margin: 0.5rem 0 0 0;'>{selected_job.get('company', 'Unknown')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        _render_setup_controls(graph)

    with col2:
        _render_interview_tips()

    if st.session_state.get('interview_questions') and not st.session_state.get('interview_session'):
        _render_review_mode_questions()


def _render_setup_controls(graph):
    interview_type = st.radio(
        "Interview type:",
        ["Technical Interview", "Behavioral Interview", "Coding Interview"],
        key="interview_type"
    )

    num_questions = st.slider("Number of questions:", 5, 20, 10, key="num_interview_questions")

    mode_col1, mode_col2 = st.columns(2)
    
    with mode_col1:
        generate_btn = st.button("📝 Generate Questions", key="generate_interview_btn")
    
    with mode_col2:
        start_live_btn = st.button("🎙️ Start Live Interview", key="start_live_interview_btn")

    if generate_btn:
        _generate_questions_via_graph(num_questions, graph)
    
    if start_live_btn:
        _start_live_interview_via_graph(interview_type, num_questions, graph)


def _generate_questions_via_graph(num_questions: int, graph):
    with st.spinner("🔄 Generating questions via LangGraph..."):
        try:
            thread_id = get_or_create_thread_id("interview_prep")
            
            state = {
                "selected_job": st.session_state.selected_job,
                "resume_data": st.session_state.get("resume_data"),
                "current_step": "interview_prep",
                "user_preferences": {"question_count": num_questions},
                "messages": [HumanMessage(content=f"Generate {num_questions} interview questions")]
            }

            final_state = None
            for state_update in stream_to_streamlit(graph, state, thread_id):
                final_state = state_update
                
                if state_update.get("interview_questions"):
                    st.session_state.interview_questions = {
                        'job': st.session_state.selected_job,
                        'type': st.session_state.interview_type,
                        'questions': state_update["interview_questions"]
                    }

            if final_state:
                display_state_summary(final_state)
                
                if final_state.get("error"):
                    st.error(f"Generation failed: {final_state['error']}")
                else:
                    st.success("✅ Questions generated!")
                    st.rerun()

        except Exception as e:
            st.error(f"Error: {str(e)}")


def _start_live_interview_via_graph(interview_type: str, num_questions: int, graph):
    with st.spinner("🔄 Initializing live interview with checkpointing..."):
        try:
            # Generate questions if not present
            if not st.session_state.get('interview_questions'):
                thread_id = get_or_create_thread_id("interview_prep")
                
                state = {
                    "selected_job": st.session_state.selected_job,
                    "resume_data": st.session_state.get("resume_data"),
                    "current_step": "interview_prep",
                    "user_preferences": {"question_count": num_questions},
                    "messages": [HumanMessage(content=f"Generate {num_questions} questions")]
                }
                
                result_state = invoke_graph_sync(graph, state, thread_id)
                
                if not result_state.get("interview_questions"):
                    st.error("Failed to generate questions")
                    return
                
                questions = result_state["interview_questions"]
            else:
                questions = st.session_state.interview_questions['questions']
            
            # Initialize session via InterviewUI (which will store in session_state)
            interview_ui = InterviewUI()
            interview_ui.start_interview_session(
                job_data=st.session_state.selected_job,
                questions=questions,
                interview_type=interview_type
            )
            
            st.success("✅ Live interview started with checkpoint support!")
            st.info("💡 You can refresh the page - your progress will be saved!")
            st.rerun()
        
        except Exception as e:
            st.error(f"Error: {str(e)}")


def _render_interview_tips():
    st.subheader("Quick Tips")
    st.markdown(f"""
    <div style="background-color: {COLORS["primary"]}; color: white; padding: 15px; 
    border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: white;">Interview Tips:</h4>
    <ul style="margin-bottom: 0;">
    <li>Research the company thoroughly</li>
    <li>Use STAR method for examples</li>
    <li>Practice technical skills</li>
    <li>Prepare questions for interviewer</li>
    <li><strong>NEW:</strong> Sessions persist across page refreshes!</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def _render_review_mode_questions():
    interview_data = st.session_state.interview_questions

    st.markdown(f"""
    <div style="background-color: {COLORS["secondary"]}; color: white; 
    padding: 10px 15px; border-radius: 8px; margin: 20px 0;">
    <h3 style="margin: 0;">{interview_data['type']} Questions (Review Mode)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Click 'Start Live Interview' above for voice recording with AI feedback!")

    for i, question in enumerate(interview_data['questions'], 1):
        question_text = question.get('question', 'Question not available')
        with st.expander(f"❓ Question {i}: {question_text[:80]}...", expanded=i==1):
            st.markdown(f"""
            <div style="background-color: {COLORS["primary"]}; color: white; 
            padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            {question_text}
            </div>
            """, unsafe_allow_html=True)

            if question.get('suggested_answer'):
                st.markdown("**Suggested Answer:**")
                st.write(question['suggested_answer'])

            if question.get('tips'):
                st.markdown("**Tips:**")
                st.write(question['tips'])

            st.text_area("Your Notes:", key=f"note_{i}", height=100)