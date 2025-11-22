from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import datetime
import json
import os

router = APIRouter()

# Persistent Queue File
QUEUE_FILE = "queue_db.json"

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_queue(queue_data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue_data, f)

class Job(BaseModel):
    id: str
    db: str
    files: List[str]
    status: str  # pending, processing, completed, failed
    created_at: str
    result: Optional[Dict[str, Any]] = None

class JobCreate(BaseModel):
    db: str
    files: List[str]

@router.get("/", response_model=Dict[str, List[Dict]])
def get_queue():
    queue = load_queue()
    print(f"DEBUG: Checking Queue. Count: {len(queue)}") # Log for debug
    return {"jobs": queue}

@router.post("/add", response_model=Job)
def add_job(job_in: JobCreate):
    queue = load_queue()
    new_job = {
        "id": str(uuid.uuid4()),
        "db": job_in.db,
        "files": job_in.files,
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat(),
        "result": None
    }
    queue.append(new_job)
    save_queue(queue)
    print(f"DEBUG: Added Job {new_job['id']} to queue.")
    return Job(**new_job)

@router.post("/update/{job_id}")
def update_job(job_id: str, status: str, result: Optional[Dict[str, Any]] = None):
    queue = load_queue()
    job_found = False
    updated_job = None
    
    for job in queue:
        if job["id"] == job_id:
            job["status"] = status
            if result:
                job["result"] = result
            job_found = True
            updated_job = job
            break
            
    if job_found:
        save_queue(queue)
        print(f"DEBUG: Updated Job {job_id} to {status}")
        return {"message": "Updated", "job": updated_job}
        
    raise HTTPException(status_code=404, detail="Job not found")

@router.get("/pending", response_model=List[Dict])
def get_pending_jobs():
    queue = load_queue()
    pending = [job for job in queue if job["status"] == "pending"]
    if pending:
        print(f"DEBUG: Returning {len(pending)} pending jobs to worker.")
    return pending
