from fastapi import APIRouter

router = APIRouter()

@router.get("/{db_name}")
def list_tables(db_name: str):
    return {
        "tables": []
    }

