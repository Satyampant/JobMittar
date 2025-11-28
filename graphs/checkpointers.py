"""LangGraph checkpointing - MemorySaver for Streamlit compatibility."""

import sys
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver

# Add project root to path when running directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))


def get_checkpointer() -> MemorySaver:
    """Create in-memory checkpointer (Streamlit-compatible).
    
    MemorySaver is ideal for Streamlit because:
    - No async/event loop issues
    - No context manager complications
    - Persists within session via st.session_state
    - Simple and fast
    
    Returns:
        Configured MemorySaver instance
    """
    return MemorySaver()


# Thread ID generation utilities
def generate_interview_thread_id(job_title: str, user_id: str = "default") -> str:
    """Generate consistent thread ID for interview sessions."""
    safe_title = job_title.replace(" ", "_").lower()
    return f"interview_{user_id}_{safe_title}"


def generate_workflow_thread_id(workflow_type: str, user_id: str = "default") -> str:
    """Generate thread ID for general workflows."""
    return f"workflow_{user_id}_{workflow_type}"


if __name__ == "__main__":
    print("Testing MemorySaver Checkpointer")
    print("=" * 60)
    
    checkpointer = get_checkpointer()
    print(f"✓ Checkpointer initialized: {type(checkpointer)}")
    print(f"✓ Type: MemorySaver (in-memory, session-based)")
    
    thread_id = generate_interview_thread_id("Python Developer")
    print(f"✓ Generated thread ID: {thread_id}")
    
    # Test checkpoint operations
    from langgraph.checkpoint.base import Checkpoint
    from uuid import uuid4
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Create test checkpoint
    test_checkpoint = Checkpoint(
        v=1,
        id=str(uuid4()),
        ts="2024-01-01T00:00:00Z",
        channel_values={"test": "data"}
    )
    
    # Test put/get
    checkpointer.put(config, test_checkpoint, {})
    retrieved = checkpointer.get(config)
    
    print(f"✓ Checkpoint storage works: {retrieved is not None}")
    
    print("\n" + "=" * 60)
    print("MemorySaver checkpointer ready for Streamlit!")