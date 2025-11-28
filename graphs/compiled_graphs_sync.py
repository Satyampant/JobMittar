"""Synchronous graph compilation for Streamlit compatibility."""

from graphs.master_graph import build_master_graph
from graphs.checkpointers import get_checkpointer


def compile_master_graph_sync():
    """Compile master graph synchronously for Streamlit.
    
    Returns:
        Compiled graph with checkpointing enabled
    """
    # Get synchronous checkpointer (no async/await needed)
    checkpointer = get_checkpointer()
    
    # Build and compile graph
    graph = build_master_graph()
    compiled = graph.compile(checkpointer=checkpointer)
    
    return compiled


if __name__ == "__main__":
    print("Testing Synchronous Graph Compilation")
    print("=" * 60)
    
    try:
        graph = compile_master_graph_sync()
        print(f"✓ Graph compiled: {graph is not None}")
        print(f"✓ Checkpointer enabled: {graph.checkpointer is not None}")
        
        # Test basic invocation
        from langchain_core.messages import HumanMessage
        
        test_state = {
            "messages": [HumanMessage(content="Test")],
            "current_step": "resume_upload",
            "resume_data": None,
            "job_results": []
        }
        
        result = graph.invoke(test_state, config={"configurable": {"thread_id": "test"}})
        print(f"✓ Invocation successful: {result.get('current_step')}")
        
    except Exception as e:
        print(f"✗ Compilation failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Synchronous compilation ready for Streamlit!")