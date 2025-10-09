#!/usr/bin/env python3
"""
Deep scan Google Drive for all relevant documents
"""

import os
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid
import PyPDF2
import json

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("🔍 Deep Scanning Google Drive for NETZ Documents")
print("="*50)

drive_path = Path("/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Drive'ım")

def load_document(text, source, doc_type, metadata):
    """Load document into vector database"""
    try:
        if not text or len(text.strip()) < 50:
            return False
            
        vector = encoder.encode(text)
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "text": text[:5000],  # Limit text size
                        "metadata": metadata
                    }
                )
            ]
        )
        return True
    except Exception as e:
        return False

def extract_pdf_text(file_path):
    """Extract text from PDF files"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(min(5, len(pdf_reader.pages))):  # First 5 pages
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
    except:
        return None

# Search patterns for important files
important_patterns = [
    "*NETZ*",
    "*81834734600020*",  # SIRET
    "*818347346*",       # SIRET short
    "*facture*",
    "*devis*",
    "*formation*",
    "*client*",
    "*comptabilite*",
    "*finance*"
]

# File extensions to process
extensions = {
    'text': ['.txt', '.md', '.log'],
    'data': ['.json', '.csv'],
    'docs': ['.pdf']
}

documents_found = []
total_loaded = 0

print("\nSearching for documents...")

# Search using patterns
for pattern in important_patterns:
    print(f"\nSearching pattern: {pattern}")
    
    for file_path in drive_path.rglob(pattern):
        if file_path.is_file() and 'venv' not in str(file_path) and '.Trash' not in str(file_path):
            file_ext = file_path.suffix.lower()
            
            # Skip if already processed
            if str(file_path) in [d['path'] for d in documents_found]:
                continue
            
            content = None
            doc_type = None
            
            # Process based on extension
            if file_ext in extensions['text']:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    doc_type = 'text_document'
                except:
                    pass
                    
            elif file_ext in extensions['data']:
                try:
                    if file_ext == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        content = json.dumps(data, indent=2, ensure_ascii=False)[:3000]
                    else:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')[:3000]
                    doc_type = 'data_file'
                except:
                    pass
                    
            elif file_ext == '.pdf':
                content = extract_pdf_text(file_path)
                doc_type = 'pdf_document'
            
            # If content extracted, save it
            if content and len(content) > 100:
                doc_info = {
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'type': doc_type
                }
                documents_found.append(doc_info)
                
                # Load to vector DB
                metadata = {
                    "source": "google_drive",
                    "type": doc_type,
                    "file_name": file_path.name,
                    "file_path": str(file_path.relative_to(drive_path)),
                    "file_size": doc_info['size']
                }
                
                doc_text = f"Document: {file_path.name}\n\n{content[:3000]}"
                
                if load_document(doc_text, "google_drive", doc_type, metadata):
                    total_loaded += 1
                    print(f"   ✅ {file_path.name}")
                    
                if total_loaded >= 100:  # Limit to prevent overload
                    break
    
    if total_loaded >= 100:
        break

# Look for specific folders
print("\n\nChecking specific folders...")
specific_folders = [
    "NETZ-Entreprise",
    "ADMINISTRATIF",
    "COMPTABILITE", 
    "FACTURES",
    "DEVIS",
    "CLIENTS"
]

for folder in specific_folders:
    folder_path = drive_path / folder
    if folder_path.exists():
        print(f"\n📁 Found folder: {folder}")
        
        # List some files
        files = list(folder_path.iterdir())[:10]
        for f in files:
            if f.is_file():
                print(f"   - {f.name}")

print(f"\n\nSummary:")
print(f"Total documents found: {len(documents_found)}")
print(f"Documents loaded to AI: {total_loaded}")

# Save document list
with open('google_drive_documents.json', 'w', encoding='utf-8') as f:
    json.dump(documents_found, f, ensure_ascii=False, indent=2)

print("\nDocument list saved to: google_drive_documents.json")