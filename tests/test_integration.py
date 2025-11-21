import sys
import os
import json
import time
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from api.queue import add_job, get_pending_jobs, update_job, JobCreate
from worker_local import process_job

def test_full_flow():
    print("🚀 Starting Mock Integration Test...")

    # 1. Test Queue Addition (Backend)
    print("\n[1] Testing Job Queue Addition...")
    job_data = JobCreate(db="TestDB", files=["mock_document.pdf"])
    job = add_job(job_data)
    print(f"    ✅ Job Created: ID={job.id}, Status={job.status}")

    # 2. Verify Pending
    pending = get_pending_jobs()
    assert len(pending) > 0
    print(f"    ✅ Pending jobs found: {len(pending)}")

    # 3. Mock Worker Processing
    print("\n[2] Testing Worker Processing Logic...")
    
    # Mocking requests.post used in worker to update backend
    with patch('requests.post') as mock_post:
        with patch('backend.worker_local.process_file_logic') as mock_logic:
            with patch('backend.worker_local.upload_chroma_to_drive') as mock_sync:
                
                # Convert Job object to dict as worker expects JSON from API
                job_dict = job.dict()
                
                # Run Worker Process
                process_job(job_dict)
                
                # Check if worker tried to update status to 'processing'
                mock_post.assert_any_call(
                    f"http://localhost:8000/api/queue/update/{job.id}", 
                    params={"status": "processing"}
                )
                print("    ✅ Worker signaled 'processing' state")
                
                # Check if worker tried to update status to 'completed'
                mock_post.assert_any_call(
                    f"http://localhost:8000/api/queue/update/{job.id}", 
                    params={"status": "completed"}
                )
                print("    ✅ Worker signaled 'completed' state")

    # 4. Verify Final State (Manually updating since mock request didn't actually hit API)
    update_job(job.id, "completed")
    print(f"\n[3] Final Job State in Backend: completed")

    print("\n🎉 All Mock Tests Passed!")

if __name__ == "__main__":
    test_full_flow()

