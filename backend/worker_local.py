import time
import requests
import json
import os
import platform
from typing import List, Dict
import shutil
import sys

# Library imports
try:
    import pdfplumber
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    from paddleocr import PaddleOCR
    import camelot
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    from pinecone import Pinecone, ServerlessSpec
    from openai import OpenAI 
except ImportError as e:
    print(f"Warning: Missing dependency {e}. Please install requirements.txt")

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_INDEX_NAME = "rag-system-index"
LOCAL_STORAGE_PATH = "./local_storage"

# Ensure directories
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

def log(msg):
    print(f"[{time.strftime('%X')}] [Worker] {msg}")

# --- Drive Helpers ---
def get_drive():
    # Drive auth logic (Skipped for brevity as we focus on Pinecone)
    pass

# --- Pinecone Helper ---
def get_pinecone_index():
    if not PINECONE_API_KEY:
        log("❌ ERROR: PINECONE_API_KEY missing.")
        return None
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        log(f"Creating Pinecone Index: {PINECONE_INDEX_NAME}")
        try:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536, 
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            time.sleep(10) # Wait for init
        except Exception as e:
            log(f"Index creation error: {e}")
            
    return pc.Index(PINECONE_INDEX_NAME)

# --- Processing Logic ---

def perform_ocr(image_path, lang='en'):
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
        result = ocr.ocr(image_path, cls=True)
        if not result or not result[0]: return ""
        text = "\n".join([line[1][0] for line in result[0]])
        return text
    except:
        return pytesseract.image_to_string(Image.open(image_path))

def extract_images_from_pdf(pdf_path, db_name):
    try:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images):
            img_name = f"{db_name}_page{i+1:03d}_img001.jpg" 
            save_path = os.path.join(LOCAL_STORAGE_PATH, "images", img_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            img.save(save_path, "JPEG")
    except Exception as e:
        log(f"Image extraction error: {e}")

def get_openai_embeddings(texts: List[str]):
    if not OPENAI_API_KEY:
        log("❌ OPENAI_API_KEY missing. Cannot embed.")
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(input=texts, model="text-embedding-3-small")
        return [data.embedding for data in response.data]
    except Exception as e:
        log(f"Embedding Error: {e}")
        return None

def process_file_logic(db_name, file_path, filename):
    log(f"Processing {filename}...")
    full_text = ""
    
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text: full_text += text + "\n"
        extract_images_from_pdf(file_path, db_name)
    elif ext in ['jpg', 'png', 'jpeg']:
        full_text = perform_ocr(file_path)
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

    if not full_text.strip():
        log("⚠️ No text extracted. Skipping embedding.")
        return

    chunk_size = 800 
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
    
    log(f"Generating Embeddings for {len(chunks)} chunks...")
    embeddings = get_openai_embeddings(chunks)
    
    if not embeddings: return

    index = get_pinecone_index()
    if not index: return

    vectors = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{db_name}_{filename}_{i}",
            "values": emb,
            "metadata": {
                "text": chunk,
                "source": filename,
                "db_name": db_name,
                "page": i
            }
        })
        
    batch_size = 50
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        
    log(f"✅ Finished processing {filename}.")

# --- Main Loop ---

def fetch_job():
    url = f"{BACKEND_URL}/api/queue/pending"
    try:
        # log(f"Checking queue at: {url}") # Verbose log
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            jobs = resp.json()
            if jobs: return jobs[0]
    except Exception as e:
        log(f"Connection Error: {e}")
    return None

def main():
    log(f"🚀 Worker started. Connecting to: {BACKEND_URL}")
    log("Waiting for jobs...")
    
    if not PINECONE_API_KEY: log("⚠️ PINECONE_API_KEY missing!")
    if not OPENAI_API_KEY: log("⚠️ OPENAI_API_KEY missing!")

    while True:
        job = fetch_job()
        if job:
            log(f"📥 Received Job: {job['id']} (DB: {job['db']})")
            requests.post(f"{BACKEND_URL}/api/queue/update/{job['id']}", params={"status": "processing"})
            
            try:
                files = job['files']
                for f in files:
                    local_f_path = os.path.join(LOCAL_STORAGE_PATH, f)
                    # In a real scenario, we would download the file from Drive here.
                    # For now, we assume it's uploaded or we create a dummy if testing.
                    if not os.path.exists(local_f_path):
                        log(f"File {f} not found locally. Creating dummy content for testing.")
                        with open(local_f_path, 'w') as df: df.write("Dummy content for RAG testing.")
                        
                    process_file_logic(job['db'], local_f_path, f)
                
                requests.post(f"{BACKEND_URL}/api/queue/update/{job['id']}", params={"status": "completed"})
                log(f"Job {job['id']} Completed! ✅")
            except Exception as e:
                log(f"Error processing job: {e}")
                requests.post(f"{BACKEND_URL}/api/queue/update/{job['id']}", params={"status": "failed", "result": str(e)})
        
        time.sleep(5)

if __name__ == "__main__":
    main()
