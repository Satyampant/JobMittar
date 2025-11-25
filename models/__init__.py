"""Pydantic models for type-safe data handling across the Job Search Assistant."""

from .resume import Resume, Education, WorkExperience, Skill
from .job import Job, JobRequirements, Company
from .interview import Interview, InterviewQuestion, InterviewResponse
from .skills import SkillCategory, SkillMatch, SkillGap

__all__ = [
    "Resume", "Education", "WorkExperience", "Skill",
    "Job", "JobRequirements", "Company",
    "Interview", "InterviewQuestion", "InterviewResponse",
    "SkillCategory", "SkillMatch", "SkillGap"
]
