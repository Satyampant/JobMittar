"""Main LangGraph workflow for JobMittar.

This module defines the core StateGraph that orchestrates:
- Resume parsing and analysis
- Job search and matching
- Interview preparation and simulation

The graph replaces manual control flow with declarative node/edge definitions.
"""

from langgraph.graph import StateGraph, END
from graphs.state import JobMittrState, create_initial_state


def create_job_mittr_graph() -> StateGraph:
    """Initialize the JobMittar workflow graph.
    
    Returns:
        Configured StateGraph ready for compilation
    """
    # Initialize graph with state schema
    graph = StateGraph(JobMittrState)
    
    # Nodes will be added here as they're implemented
    # Example:
    # graph.add_node("parse_resume", parse_resume_node)
    # graph.add_node("search_jobs", search_jobs_node)
    # graph.add_node("analyze_match", analyze_match_node)
    
    # Entry point will be set here
    # graph.set_entry_point("parse_resume")
    
    # Edges will be added here
    # graph.add_conditional_edges("parse_resume", route_after_resume)
    # graph.add_edge("search_jobs", "job_selection")
    
    return graph


def compile_graph() -> any:
    """Compile the graph into an executable workflow.
    
    Returns:
        Compiled graph ready for invocation
    """
    graph = create_job_mittr_graph()
    return graph.compile()


# Example usage and validation
if __name__ == "__main__":
    # Test state creation
    print("Testing state initialization...")
    initial_state = create_initial_state(
        current_step="resume_upload",
        resume_data={"name": "John Doe", "email": "john@example.com"}
    )
    print(f"✓ Created initial state with step: {initial_state['current_step']}")
    
    # Test state validation
    print("\nTesting state validation...")
    from graphs.state import validate_state
    
    valid, error = validate_state(initial_state)
    if valid:
        print("✓ State validation passed")
    else:
        print(f"✗ State validation failed: {error}")
    
    # Test invalid state
    print("\nTesting invalid state rejection...")
    invalid_state = JobMittrState(
        current_step="invalid_step",
        resume_data=None,
        job_results=[],
        messages=[]
    )
    valid, error = validate_state(invalid_state)
    if not valid:
        print(f"✓ Invalid state correctly rejected: {error}")
    else:
        print("✗ Invalid state incorrectly accepted")
    
    # Test graph initialization
    print("\nTesting graph initialization...")
    try:
        graph = create_job_mittr_graph()
        print(f"✓ Graph created successfully: {type(graph)}")
        print(f"✓ Graph state schema: {graph.channels}")
    except Exception as e:
        print(f"✗ Graph creation failed: {e}")
    
    print("\n" + "="*60)
    print("Step 1 Implementation Complete!")
    print("="*60)
    print("\nNext steps:")
    print("- Implement node functions in graphs/nodes/")
    print("- Wire nodes into the graph")
    print("- Add conditional routing logic")
    print("- Integrate with existing tools/executor.py")