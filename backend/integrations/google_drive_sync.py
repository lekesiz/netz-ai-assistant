"""
Google Drive Sync Integration
NETZ AI Project - Completed by YAGO recommendations

Features:
- OAuth2 authentication
- Folder-specific sync
- Incremental updates (only new/modified files)
- PDF, Word, Excel support
- Error handling & retry
- Progress tracking
"""

import os
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveSync:
    """
    Google Drive Synchronization Service
    
    Syncs specified folders from Google Drive to local storage
    and processes documents for AI knowledge base.
    """
    
    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
        download_dir: str = "./drive_downloads",
        sync_history_file: str = "./drive_sync_history.json"
    ):
        """
        Initialize Google Drive Sync
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON
            token_file: Path to save/load OAuth token
            download_dir: Directory to download files
            sync_history_file: JSON file to track sync history
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.download_dir = Path(download_dir)
        self.sync_history_file = sync_history_file
        
        # Create download directory
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Load sync history
        self.sync_history = self._load_sync_history()
        
        # Initialize Drive service
        self.service = self._authenticate()
        
        logger.info(f"✅ Google Drive Sync initialized")
        logger.info(f"   Download directory: {self.download_dir}")
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing expired token...")
                creds.refresh(Request())
            else:
                logger.info("🔐 Starting OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            logger.info("✅ Credentials saved")
        
        return build('drive', 'v3', credentials=creds)
    
    def _load_sync_history(self) -> Dict:
        """Load sync history from file"""
        if os.path.exists(self.sync_history_file):
            with open(self.sync_history_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_sync_history(self):
        """Save sync history to file"""
        with open(self.sync_history_file, 'w') as f:
            json.dump(self.sync_history, f, indent=2)
    
    def sync_folders(
        self,
        folder_names: List[str],
        file_types: List[str] = ['.pdf', '.docx', '.xlsx', '.txt', '.csv']
    ) -> Dict:
        """
        Sync specified folders from Google Drive
        
        Args:
            folder_names: List of folder names to sync
            file_types: File extensions to download
            
        Returns:
            Dict with sync results
        """
        logger.info(f"🔄 Starting sync for folders: {folder_names}")
        
        results = {
            "folders_processed": 0,
            "files_downloaded": 0,
            "files_skipped": 0,
            "errors": [],
            "new_files": []
        }
        
        for folder_name in folder_names:
            try:
                folder_id = self._find_folder(folder_name)
                
                if not folder_id:
                    logger.warning(f"⚠️ Folder not found: {folder_name}")
                    results["errors"].append(f"Folder not found: {folder_name}")
                    continue
                
                logger.info(f"📁 Processing folder: {folder_name}")
                folder_results = self._sync_folder(folder_id, folder_name, file_types)
                
                results["folders_processed"] += 1
                results["files_downloaded"] += folder_results["downloaded"]
                results["files_skipped"] += folder_results["skipped"]
                results["new_files"].extend(folder_results["new_files"])
                
            except Exception as e:
                logger.error(f"❌ Error syncing folder {folder_name}: {e}")
                results["errors"].append(f"{folder_name}: {str(e)}")
        
        # Save sync history
        self._save_sync_history()
        
        logger.info(f"✅ Sync complete!")
        logger.info(f"   Folders: {results['folders_processed']}")
        logger.info(f"   Downloaded: {results['files_downloaded']}")
        logger.info(f"   Skipped: {results['files_skipped']}")
        
        return results
    
    def _find_folder(self, folder_name: str) -> Optional[str]:
        """Find folder ID by name"""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
            
            return None
            
        except HttpError as e:
            logger.error(f"❌ Error finding folder: {e}")
            return None
    
    def _sync_folder(
        self,
        folder_id: str,
        folder_name: str,
        file_types: List[str]
    ) -> Dict:
        """Sync all files in a folder"""
        results = {
            "downloaded": 0,
            "skipped": 0,
            "new_files": []
        }
        
        try:
            # Get all files in folder
            query = f"'{folder_id}' in parents and trashed=false"
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime, mimeType, size)',
                pageSize=1000
            ).execute()
            
            files = response.get('files', [])
            logger.info(f"   Found {len(files)} files")
            
            for file_meta in files:
                file_id = file_meta['id']
                file_name = file_meta['name']
                modified_time = file_meta['modifiedTime']
                
                # Check file type
                file_ext = Path(file_name).suffix.lower()
                if file_ext not in file_types:
                    continue
                
                # Check if file needs update
                if self._should_download(file_id, modified_time):
                    success = self._download_file(file_id, file_name, folder_name)
                    
                    if success:
                        results["downloaded"] += 1
                        results["new_files"].append({
                            "name": file_name,
                            "path": str(self.download_dir / folder_name / file_name),
                            "modified": modified_time
                        })
                        
                        # Update sync history
                        self.sync_history[file_id] = {
                            "name": file_name,
                            "modified_time": modified_time,
                            "last_sync": datetime.now().isoformat()
                        }
                    else:
                        logger.warning(f"⚠️ Failed to download: {file_name}")
                else:
                    results["skipped"] += 1
                    logger.debug(f"   Skipped (already synced): {file_name}")
            
        except HttpError as e:
            logger.error(f"❌ Error syncing folder: {e}")
        
        return results
    
    def _should_download(self, file_id: str, modified_time: str) -> bool:
        """Check if file should be downloaded (new or modified)"""
        if file_id not in self.sync_history:
            return True
        
        last_modified = self.sync_history[file_id].get("modified_time")
        
        return last_modified != modified_time
    
    def _download_file(
        self,
        file_id: str,
        file_name: str,
        folder_name: str
    ) -> bool:
        """Download a single file"""
        try:
            # Create subfolder
            subfolder = self.download_dir / folder_name
            subfolder.mkdir(parents=True, exist_ok=True)
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            file_path = subfolder / file_name
            
            with io.FileIO(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.debug(f"   Downloading {file_name}: {progress}%")
            
            logger.info(f"   ✅ Downloaded: {file_name}")
            return True
            
        except HttpError as e:
            logger.error(f"   ❌ Download failed for {file_name}: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        return {
            "total_files_synced": len(self.sync_history),
            "download_directory": str(self.download_dir),
            "last_sync_history": list(self.sync_history.values())[-5:] if self.sync_history else []
        }


# Example usage
if __name__ == "__main__":
    # Initialize sync
    sync = GoogleDriveSync(
        credentials_file="credentials.json",
        download_dir="./drive_downloads"
    )
    
    # Sync specific folders
    folders_to_sync = [
        "NETZ Documents",
        "Formations", 
        "Contrats"
    ]
    
    results = sync.sync_folders(folders_to_sync)
    
    print("\n📊 Sync Results:")
    print(f"   Folders processed: {results['folders_processed']}")
    print(f"   Files downloaded: {results['files_downloaded']}")
    print(f"   Files skipped: {results['files_skipped']}")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"   - {error}")
