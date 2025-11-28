
import os
import json
from datetime import datetime
from typing import Dict, Any, List


os.makedirs("saved_jobs", exist_ok=True)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


def save_job_to_local(job_data: Dict[str, Any]) -> str:
    job_id = f"{job_data.get('title', 'job').replace(' ', '_')}_{job_data.get('company', 'company').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    file_path = os.path.join("saved_jobs", f"{job_id}.json")

    job_data["date_saved"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    job_data_copy = job_data.copy()

    for key, value in job_data_copy.items():
        if isinstance(value, datetime):
            job_data_copy[key] = value.strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(job_data_copy, f, indent=4, cls=DateTimeEncoder)

    return file_path


def load_saved_jobs() -> List[Dict[str, Any]]:
    """Load all saved jobs from local storage.

    Returns:
        list: List of job dictionaries
    """
    saved_jobs = []

    if not os.path.exists("saved_jobs"):
        return saved_jobs

    for file_name in os.listdir("saved_jobs"):
        if file_name.endswith(".json"):
            file_path = os.path.join("saved_jobs", file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)
                    saved_jobs.append(job_data)
            except Exception as e:
                print(f"Error loading job file {file_name}: {e}")

    return saved_jobs


def remove_saved_job(job_title: str, job_company: str) -> bool:
    
    for file_name in os.listdir("saved_jobs"):
        if file_name.endswith(".json"):
            file_path = os.path.join("saved_jobs", file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    job_data = json.load(f)

                if job_data.get("title") == job_title and job_data.get("company") == job_company:
                    os.remove(file_path)
                    return True
            except Exception as e:
                print(f"Error processing job file {file_name}: {e}")

    return False
