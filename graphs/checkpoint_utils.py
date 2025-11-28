"""Checkpoint recovery and state restoration utilities."""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graphs.state import JobMittrState
from models.interview import InterviewSessionState


async def resume_from_checkpoint(
    checkpointer: AsyncSqliteSaver,
    thread_id: str
) -> Optional[Dict[str, Any]]:
    """Resume workflow from last checkpoint.
    
    Args:
        checkpointer: Configured checkpointer instance
        thread_id: Thread identifier for the workflow
        
    Returns:
        Restored state dictionary or None if not found
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Get latest checkpoint
    checkpoint = await checkpointer.aget(config)
    
    if not checkpoint:
        return None
    
    # Extract state from checkpoint
    state = checkpoint.get("channel_values", {})
    
    return state


async def list_checkpoints(
    checkpointer: AsyncSqliteSaver,
    thread_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List all checkpoints for a thread or all threads.
    
    Args:
        checkpointer: Configured checkpointer instance
        thread_id: Optional thread ID filter
        
    Returns:
        List of checkpoint metadata
    """
    checkpoints = []
    
    if thread_id:
        config = {"configurable": {"thread_id": thread_id}}
        async for checkpoint in checkpointer.alist(config):
            checkpoints.append({
                "thread_id": thread_id,
                "checkpoint_id": checkpoint.get("id"),
                "timestamp": checkpoint.get("ts"),
                "channel_values": checkpoint.get("channel_values", {})
            })
    else:
        # List all threads (requires custom query - simplified for now)
        pass
    
    return checkpoints


async def restore_interview_session(
    state: Dict[str, Any]
) -> Optional[InterviewSessionState]:
    """Restore interview session from checkpoint state.
    
    Args:
        state: Checkpoint state dictionary
        
    Returns:
        Reconstructed InterviewSessionState or None
    """
    session_dict = state.get("interview_session")
    
    if not session_dict:
        return None
    
    # Reconstruct Pydantic model from dict
    session = InterviewSessionState(**session_dict)
    
    return session


async def clear_checkpoint(
    checkpointer: AsyncSqliteSaver,
    thread_id: str
):
    """Clear all checkpoints for a thread.
    
    Args:
        checkpointer: Configured checkpointer instance
        thread_id: Thread identifier to clear
    """
    # LangGraph handles checkpoint cleanup internally
    # This is a placeholder for explicit deletion if needed
    pass


def format_checkpoint_summary(state: Dict[str, Any]) -> str:
    """Format checkpoint state into human-readable summary.
    
    Args:
        state: Checkpoint state dictionary
        
    Returns:
        Formatted summary string
    """
    summary = []
    
    # Workflow step
    current_step = state.get("current_step", "unknown")
    summary.append(f"Current Step: {current_step}")
    
    # Resume data
    if state.get("resume_data"):
        name = state["resume_data"].get("name", "Unknown")
        summary.append(f"Resume: {name}")
    
    # Job search
    job_count = len(state.get("job_results", []))
    if job_count > 0:
        summary.append(f"Jobs Found: {job_count}")
    
    # Selected job
    if state.get("selected_job"):
        job_title = state["selected_job"].get("title", "Unknown")
        summary.append(f"Selected Job: {job_title}")
    
    # Interview session
    session_dict = state.get("interview_session")
    if session_dict:
        question_index = session_dict.get("current_question_index", 0)
        total_questions = len(session_dict.get("questions", []))
        responses = len(session_dict.get("responses", []))
        summary.append(f"Interview Progress: {responses}/{total_questions} questions")
        summary.append(f"Current Question Index: {question_index}")
    
    # Error state
    if state.get("error"):
        summary.append(f"Error: {state['error']}")
    
    return "\n".join(summary)


if __name__ == "__main__":
    # Test checkpoint utilities
    print("Testing Checkpoint Recovery Utilities")
    print("=" * 60)
    
    async def test_recovery():
        from graphs.checkpointers import get_checkpointer
        
        checkpointer = await get_checkpointer()
        
        # Test with non-existent thread
        state = await resume_from_checkpoint(checkpointer, "test_thread_999")
        print(f"✓ Non-existent thread returns: {state}")
        
        # Test checkpoint listing
        checkpoints = await list_checkpoints(checkpointer, "test_thread_999")
        print(f"✓ Checkpoints listed: {len(checkpoints)}")
        
        # Test session restoration with mock data
        mock_state = {
            "current_step": "interview_active",
            "resume_data": {"name": "John Doe"},
            "interview_session": {
                "job_title": "Python Developer",
                "company_name": "Tech Corp",
                "interview_type": "Technical",
                "questions": [{"question": "Q1"}, {"question": "Q2"}],
                "responses": [],
                "current_question_index": 0,
                "is_active": True
            }
        }
        
        session = await restore_interview_session(mock_state)
        print(f"✓ Session restored: {session is not None}")
        if session:
            print(f"  - Job: {session.job_title}")
            print(f"  - Questions: {len(session.questions)}")
        
        # Test formatting
        summary = format_checkpoint_summary(mock_state)
        print(f"\n✓ Checkpoint Summary:\n{summary}")
    
    asyncio.run(test_recovery())
    print("\n" + "=" * 60)
    print("Checkpoint utilities tested successfully!")