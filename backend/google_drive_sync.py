"""
Google Drive Synchronization Module
Automatically syncs documents from Google Drive to AI training system
"""

import os
import json
import hashlib
import schedule
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleDriveSync:
    """Sync Google Drive documents with AI training system"""
    
    def __init__(self, gdrive_path: str, kb_file: str = "simple_api_kb.json"):
        self.gdrive_path = Path(gdrive_path)
        self.kb_file = Path(kb_file)
        self.sync_history_file = Path("gdrive_sync_history.json")
        self.processed_dir = Path("processed_documents")
        self.processed_dir.mkdir(exist_ok=True)
        
        # Supported file extensions
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt', '.csv'}
        
        # Important folders to sync
        self.important_folders = [
            "1. NETZ INFORMATIQUE",
            "Formations",
            "Documents",
            "clients",
            "Facture 2023",
            "Facture 2024",
            "Facture 2025",
            "BILAN DE COMPETENCE"
        ]
        
        # Limit number of files for initial sync
        self.max_files_per_sync = 10
        
        # Load sync history
        self.sync_history = self._load_sync_history()
        
    def _load_sync_history(self) -> Dict:
        """Load sync history from file"""
        if self.sync_history_file.exists():
            with open(self.sync_history_file, 'r') as f:
                return json.load(f)
        return {"synced_files": {}, "last_sync": None}
    
    def _save_sync_history(self):
        """Save sync history to file"""
        with open(self.sync_history_file, 'w') as f:
            json.dump(self.sync_history, f, indent=2)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file"""
        # Use file path and modification time for faster hashing
        stat = file_path.stat()
        hash_str = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def _extract_content(self, file_path: Path) -> Optional[str]:
        """Extract content from file using document processor"""
        try:
            # Import document processor
            from document_upload_api import DocumentProcessor
            
            file_ext = file_path.suffix.lower()
            
            # Skip very large files for performance
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return f"[File too large for extraction: {file_path.name}]"
            
            logger.info(f"Extracting content from {file_path.name}")
            
            if file_ext == ".pdf":
                return DocumentProcessor.extract_pdf_content(file_path)
            elif file_ext in [".docx", ".doc"]:
                return DocumentProcessor.extract_docx_content(file_path)
            elif file_ext in [".xlsx", ".xls"]:
                return DocumentProcessor.extract_excel_content(file_path)
            elif file_ext in [".txt", ".csv"]:
                return DocumentProcessor.extract_text_content(file_path)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            # Return basic info on error
            return f"[Error extracting: {file_path.name} - {str(e)}]"
    
    def _should_sync_file(self, file_path: Path) -> bool:
        """Check if file should be synced"""
        # Check extension
        if file_path.suffix.lower() not in self.supported_extensions:
            return False
        
        # Check if in important folder
        for folder in self.important_folders:
            if folder in str(file_path):
                return True
        
        # Skip if file is too large (>50MB)
        if file_path.stat().st_size > 50 * 1024 * 1024:
            logger.warning(f"Skipping large file: {file_path}")
            return False
        
        return False
    
    def _update_knowledge_base(self, documents: List[Dict]):
        """Update AI knowledge base with new documents"""
        try:
            # Load existing KB
            if self.kb_file.exists():
                with open(self.kb_file, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
            else:
                kb = {"documents": [], "last_updated": None}
            
            # Add new documents
            existing_hashes = {doc.get("hash") for doc in kb["documents"]}
            
            for doc in documents:
                if doc["hash"] not in existing_hashes:
                    kb["documents"].append(doc)
                    logger.info(f"Added to KB: {doc['metadata']['filename']}")
            
            # Update timestamp
            kb["last_updated"] = datetime.now().isoformat()
            
            # Save KB
            with open(self.kb_file, 'w', encoding='utf-8') as f:
                json.dump(kb, f, ensure_ascii=False, indent=2)
            
            # Restart simple_api
            os.system("pkill -f simple_api.py")
            os.system("python simple_api.py > simple_api.log 2>&1 &")
            
            return True
        except Exception as e:
            logger.error(f"Error updating KB: {e}")
            return False
    
    def sync_folder(self, folder_path: Optional[Path] = None):
        """Sync specific folder or all important folders"""
        logger.info("Starting Google Drive sync...")
        
        if folder_path:
            folders_to_sync = [folder_path]
        else:
            folders_to_sync = [
                self.gdrive_path / folder 
                for folder in self.important_folders 
                if (self.gdrive_path / folder).exists()
            ]
        
        new_documents = []
        file_count = 0
        
        for folder in folders_to_sync:
            logger.info(f"Scanning folder: {folder}")
            
            # Walk through folder
            for file_path in folder.rglob("*"):
                if not file_path.is_file():
                    continue
                
                if not self._should_sync_file(file_path):
                    continue
                
                # Limit number of files
                if file_count >= self.max_files_per_sync:
                    logger.info(f"Reached file limit ({self.max_files_per_sync})")
                    break
                
                try:
                    # Get file hash
                    file_hash = self._get_file_hash(file_path)
                    
                    # Check if already synced
                    if file_hash in self.sync_history["synced_files"]:
                        continue
                    
                    # Extract content
                    content = self._extract_content(file_path)
                    if not content:
                        continue
                    
                    # Create document entry
                    doc = {
                        "content": content,
                        "metadata": {
                            "filename": file_path.name,
                            "filepath": str(file_path.relative_to(self.gdrive_path)),
                            "file_type": file_path.suffix.lower(),
                            "file_size": file_path.stat().st_size,
                            "upload_time": datetime.now().isoformat(),
                            "source": "google_drive_sync",
                            "folder": folder.name
                        },
                        "hash": file_hash,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    new_documents.append(doc)
                    
                    # Update sync history
                    self.sync_history["synced_files"][file_hash] = {
                        "path": str(file_path),
                        "synced_at": datetime.now().isoformat()
                    }
                    
                    # Copy to processed folder
                    processed_path = self.processed_dir / f"{file_hash}_{file_path.name}"
                    shutil.copy2(file_path, processed_path)
                    
                    logger.info(f"Processed: {file_path.name}")
                    file_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
            
            # Break if file limit reached
            if file_count >= self.max_files_per_sync:
                break
        
        # Update knowledge base if new documents
        if new_documents:
            success = self._update_knowledge_base(new_documents)
            if success:
                logger.info(f"Synced {len(new_documents)} new documents")
                self.sync_history["last_sync"] = datetime.now().isoformat()
                self._save_sync_history()
        else:
            logger.info("No new documents to sync")
    
    def start_auto_sync(self, interval_hours: int = 24):
        """Start automatic sync at specified interval"""
        logger.info(f"Starting auto-sync every {interval_hours} hours")
        
        # Run initial sync
        self.sync_folder()
        
        # Schedule periodic sync
        schedule.every(interval_hours).hours.do(self.sync_folder)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

class GoogleDriveWatcher(FileSystemEventHandler):
    """Watch Google Drive for real-time changes"""
    
    def __init__(self, sync_manager: GoogleDriveSync):
        self.sync_manager = sync_manager
        self.last_sync = {}
        
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path)
    
    def _handle_file_change(self, file_path: str):
        """Handle file creation/modification"""
        path = Path(file_path)
        
        # Avoid duplicate processing
        file_hash = str(path)
        current_time = time.time()
        if file_hash in self.last_sync:
            if current_time - self.last_sync[file_hash] < 10:  # 10 second cooldown
                return
        
        self.last_sync[file_hash] = current_time
        
        # Check if file should be synced
        if self.sync_manager._should_sync_file(path):
            logger.info(f"Detected change: {path.name}")
            # Sync just the parent folder
            self.sync_manager.sync_folder(path.parent)

def main():
    """Main function to run Google Drive sync"""
    # Configuration
    GDRIVE_PATH = "/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Diğer bilgisayarlar/Mon ordinateur/Commun"
    
    # Create sync manager
    sync_manager = GoogleDriveSync(GDRIVE_PATH)
    
    # Option 1: One-time sync (default)
    sync_manager.sync_folder()
    
    # Option 2: Real-time monitoring
    # event_handler = GoogleDriveWatcher(sync_manager)
    # observer = Observer()
    # observer.schedule(event_handler, GDRIVE_PATH, recursive=True)
    # observer.start()
    
    # try:
    #     logger.info("Google Drive watcher started. Press Ctrl+C to stop.")
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()
    
    # Option 3: Scheduled sync
    # sync_manager.start_auto_sync(interval_hours=1)

if __name__ == "__main__":
    main()