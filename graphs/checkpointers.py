"""LangGraph checkpointing configuration for persistent state management."""

import asyncio
from pathlib import Path
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
    # Create checkpointer from connection string
    checkpointer_context = AsyncSqliteSaver.from_conn_string(str(CHECKPOINT_DB))
    
    # Enter the async context manager to get the actual checkpointer
    checkpointer = await checkpointer_context.__aenter__()
    
    # Setup database schema
    await checkpointer.setup()
    
    return checkpointer


def get_checkpointer_sync() -> AsyncSqliteSaver:
    """Synchronous wrapper for checkpointer initialization.
    
    Returns:
        Configured AsyncSqliteSaver instance
    """
    return asyncio.run(get_checkpointer())


# Thread ID generation utilities
def generate_interview_thread_id(job_title: str, user_id: str = "default") -> str:
    """Generate consistent thread ID for interview sessions."""
    safe_title = job_title.replace(" ", "_").lower()
    return f"interview_{user_id}_{safe_title}"


def generate_workflow_thread_id(workflow_type: str, user_id: str = "default") -> str:
    """Generate thread ID for general workflows."""
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