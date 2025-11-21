from fastapi import APIRouter

router = APIRouter()

@router.get("/{db_name}")
def list_extracted_images(db_name: str):
    # In a real app, this would query a DB or list files in a specific Drive folder
    return {
        "images": [
            {"id": "1", "name": f"{db_name}_page001_img001.jpg", "url": "http://placehold.it/200x200"}
        ]
    }

@router.post("/{db_name}/rename")
def rename_image(db_name: str, old_name: str, new_name: str):
    return {"status": "renamed", "old": old_name, "new": new_name}

