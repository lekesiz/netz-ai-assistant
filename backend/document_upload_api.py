"""
Document Upload API for AI Training
Allows users to upload documents through web interface
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from datetime import datetime
import PyPDF2
import docx
import pandas as pd
from pathlib import Path
import json
import hashlib

app = FastAPI(title="NETZ Document Upload API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
UPLOAD_DIR = Path("uploaded_documents")
PROCESSED_DIR = Path("processed_documents")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

class DocumentProcessor:
    """Process and extract content from documents"""
    
    @staticmethod
    def extract_pdf_content(file_path: Path) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = []
                for page in pdf_reader.pages:
                    content.append(page.extract_text())
                return "\n".join(content)
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    @staticmethod
    def extract_docx_content(file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    @staticmethod
    def extract_excel_content(file_path: Path) -> str:
        """Extract data from Excel"""
        try:
            df = pd.read_excel(file_path, sheet_name=None)
            content = []
            for sheet_name, data in df.items():
                content.append(f"\n=== Sheet: {sheet_name} ===")
                content.append(data.to_string())
            return "\n".join(content)
        except Exception as e:
            return f"Error reading Excel: {str(e)}"
    
    @staticmethod
    def extract_text_content(file_path: Path) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading text file: {str(e)}"

def get_file_hash(file_path: Path) -> str:
    """Generate hash for file deduplication"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def update_ai_memory(content: str, metadata: dict):
    """Update AI memory with new content"""
    try:
        # Store in simple_api.py knowledge base
        kb_file = Path("simple_api_kb.json")
        
        # Load existing knowledge base
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb = json.load(f)
        else:
            kb = {"documents": [], "last_updated": None}
        
        # Add new document
        kb["documents"].append({
            "content": content,
            "metadata": metadata,
            "hash": metadata["hash"],
            "timestamp": metadata["upload_time"]
        })
        
        # Remove duplicates based on hash
        seen = set()
        unique_docs = []
        for doc in kb["documents"]:
            if doc["hash"] not in seen:
                seen.add(doc["hash"])
                unique_docs.append(doc)
        
        kb["documents"] = unique_docs
        kb["last_updated"] = datetime.now().isoformat()
        
        # Save updated knowledge base
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
        
        # Restart simple_api.py to load new data
        os.system("pkill -f simple_api.py")
        os.system("python simple_api.py > simple_api.log 2>&1 &")
        
        return True
    except Exception as e:
        print(f"Error updating AI memory: {e}")
        return False

@app.post("/api/upload/document")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a single document"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file hash for deduplication
        file_hash = get_file_hash(file_path)
        
        # Extract content based on file type
        content = ""
        file_ext = file_path.suffix.lower()
        
        if file_ext == ".pdf":
            content = DocumentProcessor.extract_pdf_content(file_path)
        elif file_ext in [".docx", ".doc"]:
            content = DocumentProcessor.extract_docx_content(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            content = DocumentProcessor.extract_excel_content(file_path)
        elif file_ext in [".txt", ".csv"]:
            content = DocumentProcessor.extract_text_content(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Create metadata
        metadata = {
            "filename": file.filename,
            "file_type": file_ext,
            "file_size": file_path.stat().st_size,
            "upload_time": datetime.now().isoformat(),
            "hash": file_hash,
            "content_length": len(content),
            "status": "processed"
        }
        
        # Update AI memory
        success = update_ai_memory(content, metadata)
        
        if success:
            # Move to processed folder
            processed_path = PROCESSED_DIR / f"{file_hash}_{file.filename}"
            shutil.move(str(file_path), str(processed_path))
            
            return {
                "status": "success",
                "message": "Document uploaded and AI memory updated",
                "metadata": metadata,
                "content_preview": content[:500] + "..." if len(content) > 500 else content
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update AI memory")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/multiple")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    """Upload multiple documents at once"""
    results = []
    for file in files:
        try:
            result = await upload_document(file)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results, "total": len(files)}

@app.get("/api/documents/list")
async def list_documents():
    """List all processed documents"""
    kb_file = Path("simple_api_kb.json")
    
    if not kb_file.exists():
        return {"documents": [], "total": 0}
    
    with open(kb_file, 'r', encoding='utf-8') as f:
        kb = json.load(f)
    
    documents = []
    for doc in kb.get("documents", []):
        documents.append({
            "filename": doc["metadata"]["filename"],
            "upload_time": doc["metadata"]["upload_time"],
            "file_type": doc["metadata"]["file_type"],
            "size": doc["metadata"]["file_size"],
            "hash": doc["hash"]
        })
    
    return {
        "documents": documents,
        "total": len(documents),
        "last_updated": kb.get("last_updated")
    }

@app.delete("/api/documents/{file_hash}")
async def delete_document(file_hash: str):
    """Delete a document from AI memory"""
    kb_file = Path("simple_api_kb.json")
    
    if not kb_file.exists():
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    with open(kb_file, 'r', encoding='utf-8') as f:
        kb = json.load(f)
    
    # Filter out the document
    original_count = len(kb["documents"])
    kb["documents"] = [doc for doc in kb["documents"] if doc["hash"] != file_hash]
    
    if len(kb["documents"]) == original_count:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Save updated knowledge base
    kb["last_updated"] = datetime.now().isoformat()
    with open(kb_file, 'w', encoding='utf-8') as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    
    # Restart simple_api.py
    os.system("pkill -f simple_api.py")
    os.system("python simple_api.py > simple_api.log 2>&1 &")
    
    return {"status": "success", "message": "Document deleted from AI memory"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "upload_dir": str(UPLOAD_DIR),
        "processed_dir": str(PROCESSED_DIR),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port for upload API