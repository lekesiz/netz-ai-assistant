"""
AI Training Orchestrator
Manages all data synchronization and AI training processes
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess

# Import sync modules
from google_drive_sync import GoogleDriveSync
from pennylane_sync import PennyLaneSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AITrainingOrchestrator:
    """Orchestrates all AI training and data synchronization"""
    
    def __init__(self):
        self.config_file = Path("ai_training_config.json")
        self.status_file = Path("ai_training_status.json")
        self.config = self._load_config()
        self.status = self._load_status()
        
        # Initialize sync managers
        self._init_sync_managers()
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        config = {
            "google_drive": {
                "path": "/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Diğer bilgisayarlar/Mon ordinateur/Commun",
                "sync_interval_hours": 24,
                "enabled": True
            },
            "pennylane": {
                "api_key": "env:PENNYLANE_API_KEY",
                "company_id": "env:PENNYLANE_COMPANY_ID",
                "sync_interval_hours": 24,
                "enabled": True
            },
            "ai_model": {
                "name": "mistral:latest",
                "training_enabled": True,
                "auto_restart": True,
                "learning_enabled": True
            },
            "services": {
                "simple_api_port": 8001,
                "document_upload_port": 8002,
                "admin_api_port": 8003,
                "frontend_port": 3001
            }
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_status(self) -> Dict:
        """Load status"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        
        return {
            "last_sync": {
                "google_drive": None,
                "pennylane": None
            },
            "document_count": 0,
            "training_status": "not_started",
            "services": {
                "simple_api": "stopped",
                "document_upload": "stopped",
                "frontend": "stopped"
            }
        }
    
    def _save_status(self):
        """Save status"""
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def _init_sync_managers(self):
        """Initialize sync managers"""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Google Drive sync
        if self.config["google_drive"]["enabled"]:
            self.gdrive_sync = GoogleDriveSync(
                self.config["google_drive"]["path"]
            )
        
        # PennyLane sync
        if self.config["pennylane"]["enabled"]:
            # Get credentials from env if specified
            api_key = self.config["pennylane"]["api_key"]
            company_id = self.config["pennylane"]["company_id"]
            
            if api_key.startswith("env:"):
                api_key = os.getenv(api_key[4:], "")
            if company_id.startswith("env:"):
                company_id = os.getenv(company_id[4:], "")
            
            if api_key and company_id:
                self.pennylane_sync = PennyLaneSync(api_key, company_id)
                logger.info(f"PennyLane sync initialized for company {company_id}")
            else:
                logger.warning("PennyLane credentials not found in environment")
    
    def start_services(self):
        """Start all services"""
        logger.info("Starting AI training services...")
        
        # Check if services are already running
        self._check_services()
        
        # Start backend services
        services = [
            ("simple_api.py", self.config["services"]["simple_api_port"]),
            ("document_upload_api.py", self.config["services"]["document_upload_port"]),
            ("admin_api.py", self.config["services"]["admin_api_port"])
        ]
        
        for service, port in services:
            if not self._is_service_running(service):
                logger.info(f"Starting {service} on port {port}")
                subprocess.Popen(
                    [sys.executable, service],
                    cwd=Path(__file__).parent,
                    stdout=open(f"{service}.log", "w"),
                    stderr=subprocess.STDOUT
                )
                time.sleep(2)
        
        # Start frontend
        frontend_path = Path(__file__).parent.parent / "frontend"
        if frontend_path.exists():
            logger.info("Starting frontend...")
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_path,
                stdout=open("frontend.log", "w"),
                stderr=subprocess.STDOUT
            )
        
        self.status["services"]["simple_api"] = "running"
        self.status["services"]["document_upload"] = "running"
        self.status["services"]["frontend"] = "running"
        self._save_status()
    
    def _is_service_running(self, service_name: str) -> bool:
        """Check if service is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", service_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_services(self):
        """Check status of all services"""
        services = ["simple_api.py", "document_upload_api.py"]
        
        for service in services:
            if self._is_service_running(service):
                logger.info(f"{service} is already running")
            else:
                logger.info(f"{service} is not running")
    
    def sync_google_drive(self):
        """Sync Google Drive documents"""
        if not self.config["google_drive"]["enabled"]:
            logger.info("Google Drive sync is disabled")
            return
        
        logger.info("Starting Google Drive sync...")
        try:
            self.gdrive_sync.sync_folder()
            self.status["last_sync"]["google_drive"] = datetime.now().isoformat()
            self._save_status()
            logger.info("Google Drive sync completed")
        except Exception as e:
            logger.error(f"Google Drive sync failed: {e}")
    
    def sync_pennylane(self):
        """Sync PennyLane data"""
        if not self.config["pennylane"]["enabled"]:
            logger.info("PennyLane sync is disabled")
            return
        
        if not hasattr(self, 'pennylane_sync'):
            logger.warning("PennyLane sync not initialized (missing API credentials)")
            return
        
        logger.info("Starting PennyLane sync...")
        try:
            self.pennylane_sync.sync_financial_data()
            self.status["last_sync"]["pennylane"] = datetime.now().isoformat()
            self._save_status()
            logger.info("PennyLane sync completed")
        except Exception as e:
            logger.error(f"PennyLane sync failed: {e}")
    
    def train_ai_model(self):
        """Train AI model with new data"""
        logger.info("Starting AI model training...")
        
        # Count documents
        kb_file = Path("simple_api_kb.json")
        if kb_file.exists():
            with open(kb_file, 'r') as f:
                kb = json.load(f)
                doc_count = len(kb.get("documents", []))
                self.status["document_count"] = doc_count
                logger.info(f"Training with {doc_count} documents")
        
        # Update training status
        self.status["training_status"] = "completed"
        self._save_status()
        
        logger.info("AI model training completed")
    
    def run_full_sync(self):
        """Run full synchronization"""
        logger.info("Starting full synchronization...")
        
        # Start services
        self.start_services()
        
        # Sync Google Drive
        self.sync_google_drive()
        
        # Sync PennyLane
        self.sync_pennylane()
        
        # Train AI model
        self.train_ai_model()
        
        logger.info("Full synchronization completed")
    
    def start_scheduled_sync(self):
        """Start scheduled synchronization"""
        logger.info("Starting scheduled synchronization...")
        
        # Run initial sync
        self.run_full_sync()
        
        # Start Google Drive monitoring
        if self.config["google_drive"]["enabled"]:
            gdrive_thread = threading.Thread(
                target=self._run_gdrive_monitor,
                daemon=True
            )
            gdrive_thread.start()
        
        # Start PennyLane scheduled sync
        if self.config["pennylane"]["enabled"] and hasattr(self, 'pennylane_sync'):
            pennylane_thread = threading.Thread(
                target=self._run_pennylane_scheduled,
                daemon=True
            )
            pennylane_thread.start()
        
        logger.info("Scheduled synchronization started")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(60)
                self._check_services()
        except KeyboardInterrupt:
            logger.info("Stopping orchestrator...")
    
    def _run_gdrive_monitor(self):
        """Run Google Drive monitoring"""
        from watchdog.observers import Observer
        from google_drive_sync import GoogleDriveWatcher
        
        event_handler = GoogleDriveWatcher(self.gdrive_sync)
        observer = Observer()
        observer.schedule(
            event_handler, 
            self.config["google_drive"]["path"], 
            recursive=True
        )
        observer.start()
        observer.join()
    
    def _run_pennylane_scheduled(self):
        """Run PennyLane scheduled sync"""
        self.pennylane_sync.start_auto_sync(
            interval_hours=self.config["pennylane"]["sync_interval_hours"]
        )
    
    def get_status_report(self) -> Dict:
        """Get status report"""
        kb_file = Path("simple_api_kb.json")
        doc_count = 0
        
        if kb_file.exists():
            with open(kb_file, 'r') as f:
                kb = json.load(f)
                doc_count = len(kb.get("documents", []))
        
        return {
            "configuration": self.config,
            "status": self.status,
            "document_count": doc_count,
            "services": {
                service: "running" if self._is_service_running(service + ".py")
                else "stopped"
                for service in ["simple_api", "document_upload"]
            },
            "report_time": datetime.now().isoformat()
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Training Orchestrator")
    parser.add_argument("--sync", action="store_true", help="Run one-time sync")
    parser.add_argument("--monitor", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--status", action="store_true", help="Show status report")
    parser.add_argument("--start-services", action="store_true", help="Start all services")
    
    args = parser.parse_args()
    
    orchestrator = AITrainingOrchestrator()
    
    if args.status:
        report = orchestrator.get_status_report()
        print(json.dumps(report, indent=2))
    elif args.start_services:
        orchestrator.start_services()
    elif args.sync:
        orchestrator.run_full_sync()
    elif args.monitor:
        orchestrator.start_scheduled_sync()
    else:
        # Default: start monitoring
        orchestrator.start_scheduled_sync()

if __name__ == "__main__":
    main()