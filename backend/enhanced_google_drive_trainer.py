#!/usr/bin/env python3
"""
Enhanced Google Drive AI Training System for NETZ
Processes real Google Drive documents and trains AI with comprehensive NETZ knowledge
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass
import hashlib
import mimetypes

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logging.warning("Google API client not available. Install with: pip install google-api-python-client google-auth")

from lightweight_rag import LightweightRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedDocument:
    """Represents a processed document from Google Drive"""
    id: str
    name: str
    mime_type: str
    content: str
    metadata: Dict[str, Any]
    source_path: str
    chunks: List[str]

class EnhancedGoogleDriveTrainer:
    """Enhanced Google Drive document processor and AI trainer"""
    
    def __init__(self):
        self.rag = LightweightRAG()
        self.google_drive_service = None
        self.processed_documents = []
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        
        # NETZ-specific document types to prioritize
        self.priority_files = [
            'tarifs', 'prix', 'pricing', 'guide', 'formation', 'training',
            'service', 'contact', 'procedure', 'manuel', 'documentation'
        ]
        
        # Initialize Google Drive API
        self._initialize_google_api()
    
    def _initialize_google_api(self):
        """Initialize Google Drive API connection"""
        if not GOOGLE_API_AVAILABLE:
            logger.warning("📵 Google API not available. Using simulation mode.")
            return
        
        try:
            creds = None
            token_path = 'google_drive_token.json'
            credentials_path = 'google_drive_credentials.json'
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.scopes)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists(credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                else:
                    logger.warning("🔑 No Google Drive credentials found. Please add google_drive_credentials.json")
                    return
                
                # Save token for next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.google_drive_service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive API initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Drive API: {str(e)}")
            self.google_drive_service = None
    
    async def discover_netz_folders(self) -> List[Dict]:
        """Discover NETZ-related folders in Google Drive"""
        if not self.google_drive_service:
            return []
        
        try:
            # Search for folders containing 'NETZ' or similar
            search_terms = ['NETZ', 'netz', 'Informatique', 'Documents']
            found_folders = []
            
            for term in search_terms:
                query = f"name contains '{term}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.google_drive_service.files().list(
                    q=query,
                    fields="files(id, name, parents)",
                    pageSize=50
                ).execute()
                
                folders = results.get('files', [])
                for folder in folders:
                    if folder not in found_folders:
                        found_folders.append(folder)
                        logger.info(f"📁 Found folder: {folder['name']} (ID: {folder['id']})")
            
            return found_folders
            
        except Exception as e:
            logger.error(f"❌ Error discovering folders: {str(e)}")
            return []
    
    async def process_folder_contents(self, folder_id: str, folder_name: str) -> Dict[str, Any]:
        """Process all documents in a Google Drive folder"""
        logger.info(f"📂 Processing folder: {folder_name}")
        
        try:
            # Get all files in folder
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.google_drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, parents)",
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"📄 Found {len(files)} files in {folder_name}")
            
            processed_count = 0
            skipped_count = 0
            
            for file_info in files:
                try:
                    if await self._process_single_file(file_info, folder_name):
                        processed_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    logger.error(f"❌ Error processing {file_info['name']}: {str(e)}")
                    skipped_count += 1
            
            return {
                "folder_name": folder_name,
                "total_files": len(files),
                "processed": processed_count,
                "skipped": skipped_count,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing folder {folder_name}: {str(e)}")
            return {
                "folder_name": folder_name,
                "success": False,
                "error": str(e)
            }
    
    async def _process_single_file(self, file_info: Dict, folder_name: str) -> bool:
        """Process a single file from Google Drive"""
        try:
            file_id = file_info['id']
            file_name = file_info['name']
            mime_type = file_info['mimeType']
            
            # Check if file is relevant to NETZ
            if not self._is_netz_relevant(file_name):
                logger.info(f"⏭️ Skipping non-NETZ file: {file_name}")
                return False
            
            logger.info(f"📄 Processing: {file_name} ({mime_type})")
            
            # Extract content based on file type
            content = await self._extract_file_content(file_id, file_name, mime_type)
            
            if not content or len(content.strip()) < 100:
                logger.warning(f"⚠️ Insufficient content in: {file_name}")
                return False
            
            # Create processed document
            doc = ProcessedDocument(
                id=file_id,
                name=file_name,
                mime_type=mime_type,
                content=content,
                metadata={
                    "source": "google_drive",
                    "folder": folder_name,
                    "file_size": file_info.get('size', 0),
                    "modified_time": file_info.get('modifiedTime'),
                    "processed_time": datetime.now().isoformat(),
                    "priority": self._get_file_priority(file_name),
                    "content_hash": hashlib.md5(content.encode()).hexdigest()[:8]
                },
                source_path=f"/{folder_name}/{file_name}",
                chunks=self._create_content_chunks(content)
            )
            
            self.processed_documents.append(doc)
            logger.info(f"✅ Processed: {file_name} ({len(content)} chars, {len(doc.chunks)} chunks)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing file {file_info.get('name', 'unknown')}: {str(e)}")
            return False
    
    async def _extract_file_content(self, file_id: str, file_name: str, mime_type: str) -> str:
        """Extract content from different file types"""
        try:
            if mime_type == 'application/vnd.google-apps.document':
                # Google Docs - export as plain text
                content = self.google_drive_service.files().export(
                    fileId=file_id, mimeType='text/plain'
                ).execute()
                return content.decode('utf-8')
            
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                # Google Sheets - export as CSV
                content = self.google_drive_service.files().export(
                    fileId=file_id, mimeType='text/csv'
                ).execute()
                return content.decode('utf-8')
            
            elif mime_type == 'application/vnd.google-apps.presentation':
                # Google Slides - export as plain text
                content = self.google_drive_service.files().export(
                    fileId=file_id, mimeType='text/plain'
                ).execute()
                return content.decode('utf-8')
            
            elif mime_type.startswith('text/') or mime_type == 'application/json':
                # Text files, JSON, etc.
                content = self.google_drive_service.files().get_media(fileId=file_id).execute()
                return content.decode('utf-8', errors='ignore')
            
            elif mime_type == 'application/pdf':
                # PDF files - would need PyPDF2 or similar
                logger.info(f"📕 PDF file detected: {file_name} (PDF processing not implemented)")
                return f"PDF Document: {file_name}"
            
            else:
                logger.info(f"❓ Unsupported file type: {mime_type}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error extracting content from {file_name}: {str(e)}")
            return ""
    
    def _is_netz_relevant(self, filename: str) -> bool:
        """Check if file is relevant to NETZ business"""
        filename_lower = filename.lower()
        
        # Always include files with these terms
        relevant_terms = [
            'netz', 'tarif', 'prix', 'formation', 'service', 'guide', 
            'procedure', 'contact', 'client', 'devis', 'facture',
            'maintenance', 'depannage', 'support', 'documentation'
        ]
        
        return any(term in filename_lower for term in relevant_terms)
    
    def _get_file_priority(self, filename: str) -> int:
        """Get priority score for file (1-5, 5 being highest)"""
        filename_lower = filename.lower()
        
        if any(term in filename_lower for term in ['tarif', 'prix', 'pricing']):
            return 5
        elif any(term in filename_lower for term in ['guide', 'manuel', 'documentation']):
            return 4
        elif any(term in filename_lower for term in ['formation', 'training']):
            return 4
        elif any(term in filename_lower for term in ['service', 'procedure']):
            return 3
        else:
            return 2
    
    def _create_content_chunks(self, content: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split content into chunks for better AI processing"""
        if len(content) <= max_chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + max_chunk_size
            
            # Try to break at sentence boundaries
            if end < len(content):
                # Look for sentence endings
                for i in range(end, max(start + max_chunk_size//2, end - 100), -1):
                    if content[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    async def add_to_rag_system(self) -> Dict[str, Any]:
        """Add all processed documents to RAG system"""
        logger.info(f"🧠 Adding {len(self.processed_documents)} documents to RAG system...")
        
        total_chunks = 0
        successful_docs = 0
        
        for doc in self.processed_documents:
            try:
                for i, chunk in enumerate(doc.chunks):
                    chunk_id = f"{doc.id}_chunk_{i}"
                    
                    metadata = {
                        **doc.metadata,
                        "document_name": doc.name,
                        "chunk_index": i,
                        "total_chunks": len(doc.chunks),
                        "source_path": doc.source_path
                    }
                    
                    await self.rag.add_document(
                        doc_id=chunk_id,
                        content=chunk,
                        metadata=metadata
                    )
                    
                    total_chunks += 1
                
                successful_docs += 1
                logger.info(f"✅ Added {doc.name} to RAG ({len(doc.chunks)} chunks)")
                
            except Exception as e:
                logger.error(f"❌ Failed to add {doc.name} to RAG: {str(e)}")
        
        # Save RAG state
        await self.rag.save_state()
        
        result = {
            "documents_processed": successful_docs,
            "total_chunks_added": total_chunks,
            "rag_state_saved": True,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"💾 RAG system updated: {successful_docs} docs, {total_chunks} chunks")
        return result
    
    async def run_comprehensive_training(self, folder_names: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive training from Google Drive"""
        logger.info("🚀 Starting comprehensive Google Drive AI training...")
        
        if not self.google_drive_service:
            logger.error("❌ Google Drive API not available")
            return {"success": False, "error": "Google Drive API not available"}
        
        # Discover folders if not specified
        if not folder_names:
            folders = await self.discover_netz_folders()
            folder_names = [folder['name'] for folder in folders[:3]]  # Limit to 3 folders
        
        if not folder_names:
            logger.error("❌ No NETZ folders found")
            return {"success": False, "error": "No NETZ folders found"}
        
        # Process each folder
        folder_results = []
        for folder_name in folder_names:
            # Find folder ID
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.google_drive_service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get('files', [])
            
            if folders:
                folder_result = await self.process_folder_contents(folders[0]['id'], folder_name)
                folder_results.append(folder_result)
        
        # Add to RAG system
        rag_result = await self.add_to_rag_system()
        
        # Generate summary
        total_processed = sum(result.get('processed', 0) for result in folder_results)
        total_files = sum(result.get('total_files', 0) for result in folder_results)
        
        summary = {
            "success": True,
            "training_completed": datetime.now().isoformat(),
            "folders_processed": len(folder_results),
            "total_files_found": total_files,
            "documents_processed": total_processed,
            "documents_added_to_ai": len(self.processed_documents),
            "total_chunks": rag_result.get('total_chunks_added', 0),
            "folder_results": folder_results,
            "rag_integration": rag_result
        }
        
        logger.info(f"🎯 Training completed: {total_processed}/{total_files} files processed")
        return summary
    
    async def test_ai_knowledge(self) -> Dict[str, Any]:
        """Test AI knowledge with NETZ-specific queries"""
        test_queries = [
            "Quels sont les tarifs de NETZ Informatique?",
            "Comment contacter NETZ?",
            "Quelles formations proposez-vous?",
            "Quel est le prix de la maintenance?",
            "Où êtes-vous situés?",
            "Quels sont vos horaires d'ouverture?",
            "Proposez-vous des formations Python?",
            "Comment obtenir un devis?",
            "Quel est le délai d'intervention?",
            "Travaillez-vous avec les entreprises?"
        ]
        
        test_results = []
        logger.info("🧪 Testing AI knowledge with NETZ-specific queries...")
        
        for query in test_queries:
            try:
                results = await self.rag.search(query, k=3)
                
                if results:
                    best_match = results[0]
                    confidence = best_match.get('score', 0)
                    
                    test_results.append({
                        "query": query,
                        "success": True,
                        "confidence": confidence,
                        "response_preview": best_match['content'][:200] + "...",
                        "source_document": best_match.get('metadata', {}).get('document_name', 'Unknown'),
                        "source_folder": best_match.get('metadata', {}).get('folder', 'Unknown')
                    })
                    
                    logger.info(f"✅ {query} -> Confidence: {confidence:.3f}")
                else:
                    test_results.append({
                        "query": query,
                        "success": False,
                        "error": "No results found"
                    })
                    logger.warning(f"❌ No results for: {query}")
                    
            except Exception as e:
                test_results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"❌ Error testing '{query}': {str(e)}")
        
        successful_queries = len([r for r in test_results if r.get('success')])
        success_rate = (successful_queries / len(test_queries)) * 100
        
        return {
            "total_queries": len(test_queries),
            "successful_queries": successful_queries,
            "success_rate": success_rate,
            "test_results": test_results,
            "ai_readiness": "Excellent" if success_rate >= 90 else "Good" if success_rate >= 75 else "Fair" if success_rate >= 60 else "Needs Improvement"
        }

async def main():
    """Main function to run the enhanced Google Drive training"""
    logger.info("🚀 NETZ AI Enhanced Google Drive Training System")
    
    trainer = EnhancedGoogleDriveTrainer()
    
    # Run comprehensive training
    training_result = await trainer.run_comprehensive_training()
    
    if training_result.get('success'):
        logger.info("✅ Training completed successfully!")
        
        # Test AI knowledge
        test_result = await trainer.test_ai_knowledge()
        
        # Final report
        logger.info(f"\n🎯 FINAL TRAINING REPORT:")
        logger.info(f"   📁 Folders processed: {training_result.get('folders_processed', 0)}")
        logger.info(f"   📄 Documents processed: {training_result.get('documents_processed', 0)}")
        logger.info(f"   🧠 AI knowledge chunks: {training_result.get('total_chunks', 0)}")
        logger.info(f"   ✅ AI success rate: {test_result.get('success_rate', 0):.1f}%")
        logger.info(f"   🎓 AI readiness: {test_result.get('ai_readiness', 'Unknown')}")
        
        return {
            "training_result": training_result,
            "test_result": test_result,
            "overall_success": training_result.get('success') and test_result.get('success_rate', 0) >= 75
        }
    else:
        logger.error("❌ Training failed")
        return {"success": False, "error": training_result.get('error')}

if __name__ == "__main__":
    asyncio.run(main())