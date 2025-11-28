
from langgraph.graph import StateGraph, END
from graphs.state import JobMittrState
from graphs.nodes.job_nodes import (
    search_jobs_node,
    select_job_node,
    analyze_match_node
)
from graphs.edges import route_after_search, route_after_match_analysis


def create_job_subgraph() -> StateGraph:
    subgraph = StateGraph(JobMittrState)
    
    subgraph.add_node("search_jobs", search_jobs_node)
    subgraph.add_node("select_job", select_job_node)
    subgraph.add_node("analyze_match", analyze_match_node)
    subgraph.add_node("no_results_handler", _no_results_handler)
    
    subgraph.set_entry_point("search_jobs")
    
    subgraph.add_conditional_edges(
        "search_jobs",
        route_after_search,
        {
            "select_job": "select_job",
            "no_results_end": "no_results_handler",
            "error": END
        }
    )
    
    subgraph.add_edge("select_job", "analyze_match")
    
    subgraph.add_conditional_edges(
        "analyze_match",
        route_after_match_analysis,
        {
            "interview_prep": END,  
            "end": END,
            "error": END
        }
    )
    
    subgraph.add_edge("no_results_handler", END)
    
    return subgraph


def _no_results_handler(state: JobMittrState) -> JobMittrState:
    job_query = state.get("job_query", {})
    keywords = job_query.get("keywords", "specified criteria")
    location = job_query.get("location", "specified location")
    
    return {
        **state,
        "error": None, 
        "current_step": "job_search_complete",
        "messages": [
            f"No jobs found for '{keywords}' in '{location}'. Try different keywords or location."
        ]
    }


def compile_job_subgraph():
    subgraph = create_job_subgraph()
    return subgraph.compile()

