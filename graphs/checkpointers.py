
import sys
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))


def get_checkpointer() -> MemorySaver:
    return MemorySaver()


def generate_interview_thread_id(job_title: str, user_id: str = "default") -> str:
    safe_title = job_title.replace(" ", "_").lower()
    return f"interview_{user_id}_{safe_title}"


def generate_workflow_thread_id(workflow_type: str, user_id: str = "default") -> str:
    return f"workflow_{user_id}_{workflow_type}"
