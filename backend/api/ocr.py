from fastapi import APIRouter

router = APIRouter()

@router.get("/{db_name}/status")
def get_ocr_status(db_name: str):
    # Return status of OCR jobs for this DB
    return {"status": "idle", "processed_pages": 0, "total_pages": 0}

