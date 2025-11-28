"""Compiled graph factories with checkpointing enabled.

This module provides production-ready compiled graphs with persistence.
"""

import asyncio
from typing import Optional
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graphs.resume_subgraph import create_resume_subgraph
from graphs.job_subgraph import create_job_subgraph
from graphs.interview_subgraph import create_interview_subgraph
from graphs.checkpointers import get_checkpointer


async def compile_resume_graph_with_checkpoint(
    checkpointer: Optional[AsyncSqliteSaver] = None
):
    """Compile resume processing graph with checkpointing.
    
    Args:
        checkpointer: Optional custom checkpointer instance
        
    Returns:
        Compiled graph with persistence
    """
    if checkpointer is None:
        checkpointer = await get_checkpointer()
    
    graph = create_resume_subgraph()
    return graph.compile(checkpointer=checkpointer)


async def compile_job_graph_with_checkpoint(
    checkpointer: Optional[AsyncSqliteSaver] = None
):
    """Compile job search graph with checkpointing.
    
    Args:
        checkpointer: Optional custom checkpointer instance
        
    Returns:
        Compiled graph with persistence
    """
    if checkpointer is None:
        checkpointer = await get_checkpointer()
    
    graph = create_job_subgraph()
    return graph.compile(checkpointer=checkpointer)


async def compile_interview_graph_with_checkpoint(
    checkpointer: Optional[AsyncSqliteSaver] = None
):
    """Compile interview preparation graph with checkpointing.
    
    Args:
        checkpointer: Optional custom checkpointer instance
        
    Returns:
        Compiled graph with persistence
    """
    if checkpointer is None:
        checkpointer = await get_checkpointer()
    
    graph = create_interview_subgraph()
    return graph.compile(checkpointer=checkpointer)


def compile_resume_graph_sync():
    """Synchronous wrapper for resume graph compilation."""
    return asyncio.run(compile_resume_graph_with_checkpoint())


def compile_job_graph_sync():
    """Synchronous wrapper for job graph compilation."""
    return asyncio.run(compile_job_graph_with_checkpoint())


def compile_interview_graph_sync():
    """Synchronous wrapper for interview graph compilation."""
    return asyncio.run(compile_interview_graph_with_checkpoint())


if __name__ == "__main__":
    # Test graph compilation with checkpointing
    print("Testing Graph Compilation with Checkpointing")
    print("=" * 60)
    
    async def test_compilation():
        # Test resume graph
        resume_graph = await compile_resume_graph_with_checkpoint()
        print(f"✓ Resume graph compiled: {resume_graph is not None}")
        
        # Test job graph
        job_graph = await compile_job_graph_with_checkpoint()
        print(f"✓ Job graph compiled: {job_graph is not None}")
        
        # Test interview graph
        interview_graph = await compile_interview_graph_with_checkpoint()
        print(f"✓ Interview graph compiled: {interview_graph is not None}")
        
        return resume_graph, job_graph, interview_graph
    
    graphs = asyncio.run(test_compilation())
    print("\n" + "=" * 60)
    print("All graphs compiled successfully with checkpointing!")