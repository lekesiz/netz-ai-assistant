import logging
import schedule
import time
import threading
from datetime import datetime
from pathlib import Path
import json
from typing import Optional
from pennylane_ingestion import PennyLaneIngestion
from data_ingestion import DataIngestion

logger = logging.getLogger(__name__)

class DataScheduler:
    """Scheduler for automatic data updates"""
    
    def __init__(self):
        self.pennylane_ingestion = PennyLaneIngestion()
        self.google_drive_ingestion = DataIngestion()
        self.is_running = False
        self.scheduler_thread = None
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load scheduler configuration"""
        default_config = {
            "pennylane": {
                "enabled": True,
                "schedule": "daily",  # daily, hourly, weekly
                "time": "02:00"  # For daily schedule
            },
            "google_drive": {
                "enabled": True,
                "schedule": "daily",
                "time": "03:00"
            },
            "retention_days": 30  # Keep backups for 30 days
        }
        
        config_path = Path("configs/scheduler_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        
        return default_config
    
    def update_pennylane_data(self):
        """Update PennyLane accounting data"""
        try:
            logger.info("Starting PennyLane data update...")
            self.pennylane_ingestion.ingest_pennylane_data()
            self._log_update_status("pennylane", "success")
            logger.info("PennyLane data update completed successfully")
        except Exception as e:
            logger.error(f"PennyLane update failed: {e}")
            self._log_update_status("pennylane", "failed", str(e))
    
    def update_google_drive_data(self):
        """Update Google Drive documents"""
        try:
            logger.info("Starting Google Drive data update...")
            google_drive_path = "/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Diğer bilgisayarlar/Mon ordinateur/Commun"
            
            # Update documents from key directories
            key_dirs = [
                "1. NETZ INFORMATIQUE/1.5 DOCUMENTS ADMINISTRATIFS",
                "1. NETZ INFORMATIQUE/1.4 SERVICES/FORMATIONS",
                "1. NETZ INFORMATIQUE/1.3 PRODUITS"
            ]
            
            for dir_name in key_dirs:
                full_path = Path(google_drive_path) / dir_name
                if full_path.exists():
                    logger.info(f"Processing directory: {dir_name}")
                    self.google_drive_ingestion.ingest_directory(str(full_path))
            
            self._log_update_status("google_drive", "success")
            logger.info("Google Drive data update completed successfully")
        except Exception as e:
            logger.error(f"Google Drive update failed: {e}")
            self._log_update_status("google_drive", "failed", str(e))
    
    def clean_old_backups(self):
        """Clean old backup files based on retention policy"""
        try:
            retention_days = self.config.get("retention_days", 30)
            backup_dir = Path("data/pennylane_backup")
            
            if not backup_dir.exists():
                return
            
            cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
            
            for backup_file in backup_dir.glob("pennylane_*.json"):
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file}")
                    
        except Exception as e:
            logger.error(f"Error cleaning backups: {e}")
    
    def _log_update_status(self, source: str, status: str, error: Optional[str] = None):
        """Log update status to file"""
        status_file = Path("data/update_log.json")
        status_file.parent.mkdir(exist_ok=True)
        
        # Load existing log
        log_data = []
        if status_file.exists():
            with open(status_file, 'r') as f:
                log_data = json.load(f)
        
        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "status": status
        }
        if error:
            entry["error"] = error
            
        log_data.append(entry)
        
        # Keep only last 100 entries
        log_data = log_data[-100:]
        
        # Save updated log
        with open(status_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def setup_schedules(self):
        """Setup update schedules based on configuration"""
        # PennyLane schedule
        if self.config["pennylane"]["enabled"]:
            schedule_type = self.config["pennylane"]["schedule"]
            if schedule_type == "daily":
                schedule.every().day.at(self.config["pennylane"]["time"]).do(self.update_pennylane_data)
            elif schedule_type == "hourly":
                schedule.every().hour.do(self.update_pennylane_data)
            elif schedule_type == "weekly":
                schedule.every().week.at(self.config["pennylane"]["time"]).do(self.update_pennylane_data)
            logger.info(f"PennyLane updates scheduled: {schedule_type}")
        
        # Google Drive schedule
        if self.config["google_drive"]["enabled"]:
            schedule_type = self.config["google_drive"]["schedule"]
            if schedule_type == "daily":
                schedule.every().day.at(self.config["google_drive"]["time"]).do(self.update_google_drive_data)
            elif schedule_type == "hourly":
                schedule.every().hour.do(self.update_google_drive_data)
            elif schedule_type == "weekly":
                schedule.every().week.at(self.config["google_drive"]["time"]).do(self.update_google_drive_data)
            logger.info(f"Google Drive updates scheduled: {schedule_type}")
        
        # Cleanup schedule (daily at 4 AM)
        schedule.every().day.at("04:00").do(self.clean_old_backups)
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        self.setup_schedules()
        self.is_running = True
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """Start the scheduler in background"""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.scheduler_thread = threading.Thread(target=self.run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            logger.info("Data scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Data scheduler stopped")
    
    def trigger_update(self, source: str):
        """Manually trigger an update for a specific source"""
        if source == "pennylane":
            self.update_pennylane_data()
        elif source == "google_drive":
            self.update_google_drive_data()
        else:
            raise ValueError(f"Unknown source: {source}")

# Singleton instance
_scheduler = None

def get_scheduler() -> DataScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = DataScheduler()
    return _scheduler

# Auto-start scheduler when module is imported
def init_scheduler():
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler