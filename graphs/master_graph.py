
from langgraph.graph import StateGraph, START, END
from graphs.state import JobMittrState

from graphs.nodes.resume_nodes import (
    parse_resume_node,
    analyze_resume_node,
    validate_resume_node
)
from graphs.nodes.job_nodes import (
    search_jobs_node,
    select_job_node,
    analyze_match_node
)
from graphs.nodes.interview_nodes import (
    generate_questions_node,
    initialize_interview_session_node,
    conduct_question_node,
    advance_question_node,
    finalize_interview_node
)
from graphs.nodes.orchestration_nodes import (
    intent_classifier_node,
    error_handler_node,
    workflow_complete_node
)

from graphs.edges.routing import (
    route_from_intent_classifier,
    route_after_resume,
    route_after_job_selection,
    route_after_match_analysis,
    route_to_completion_or_error
)
from graphs.edges import (
    route_after_search,
    route_interview_progress,
    route_after_conduct
)


def build_master_graph() -> StateGraph:
    graph = StateGraph(JobMittrState)
    
    # === Core Orchestration Nodes ===
    graph.add_node("intent_classifier", intent_classifier_node)
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("workflow_complete", workflow_complete_node)
    
    # === Resume Processing Nodes ===
    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("analyze_resume", analyze_resume_node)
    graph.add_node("validate_resume", validate_resume_node)
    
    # === Job Search Nodes ===
    graph.add_node("search_jobs", search_jobs_node)
    graph.add_node("select_job", select_job_node)
    graph.add_node("analyze_match", analyze_match_node)
    graph.add_node("no_results_handler", _no_results_handler)
    
    # === Interview Preparation Nodes ===
    graph.add_node("generate_questions", generate_questions_node)
    graph.add_node("initialize_session", initialize_interview_session_node)
    graph.add_node("conduct_question", conduct_question_node)
    graph.add_node("advance_question", advance_question_node)
    graph.add_node("finalize_interview", finalize_interview_node)
    graph.add_node("await_input", lambda state: {**state, "current_step": "awaiting_response"})
    graph.add_node("check_progress", lambda state: state)
    
    # === Set Entry Point ===
    graph.add_edge(START, "intent_classifier")
    
    # === Intent Classification Routing ===
    graph.add_conditional_edges(
        "intent_classifier",
        route_from_intent_classifier,
        {
            "parse_resume": "parse_resume",
            "search_jobs": "search_jobs",
            "generate_questions": "generate_questions",
            "error": "error_handler"
        }
    )
    
    # === Resume Subgraph Flow ===
    graph.add_edge("parse_resume", "analyze_resume")
    graph.add_edge("analyze_resume", "validate_resume")
    
    # Route after resume validation
    graph.add_conditional_edges(
        "validate_resume",
        route_after_resume,
        {
            "job_search": "search_jobs",
            "complete": "workflow_complete",
            "error": "error_handler"
        }
    )
    
    # === Job Search Subgraph Flow ===
    graph.add_conditional_edges(
        "search_jobs",
        route_after_search,
        {
            "select_job": "select_job",
            "no_results_end": "no_results_handler",
            "error": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "select_job",
        route_after_job_selection,
        {
            "analyze_match": "analyze_match",
            "generate_questions": "generate_questions",
            "complete": "workflow_complete",
            "error": "error_handler"
        }
    )
    
    graph.add_conditional_edges(
        "analyze_match",
        route_after_match_analysis,
        {
            "generate_questions": "generate_questions",
            "complete": "workflow_complete",
            "error": "error_handler"
        }
    )
    
    graph.add_edge("no_results_handler", "workflow_complete")
    
    # === Interview Subgraph Flow ===
    graph.add_edge("generate_questions", "initialize_session")
    graph.add_edge("initialize_session", "conduct_question")
    
    graph.add_conditional_edges(
        "conduct_question",
        route_after_conduct,
        {
            "await_input": "await_input",
            "check_progress": "check_progress",
            "error": "error_handler"
        }
    )
    
    graph.add_edge("await_input", "conduct_question")
    
    graph.add_conditional_edges(
        "check_progress",
        route_interview_progress,
        {
            "advance_question": "advance_question",
            "conduct_question": "conduct_question",
            "finalize_interview": "finalize_interview",
            "error": "error_handler"
        }
    )
    
    graph.add_edge("advance_question", "conduct_question")
    graph.add_edge("finalize_interview", "workflow_complete")
    
    # === Error Handling and Completion ===
    graph.add_edge("error_handler", "workflow_complete")
    graph.add_edge("workflow_complete", END)
    
    return graph


def _no_results_handler(state: JobMittrState) -> JobMittrState:
    """Handle no job results scenario."""
    job_query = state.get("job_query", {})
    keywords = job_query.get("keywords", "specified criteria")
    location = job_query.get("location", "specified location")
    
    return {
        **state,
        "error": None,
        "current_step": "job_search_complete",
        "messages": state.get("messages", []) + [
            f"No jobs found for '{keywords}' in '{location}'. Try different keywords or location."
        ]
    }


def compile_master_graph():
    graph = build_master_graph()
    return graph.compile()
