# backend/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from Query_Handling import extract_drug_name
from download_pdfs import get_full_links
from pdf_to_markdown import to_markdown
from backend.markdown_to_chunks import markdown_to_chunks
from chunks_to_chromadb import create_drug_collection, get_embedding
from query_search import retrieve_relevant_chunks

import uuid


from database import create_session, get_session, add_message, list_sessions, delete_session, update_drug_name


class Message(BaseModel):
    role: str    # e.g., "user" or "assistant"
    content: str



class RetrieveChunksRequest(BaseModel):
    drug_name: str
    query: str


app = FastAPI()

# Allow CORS for your React app (adjust the origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FetchRequest(BaseModel):
    prompt: str
    session_id: str

class PdfSelectRequest(BaseModel):
    prompt: str
    storedPdfs: list  # list of PDF objects


@app.post("/api/session")
def create_sessions():
    """
    Create a new chat session and return its ID.
    """
    session_id = create_session()
    print("Created session:", session_id)
    return {"session_id": session_id}

@app.get("/api/session/{session_id}")
def get_session_endpoint(session_id: str):
    """
    Retrieve all messages in a given session.
    """
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    # Return only the messages array
    return {
        "messages": session.get("messages", []),
        "drug_name": session.get("drug_name", "")
    }



@app.post("/api/session/{session_id}/message")
def add_message_endpoint(session_id: str, message: Message):
    """
    Add a new message to a specific session.
    """
    success = add_message(session_id, message.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or message could not be added.")
    print("Updated session:", session_id)
    return {"status": "ok", "session_id": session_id}




@app.get("/api/sessions")
def list_sessions_endpoint():
    """
    Returns a list of all session IDs.
    """
    sessions = list_sessions()
    return {"sessions": sessions}

@app.delete("/api/session/{session_id}")
def delete_session_endpoint(session_id: str):
    """
    Deletes a session from MongoDB.
    """
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"status": "deleted", "session_id": session_id}

@app.post("/api/fetch-pdfs")
def fetch_pdfs(request: FetchRequest):
    print(request)
    prompt = request.prompt
    # Check if the prompt contains fetch keywords
    session_id = request.session_id
    if ("fetch the relevant document" in prompt.lower() or 
        "fetch documents" in prompt.lower()):
        drug_name = extract_drug_name(prompt)
        
        if drug_name:
            update_drug_name(session_id, drug_name)
            pdf_list = get_full_links(drug_name)
            return {
                "drug_name": drug_name,
                "pdf_list": pdf_list
            }
        else:
            raise HTTPException(status_code=400, detail="Could not extract a valid drug name.")
    else:
        raise HTTPException(status_code=400, detail="Prompt does not request document fetching.")

class PdfSelectResponse(BaseModel):
    markdown: str

@app.post("/api/select-pdf", response_model=PdfSelectResponse)
def select_pdf(request: PdfSelectRequest):
    prompt = request.prompt
    # Assume the prompt contains a PDF selection number at the end
    try:
        pdf_index = int(prompt.strip().split()[-1]) - 1
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PDF selection input.")

    # Retrieve pdf_list from the passed data
    pdf_list = request.storedPdfs
    if pdf_list is None or pdf_index < 0 or pdf_index >= len(pdf_list):
        raise HTTPException(status_code=400, detail="Invalid PDF selection.")

    selected_pdf = pdf_list[pdf_index]
    pdf_path = selected_pdf['path']
    md_content = to_markdown(pdf_path)
    return {"markdown": md_content}

# New Endpoint: Convert Markdown to Chunks
class MarkdownRequest(BaseModel):
    markdown: str

@app.post("/api/markdown-to-chunks")
def convert_markdown_to_chunks(request: MarkdownRequest):
    markdown = request.markdown
    header_list = markdown_to_chunks(markdown)
    if not header_list:
        raise HTTPException(status_code=400, detail="No chunks found in the markdown.")
    return {"header_list": header_list}

# New Endpoint: Store Chunks to ChromaDB
class StoreChunksRequest(BaseModel):
    drug_name: str
    header_list: dict

@app.post("/api/store-chunks")
def store_chunks(request: StoreChunksRequest):
    drug_name = request.drug_name
    header_list = request.header_list
    # Create or retrieve the collection for this drug
    collection = create_drug_collection(drug_name)
    id_counter = 0
    logs = []
    for key, values in header_list.items():
        for value in values:
            embedding = get_embedding(value)
            if embedding:
                logs.append(f"Adding '{value}' (Embedding: {embedding[:3]}...) to ChromaDB...")
                collection.add(
                    ids=[str(id_counter)],
                    documents=[value],
                    metadatas=[{"category": key}],
                    embeddings=[embedding]
                )
                id_counter += 1
            else:
                logs.append(f"Skipping '{value}' due to missing embedding.")
    # Retrieve the stored documents for confirmation
    stored = collection.get()
    return {"logs": logs, "stored": stored}


@app.post("/api/retrieve-chunks")
def retrieve_chunks(request: RetrieveChunksRequest):
    drug_name = request.drug_name.strip()  # sanitize the drug name
    query_text = request.query
    


    print("HERE IS THE DRUG NAME:   ", drug_name)
    # Get or create the collection for the given drug
    collection = create_drug_collection(drug_name)
    if collection is None:
        raise HTTPException(status_code=500, detail="Could not create or retrieve collection.")
    
    # Retrieve relevant chunks along with logs
    # relevant_chunks, logs = retrieve_relevant_chunks(query_text, collection)
    # return {"relevant_chunks": relevant_chunks, "logs": logs}

    final_response = retrieve_relevant_chunks(query_text, collection)
    return {"response": final_response}