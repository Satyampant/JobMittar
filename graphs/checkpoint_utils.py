
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graphs.state import JobMittrState
from models.interview import InterviewSessionState


async def resume_from_checkpoint(checkpointer: AsyncSqliteSaver,thread_id: str) -> Optional[Dict[str, Any]]:
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = await checkpointer.aget(config)
    
    if not checkpoint:
        return None
    
    state = checkpoint.get("channel_values", {})
    return state


async def list_checkpoints(checkpointer: AsyncSqliteSaver,thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
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
        pass
    
    return checkpoints


async def restore_interview_session(state: Dict[str, Any]) -> Optional[InterviewSessionState]:
    session_dict = state.get("interview_session")
    if not session_dict:
        return None
    
    session = InterviewSessionState(**session_dict)
    return session


async def clear_checkpoint(checkpointer: AsyncSqliteSaver,thread_id: str):
    pass


def format_checkpoint_summary(state: Dict[str, Any]) -> str:
    summary = []

    current_step = state.get("current_step", "unknown")
    summary.append(f"Current Step: {current_step}")
    
    if state.get("resume_data"):
        name = state["resume_data"].get("name", "Unknown")
        summary.append(f"Resume: {name}")
    
    job_count = len(state.get("job_results", []))
    if job_count > 0:
        summary.append(f"Jobs Found: {job_count}")
    
    if state.get("selected_job"):
        job_title = state["selected_job"].get("title", "Unknown")
        summary.append(f"Selected Job: {job_title}")
    
    session_dict = state.get("interview_session")
    if session_dict:
        question_index = session_dict.get("current_question_index", 0)
        total_questions = len(session_dict.get("questions", []))
        responses = len(session_dict.get("responses", []))
        summary.append(f"Interview Progress: {responses}/{total_questions} questions")
        summary.append(f"Current Question Index: {question_index}")
    
    if state.get("error"):
        summary.append(f"Error: {state['error']}")
    
    return "\n".join(summary)
