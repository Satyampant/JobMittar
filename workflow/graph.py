from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from workflows.state import JobSearchState, WorkflowStatus
from workflows.nodes import parse_resume_node, search_jobs_node, analyze_match_node, generate_questions_node

def should_search_jobs(state: JobSearchState) -> str:
    """Conditional edge: determine if job search should run"""
    return "search_jobs" if state.get("search_keywords") else "end"

def should_analyze_match(state: JobSearchState) -> str:
    """Conditional edge: determine if match analysis should run"""
    return "analyze_match" if state.get("selected_job") else "end"

def create_workflow() -> StateGraph:
    """Create job search workflow graph with checkpointing"""
    workflow = StateGraph(JobSearchState)
    
    # Add nodes
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("search_jobs", search_jobs_node)
    workflow.add_node("analyze_match", analyze_match_node)
    workflow.add_node("generate_questions", generate_questions_node)
    
    # Define edges
    workflow.set_entry_point("parse_resume")
    workflow.add_conditional_edges("parse_resume", should_search_jobs, {"search_jobs": "search_jobs", "end": END})
    workflow.add_conditional_edges("search_jobs", should_analyze_match, {"analyze_match": "analyze_match", "end": END})
    workflow.add_edge("analyze_match", "generate_questions")
    workflow.add_edge("generate_questions", END)
    
    # Compile with checkpointing
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
