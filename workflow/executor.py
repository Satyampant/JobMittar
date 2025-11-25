from datetime import datetime
from typing import Dict, Any, Optional
from workflows.graph import create_workflow
from workflows.state import JobSearchState, WorkflowStatus

class WorkflowExecutor:
    """Execute and manage LangGraph workflows with error recovery"""
    
    def __init__(self):
        self.graph = create_workflow()
    
    async def run_resume_analysis(self, resume_text: str, checkpoint_id: Optional[str] = None) -> JobSearchState:
        """Run resume parsing workflow with checkpointing"""
        config = {"configurable": {"thread_id": checkpoint_id or f"resume_{datetime.now().timestamp()}"}}
        state = {"resume_text": resume_text, "status": WorkflowStatus.PENDING, "timestamp": datetime.now()}
        result = await self.graph.ainvoke(state, config)
        return result
    
    async def run_job_search(self, state: JobSearchState, keywords: str, location: str, platforms: list) -> JobSearchState:
        """Run job search workflow from current state"""
        state.update({"search_keywords": keywords, "location": location, "platforms": platforms})
        config = {"configurable": {"thread_id": state.get("checkpoint_id", f"job_{datetime.now().timestamp()}")}}
        result = await self.graph.ainvoke(state, config)
        return result
    
    async def run_interview_prep(self, state: JobSearchState, selected_job: Dict[str, Any]) -> JobSearchState:
        """Run interview preparation workflow"""
        state["selected_job"] = selected_job
        config = {"configurable": {"thread_id": state.get("checkpoint_id", f"interview_{datetime.now().timestamp()}")}}
        result = await self.graph.ainvoke(state, config)
        return result
