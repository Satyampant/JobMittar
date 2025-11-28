"""LangGraph checkpointing configuration for persistent state management.

This module configures SQLite-based checkpointing to enable:
- Session resumption across process restarts
- Interview state recovery after interruptions
- Thread-based workflow isolation
"""

import asyncio
from pathlib import Path
from typing import Optional
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


# Ensure checkpoints directory exists
CHECKPOINT_DIR = Path("checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)
CHECKPOINT_DB = CHECKPOINT_DIR / "jobmittr.db"


async def get_checkpointer() -> AsyncSqliteSaver:
    """Create and initialize async SQLite checkpointer.
    
    Returns:
        Configured AsyncSqliteSaver instance
    """
    checkpointer = AsyncSqliteSaver.from_conn_string(str(CHECKPOINT_DB))
    # Initialize database schema
    await checkpointer.setup()
    return checkpointer


def get_checkpointer_sync() -> AsyncSqliteSaver:
    """Synchronous wrapper for checkpointer initialization.
    
    Returns:
        Configured AsyncSqliteSaver instance
    """
    return asyncio.run(get_checkpointer())


async def cleanup_old_checkpoints(days_old: int = 30):
    """Remove checkpoints older than specified days.
    
    Args:
        days_old: Age threshold for deletion
    """
    checkpointer = await get_checkpointer()
    # LangGraph checkpointer handles automatic cleanup
    # This is a placeholder for future custom cleanup logic
    pass


# Thread ID generation utilities
def generate_interview_thread_id(job_title: str, user_id: str = "default") -> str:
    """Generate consistent thread ID for interview sessions.
    
    Args:
        job_title: Job position being interviewed for
        user_id: User identifier
        
    Returns:
        Formatted thread ID
    """
    safe_title = job_title.replace(" ", "_").lower()
    return f"interview_{user_id}_{safe_title}"


def generate_workflow_thread_id(workflow_type: str, user_id: str = "default") -> str:
    """Generate thread ID for general workflows.
    
    Args:
        workflow_type: Type of workflow (resume_analysis, job_search, etc.)
        user_id: User identifier
        
    Returns:
        Formatted thread ID
    """
    return f"workflow_{user_id}_{workflow_type}"


if __name__ == "__main__":
    # Test checkpointer initialization
    print("Testing Checkpointer Initialization")
    print("=" * 60)
    
    async def test_checkpointer():
        checkpointer = await get_checkpointer()
        print(f"✓ Checkpointer initialized: {type(checkpointer)}")
        print(f"✓ Database path: {CHECKPOINT_DB}")
        print(f"✓ Database exists: {CHECKPOINT_DB.exists()}")
        
        # Test thread ID generation
        thread_id = generate_interview_thread_id("Python Developer")
        print(f"✓ Generated thread ID: {thread_id}")
        
        return checkpointer
    
    asyncio.run(test_checkpointer())
    print("\n" + "=" * 60)
    print("Checkpointer setup complete!")