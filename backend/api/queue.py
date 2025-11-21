from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import datetime

router = APIRouter()

# In-memory queue storage (In production, use Redis or a DB)
# Since Render spins down, this is ephemeral. 
# The Local Worker will sync status updates here.
JOB_QUEUE = []

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

@router.get("/", response_model=Dict[str, List[Job]])
def get_queue():
    return {"jobs": JOB_QUEUE}

@router.post("/add", response_model=Job)
def add_job(job_in: JobCreate):
    new_job = Job(
        id=str(uuid.uuid4()),
        db=job_in.db,
        files=job_in.files,
        status="pending",
        created_at=datetime.datetime.now().isoformat()
    )
    JOB_QUEUE.append(new_job)
    return new_job

@router.post("/update/{job_id}")
def update_job(job_id: str, status: str, result: Optional[Dict[str, Any]] = None):
    for job in JOB_QUEUE:
        if job.id == job_id:
            job.status = status
            if result:
                job.result = result
            return {"message": "Updated", "job": job}
    raise HTTPException(status_code=404, detail="Job not found")

@router.get("/pending", response_model=List[Job])
def get_pending_jobs():
    return [job for job in JOB_QUEUE if job.status == "pending"]

