from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List
import shutil
import os
from .drive import upload_file_to_drive_folder  # We will implement this helper

router = APIRouter()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    db_name: str = Form(...)
):
    uploaded_files_info = []
    
    # Ensure local temp dir exists
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save temporarily locally (on Render container)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Upload to Google Drive (Implementation dependency)
        # We assume a specific folder structure in Drive: RAG_SYSTEM / <db_name> / raw_files
        try:
            drive_file_id = await upload_file_to_drive_folder(file_path, file.filename, db_name)
            uploaded_files_info.append({
                "filename": file.filename,
                "drive_id": drive_file_id,
                "local_path": file_path 
            })
        except Exception as e:
            print(f"Drive Upload Error: {e}")
            # Even if drive fails, we might want to queue it if worker can access local?
            # No, Render is remote. Must upload to Drive.
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to Drive: {str(e)}")
        finally:
            # Clean up local file to save space
            if os.path.exists(file_path):
                os.remove(file_path)
                
    return {"status": "success", "files": uploaded_files_info}

