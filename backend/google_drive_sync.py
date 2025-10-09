"""
Google Drive Sync Service
Syncs documents from Google Drive folder for RAG indexing
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging
from dataclasses import dataclass
import mimetypes

from rag_service import get_rag_service

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document metadata"""
    file_path: str
    content: str
    metadata: Dict[str, Any]
    doc_id: str
    
class GoogleDriveSync:
    """Handles syncing documents from Google Drive folder"""
    
    def __init__(self):
        self.drive_path = Path(os.getenv('GOOGLE_DRIVE_PATH', '/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Mon Drive'))
        self.supported_extensions = {
            '.txt', '.md', '.json', '.csv'  # Only text files for now
        }
        self.indexed_files = self._load_index()
        self.max_files = 10  # Limit to 10 files for performance
        
    def _load_index(self) -> Dict[str, str]:
        """Load index of previously processed files"""
        index_file = Path("data/google_drive_index.json")
        if index_file.exists():
            with open(index_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_index(self):
        """Save index of processed files"""
        index_file = Path("data/google_drive_index.json")
        index_file.parent.mkdir(exist_ok=True)
        with open(index_file, 'w') as f:
            json.dump(self.indexed_files, f, indent=2)
            
    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file for change detection"""
        stat = file_path.stat()
        hash_input = f"{file_path}:{stat.st_size}:{stat.st_mtime}".encode()
        return hashlib.md5(hash_input).hexdigest()
        
    def _extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        extension = file_path.suffix.lower()
        
        try:
            if extension in ['.txt', '.md']:
                return file_path.read_text(encoding='utf-8', errors='ignore')
                
            elif extension == '.json':
                data = json.loads(file_path.read_text())
                return json.dumps(data, indent=2, ensure_ascii=False)
                
            elif extension in ['.html', '.xml']:
                # Simple text extraction
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                # Remove basic tags
                import re
                return re.sub('<[^<]+?>', '', content)
                
            elif extension == '.csv':
                lines = file_path.read_text(encoding='utf-8', errors='ignore').split('\n')
                return '\n'.join(lines[:1000])  # Limit to first 1000 lines
                
            elif extension == '.pdf':
                # For now, skip PDFs (would need PyPDF2 or similar)
                logger.info(f"Skipping PDF file: {file_path}")
                return ""
                
            elif extension in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                # For now, skip Office files (would need python-docx, openpyxl, etc.)
                logger.info(f"Skipping Office file: {file_path}")
                return ""
                
            else:
                # Try to read as text
                return file_path.read_text(encoding='utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
            
    def _create_document(self, file_path: Path) -> Document:
        """Create document object from file"""
        relative_path = file_path.relative_to(self.drive_path)
        
        # Extract text content
        content = self._extract_text(file_path)
        if not content:
            return None
            
        # Create metadata
        stat = file_path.stat()
        metadata = {
            "source": "google_drive",
            "file_path": str(relative_path),
            "file_name": file_path.name,
            "file_type": file_path.suffix,
            "size_bytes": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "mime_type": mimetypes.guess_type(str(file_path))[0],
            "sync_time": datetime.utcnow().isoformat()
        }
        
        # Generate document ID
        doc_id = f"gdrive_{hashlib.md5(str(relative_path).encode()).hexdigest()}"
        
        return Document(
            file_path=str(file_path),
            content=content,
            metadata=metadata,
            doc_id=doc_id
        )
        
    def scan_documents(self) -> List[Document]:
        """Scan Google Drive folder for documents"""
        documents = []
        
        if not self.drive_path.exists():
            logger.error(f"Google Drive path does not exist: {self.drive_path}")
            return documents
            
        logger.info(f"Scanning Google Drive folder: {self.drive_path}")
        
        file_count = 0
        # Walk through directory
        for file_path in self.drive_path.rglob('*'):
            if file_count >= self.max_files:
                logger.info(f"Reached max file limit ({self.max_files})")
                break
                
            if not file_path.is_file():
                continue
                
            # Skip hidden files and system files
            if file_path.name.startswith('.') or file_path.name.startswith('~'):
                continue
                
            # Check if file type is supported
            if file_path.suffix.lower() not in self.supported_extensions:
                continue
                
            # Check if file has changed
            file_hash = self._get_file_hash(file_path)
            if str(file_path) in self.indexed_files and self.indexed_files[str(file_path)] == file_hash:
                logger.debug(f"Skipping unchanged file: {file_path}")
                continue
                
            # Create document
            doc = self._create_document(file_path)
            if doc:
                documents.append(doc)
                self.indexed_files[str(file_path)] = file_hash
                logger.info(f"Found document: {file_path.name}")
                file_count += 1
                
        self._save_index()
        logger.info(f"Found {len(documents)} new/changed documents")
        return documents
        
    def sync_to_rag(self) -> Dict[str, Any]:
        """Sync documents to RAG system"""
        try:
            # Get RAG service
            rag = get_rag_service()
            if not rag:
                return {"status": "error", "message": "RAG service not initialized"}
                
            # Scan for documents
            documents = self.scan_documents()
            if not documents:
                return {
                    "status": "success",
                    "message": "No new documents to sync",
                    "documents_processed": 0
                }
                
            # Process documents
            processed = 0
            errors = []
            
            for doc in documents:
                try:
                    # Add to RAG
                    rag.add_document(
                        text=doc.content,
                        metadata=doc.metadata,
                        doc_id=doc.doc_id
                    )
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {doc.file_path}: {str(e)}")
                    errors.append({
                        "file": doc.metadata['file_name'],
                        "error": str(e)
                    })
                    
            # Build index
            logger.info("Building vector index...")
            rag.build_index()
            
            return {
                "status": "success",
                "message": f"Synced {processed} documents",
                "documents_processed": processed,
                "total_documents": len(documents),
                "errors": errors,
                "sync_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Google Drive sync error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "documents_processed": 0
            }

# Singleton instance
_sync_instance = None

def get_google_drive_sync() -> GoogleDriveSync:
    """Get Google Drive sync instance"""
    global _sync_instance
    if _sync_instance is None:
        _sync_instance = GoogleDriveSync()
    return _sync_instance