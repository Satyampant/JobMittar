
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
    if checkpointer is None:
        checkpointer = await get_checkpointer()
    
    graph = create_resume_subgraph()
    return graph.compile(checkpointer=checkpointer)


async def compile_job_graph_with_checkpoint(checkpointer: Optional[AsyncSqliteSaver] = None):
    if checkpointer is None:
        checkpointer = await get_checkpointer()
    
    graph = create_job_subgraph()
    return graph.compile(checkpointer=checkpointer)


async def compile_interview_graph_with_checkpoint(checkpointer: Optional[AsyncSqliteSaver] = None):
    if checkpointer is None:
        checkpointer = await get_checkpointer()
    
    graph = create_interview_subgraph()
    return graph.compile(checkpointer=checkpointer)


def compile_resume_graph_sync():
    return asyncio.run(compile_resume_graph_with_checkpoint())


def compile_job_graph_sync():
    return asyncio.run(compile_job_graph_with_checkpoint())


def compile_interview_graph_sync():
    return asyncio.run(compile_interview_graph_with_checkpoint())

