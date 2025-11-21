from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

DATABASES = ["DefaultDB"]

class DBCreate(BaseModel):
    name: str

@router.get("/", response_model=List[str])
def list_dbs():
    return DATABASES

@router.post("/create")
def create_db(db: DBCreate):
    if db.name in DATABASES:
        raise HTTPException(status_code=400, detail="Database already exists")
    DATABASES.append(db.name)
    # Trigger creation of folder in Drive via Queue or direct drive call
    return {"status": "created", "name": db.name}

# Helper to sync DB (used by llm.py)
async def sync_db_from_drive(db_name: str):
    print(f"Syncing {db_name} from Drive...")
    # Logic: Download ChromaDB folder zip from Drive, unzip to /tmp/chroma_db
    pass

