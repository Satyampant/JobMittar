
from langgraph.graph import StateGraph, END
from graphs.state import JobMittrState
from graphs.nodes.interview_nodes import (
    generate_questions_node,
    initialize_interview_session_node,
    conduct_question_node,
    advance_question_node,
    finalize_interview_node
)


def route_interview_progress(state: JobMittrState) -> str:
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return "error"
    
    from models.interview import InterviewSessionState
    session = InterviewSessionState(**session_dict)
    
    if session.current_question_index >= len(session.questions):
        return "finalize_interview"
    
    if len(session.responses) > session.current_question_index:
        return "advance_question"
    
    return "conduct_question"


def route_after_conduct(state: JobMittrState) -> str:
    current_step = state.get("current_step", "")
    
    if current_step == "awaiting_response":
        return "await_input"
    
    if state.get("error"):
        return "error"
    
    return "check_progress"


def create_interview_subgraph() -> StateGraph:
    
    subgraph = StateGraph(JobMittrState)
    
    subgraph.add_node("generate_questions", generate_questions_node)
    subgraph.add_node("initialize_session", initialize_interview_session_node)
    subgraph.add_node("conduct_question", conduct_question_node)
    subgraph.add_node("advance_question", advance_question_node)
    subgraph.add_node("finalize_interview", finalize_interview_node)
    
    subgraph.add_node("await_input", lambda state: {**state, "current_step": "awaiting_response"})
    
    subgraph.add_node("check_progress", lambda state: state)
    
    subgraph.set_entry_point("generate_questions")
    
    subgraph.add_edge("generate_questions", "initialize_session")
    subgraph.add_edge("initialize_session", "conduct_question")
    
    subgraph.add_conditional_edges(
        "conduct_question",
        route_after_conduct,
        {
            "await_input": "await_input",  # Pause for user input
            "check_progress": "check_progress",
            "error": END
        }
    )
    
    subgraph.add_edge("await_input", "conduct_question")
    
    subgraph.add_conditional_edges(
        "check_progress",
        route_interview_progress,
        {
            "advance_question": "advance_question",
            "conduct_question": "conduct_question",
            "finalize_interview": "finalize_interview",
            "error": END
        }
    )
    
    subgraph.add_edge("advance_question", "conduct_question")
    
    subgraph.add_edge("finalize_interview", END)
    
    return subgraph


def compile_interview_subgraph():
    subgraph = create_interview_subgraph()
    return subgraph.compile()

