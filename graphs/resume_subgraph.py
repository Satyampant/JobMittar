"""parse → analyze → validate → END."""

from langgraph.graph import StateGraph, END
from graphs.state import JobMittrState
from graphs.nodes.resume_nodes import (
    parse_resume_node,
    analyze_resume_node,
    validate_resume_node
)


def create_resume_subgraph() -> StateGraph:
    subgraph = StateGraph(JobMittrState)
    
    # Add nodes in processing order
    subgraph.add_node("parse_resume", parse_resume_node)
    subgraph.add_node("analyze_resume", analyze_resume_node)
    subgraph.add_node("validate_resume", validate_resume_node)
    
    # Set entry point
    subgraph.set_entry_point("parse_resume")
    
    # Wire sequential flow
    subgraph.add_edge("parse_resume", "analyze_resume")
    subgraph.add_edge("analyze_resume", "validate_resume")
    subgraph.add_edge("validate_resume", END)
    
    return subgraph


def compile_resume_subgraph():
    subgraph = create_resume_subgraph()
    return subgraph.compile()

