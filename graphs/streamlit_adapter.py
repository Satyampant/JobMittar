"""Streamlit adapter for LangGraph integration with async/sync bridging."""

import asyncio
import streamlit as st
from typing import Dict, Any, Optional, Iterator
# from langgraph.graph import CompiledGraph
from graphs.checkpointers import get_checkpointer


def invoke_graph_sync(
    graph,
    state: Dict[str, Any],
    thread_id: str
) -> Dict[str, Any]:
    """Synchronous wrapper for graph invocation (Streamlit compatible).
    
    Args:
        graph: Compiled LangGraph instance
        state: Input state dictionary
        thread_id: Thread identifier for checkpointing
        
    Returns:
        Final state after graph execution
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # LangGraph's invoke is synchronous by default
        result = graph.invoke(state, config=config)
        return result
    except Exception as e:
        st.error(f"Graph execution failed: {str(e)}")
        return {**state, "error": str(e)}


def stream_to_streamlit(
    graph,
    state: Dict[str, Any],
    thread_id: str
) -> Iterator[Dict[str, Any]]:
    """Stream graph execution with real-time UI updates.
    
    Args:
        graph: Compiled LangGraph instance
        state: Input state dictionary
        thread_id: Thread identifier for checkpointing
        
    Yields:
        State updates from each node execution
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        for event in graph.stream(state, config=config):
            # Each event is {node_name: state_update}
            for node_name, node_state in event.items():
                current_step = node_state.get("current_step", "unknown")
                
                # Display node progress
                with st.status(f"🔄 {node_name.replace('_', ' ').title()}", expanded=False) as status:
                    st.write(f"Step: {current_step}")
                    
                    # Show errors if any
                    if node_state.get("error"):
                        st.error(node_state["error"])
                        status.update(label=f"❌ {node_name}", state="error")
                    else:
                        status.update(label=f"✅ {node_name}", state="complete")
                
                yield node_state
                
    except Exception as e:
        st.error(f"Stream failed: {str(e)}")
        yield {**state, "error": str(e)}


def get_or_create_thread_id(prefix: str = "streamlit") -> str:
    """Get or create persistent thread ID in Streamlit session state.
    
    Args:
        prefix: Thread ID prefix for namespacing
        
    Returns:
        Thread identifier string
    """
    if "thread_id" not in st.session_state:
        import uuid
        st.session_state.thread_id = f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    return st.session_state.thread_id


async def invoke_graph_async(
    graph,
    state: Dict[str, Any],
    thread_id: str
) -> Dict[str, Any]:
    """Async graph invocation for future integration.
    
    Args:
        graph: Compiled LangGraph instance
        state: Input state dictionary
        thread_id: Thread identifier
        
    Returns:
        Final state after execution
    """
    # Wrap sync invoke in async
    loop = asyncio.get_event_loop()
    config = {"configurable": {"thread_id": thread_id}}
    
    result = await loop.run_in_executor(
        None,
        lambda: graph.invoke(state, config=config)
    )
    
    return result


def display_state_summary(state: Dict[str, Any]):
    """Display formatted state summary in Streamlit.
    
    Args:
        state: Current workflow state
    """
    with st.expander("🔍 Workflow State", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Step", state.get("current_step", "unknown"))
        
        with col2:
            resume_loaded = "✅" if state.get("resume_data") else "❌"
            st.metric("Resume", resume_loaded)
        
        with col3:
            jobs_found = len(state.get("job_results", []))
            st.metric("Jobs Found", jobs_found)
        
        # Show error if present
        if state.get("error"):
            st.error(f"Error: {state['error']}")


def reset_graph_state():
    """Clear all graph-related session state."""
    keys_to_clear = [
        "resume_data", "job_results", "selected_job",
        "match_analysis", "interview_questions", "interview_session"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Workflow state reset!")