from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import time
import asyncio
import json

# Try importing Pinecone and OpenAI
try:
    from pinecone import Pinecone
    import openai
except ImportError:
    pass

router = APIRouter()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "rag-system-index"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class ChatMessage(BaseModel):
    role: str 
    content: str

class QueryRequest(BaseModel):
    db_name: str
    messages: List[ChatMessage]
    llm_provider: str 
    llm_model: str

async def generate_stream_mock(query: str):
    msg = "API Key eksik. Lütfen backend ortam değişkenlerini (OPENAI_API_KEY veya OPENROUTER_API_KEY) kontrol edin."
    yield f"data: {msg}\n\n"
    yield "data: [DONE]\n\n"

async def generate_llm_response(context_text: str, context_sources: List[Dict], history: List[ChatMessage], provider="openai", model="gpt-4"):
    """
    Streams response from OpenAI or OpenRouter based on provider.
    """
    
    # 1. Configure Client based on Provider
    api_key = None
    base_url = None
    
    if provider == "openrouter":
        api_key = OPENROUTER_API_KEY
        base_url = "https://openrouter.ai/api/v1"
    else:
        # Default to OpenAI
        api_key = OPENAI_API_KEY
        base_url = None # Default OpenAI URL

    if not api_key:
        yield f"data: Error: Missing API Key for {provider}.\n\n"
        yield "data: [DONE]\n\n"
        return

    client = openai.AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    system_prompt = f"""You are a helpful RAG assistant. 
    Answer the user's question using ONLY the context below.
    If the answer is not in the context, say "I couldn't find this information in the documents."
    
    CONTEXT:
    {context_text}
    """

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        # Extra headers for OpenRouter to identify the app
        extra_headers = {}
        if provider == "openrouter":
            extra_headers = {
                "HTTP-Referer": "https://rag-system.local", # Required by OpenRouter
                "X-Title": "RAG System"
            }

        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            extra_headers=extra_headers
        )
        
        # Stream the answer content
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                # Clean newlines for SSE data safety
                safe_content = content.replace("\n", "\\n")
                yield f"data: {safe_content}\n\n"
        
        # Append Citations
        if context_sources:
            yield f"data: \\n\\n---\\n**Kaynaklar:**\\n\n\n"
            seen = set()
            for src in context_sources:
                ref = f"• {src['source']} (Sayfa {src.get('page', '?')})"
                if ref not in seen:
                    yield f"data: {ref}\\n\n\n"
                    seen.add(ref)

    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
        
    yield "data: [DONE]\n\n"

def get_context_from_pinecone(query: str, db_name: str):
    """
    Retrieves relevant chunks using OpenAI Embeddings + Pinecone
    """
    # Note: Embedding always uses OpenAI for consistency/quality, 
    # even if Chat uses OpenRouter. 
    # If you want to use OpenRouter for embedding too, you'd need a model that supports it there.
    # For now, we stick to OpenAI for embeddings as it's the most stable for RAG.
    
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        return "", []
        
    try:
        # 1. Generate Embedding (Must match Worker's model: text-embedding-3-small)
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        emb_response = client.embeddings.create(
            input=query, 
            model="text-embedding-3-small"
        )
        query_vector = emb_response.data[0].embedding

        # 2. Query Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        results = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            filter={"db_name": db_name}
        )
        
        context_text = ""
        sources = []
        
        for match in results.matches:
            if match.score > 0.70: 
                meta = match.metadata
                context_text += f"---\nContent: {meta.get('text', '')}\nSource: {meta.get('source', '')}\n"
                sources.append({"source": meta.get('source'), "page": meta.get('page')})
                
        return context_text, sources

    except Exception as e:
        print(f"RAG Error: {e}")
        return "", []

@router.post("/chat")
async def chat_rag(request: QueryRequest):
    # 1. Embed Query & Search Pinecone
    last_user_msg = request.messages[-1].content
    context_text, context_sources = get_context_from_pinecone(last_user_msg, request.db_name)
    
    # 2. Stream Response
    return StreamingResponse(
        generate_llm_response(
            context_text, 
            context_sources, 
            request.messages, 
            provider=request.llm_provider, 
            model=request.llm_model
        ), 
        media_type="text/event-stream"
    )
