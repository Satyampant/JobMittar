from typing import Dict, Any
from workflows.state import JobSearchState, WorkflowStatus
from models.resume_models import ResumeData
from models.job_models import JobListing

async def parse_resume_node(state: JobSearchState) -> Dict[str, Any]:
    """Parse resume text into structured data"""
    from utils.resume_parser import ResumeParser
    parser = ResumeParser()
    parsed = parser.parse_resume(state["resume_text"])
    return {"resume_parsed": parsed, "skills": parsed.get("skills", []), 
            "experience": parsed.get("experience", []), "status": WorkflowStatus.IN_PROGRESS}

async def search_jobs_node(state: JobSearchState) -> Dict[str, Any]:
    """Search for jobs based on resume and criteria"""
    from agents.job_search_agent import JobSearchAgent
    agent = JobSearchAgent()
    jobs = agent.search_jobs(state["resume_parsed"], state["search_keywords"], 
                            state["location"], state["platforms"])
    return {"jobs": jobs, "status": WorkflowStatus.IN_PROGRESS}

async def analyze_match_node(state: JobSearchState) -> Dict[str, Any]:
    """Analyze job match with resume"""
    from agents.job_search_agent import JobSearchAgent
    agent = JobSearchAgent()
    analysis = agent.get_job_match_analysis(state["resume_parsed"], state["selected_job"])
    return {"match_analysis": analysis}

async def generate_questions_node(state: JobSearchState) -> Dict[str, Any]:
    """Generate interview questions"""
    from agents.interview_agent import InterviewAgent
    agent = InterviewAgent()
    questions = agent.generate_interview_questions(state["selected_job"], state["resume_parsed"])
    return {"interview_questions": questions, "status": WorkflowStatus.COMPLETED}
