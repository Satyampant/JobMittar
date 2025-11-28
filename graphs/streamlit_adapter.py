
import streamlit as st
from typing import Dict, Any, Iterator


def invoke_graph_sync(graph,state: Dict[str, Any],thread_id: str) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result = graph.invoke(state, config=config)
        return result
    except Exception as e:
        st.error(f"Graph execution failed: {str(e)}")
        return {**state, "error": str(e)}


def stream_to_streamlit(graph,state: Dict[str, Any],thread_id: str) -> Iterator[Dict[str, Any]]:
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        for event in graph.stream(state, config=config):
            for node_name, node_state in event.items():
                current_step = node_state.get("current_step", "unknown")
                
                with st.status(f"🔄 {node_name.replace('_', ' ').title()}", expanded=False) as status:
                    st.write(f"Step: {current_step}")
                    
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
    if "thread_id" not in st.session_state:
        import uuid
        st.session_state.thread_id = f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    return st.session_state.thread_id


def display_state_summary(state: Dict[str, Any]):
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
        
        if state.get("error"):
            st.error(f"Error: {state['error']}")


def reset_graph_state():
    keys_to_clear = [
        "resume_data", "job_results", "selected_job",
        "match_analysis", "interview_questions", "interview_session"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Workflow state reset!")