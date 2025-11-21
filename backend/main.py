from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import files, ocr, images, tables, embeddings, queue, llm, drive, db
import os

app = FastAPI(title="RAG System Backend")

# CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(queue.router, prefix="/api/queue", tags=["Queue"])
app.include_router(llm.router, prefix="/api/query", tags=["Query"])
app.include_router(db.router, prefix="/api/db", tags=["Database"])
app.include_router(drive.router, prefix="/api/drive", tags=["Drive"])

@app.get("/")
def read_root():
    return {"status": "online", "system": "RAG-1 Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

