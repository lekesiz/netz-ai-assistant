"""
Integrations API Routes
NETZ AI Project - REST API for Google Drive, Gmail, PennyLane, Wedof integrations

Features:
- Manual sync triggers for all integrations
- Sync status tracking
- Results retrieval
- Error handling
- Admin-only access control
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Try to import integrations
try:
    from integrations.google_drive_sync import get_google_drive_sync, GoogleDriveSync
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    logger.warning("⚠️  Google Drive integration not available")

try:
    from integrations.gmail_sync import get_gmail_sync, GmailSync
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logger.warning("⚠️ Gmail integration not available")

try:
    from integrations.pennylane_webhook import get_pennylane_client
    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False
    logger.warning("⚠️ PennyLane integration not available")

try:
    from integrations.wedof_sync import get_wedof_sync, WedofSync
    WEDOF_AVAILABLE = True
except ImportError:
    WEDOF_AVAILABLE = False
    logger.warning("⚠️ Wedof integration not available")

# Response models
class SyncResponse(BaseModel):
    """Response for sync operations"""
    success: bool
    message: str
    task_id: Optional[str] = None
    records_synced: Optional[int] = None
    error: Optional[str] = None

class SyncStatusResponse(BaseModel):
    """Sync status for all integrations"""
    google_drive: Dict[str, Any]
    gmail: Dict[str, Any]
    pennylane: Dict[str, Any]
    wedof: Dict[str, Any]
    last_updated: str

class IntegrationStatus(BaseModel):
    """Status for single integration"""
    enabled: bool
    last_sync: Optional[str] = None
    records_count: int = 0
    error: Optional[str] = None

# Store sync history in memory (in production, use database)
sync_history: Dict[str, List[Dict]] = {
    "google_drive": [],
    "gmail": [],
    "pennylane": [],
    "wedof": []
}

def create_integrations_router(get_admin_user=None):
    """
    Create integrations API router

    Args:
        get_admin_user: Dependency function for admin authentication
    """
    router = APIRouter(prefix="/api/integrations", tags=["integrations"])

    # Helper function for admin dependency (optional)
    def require_admin():
        if get_admin_user:
            return Depends(get_admin_user)
        return lambda: None  # No auth required if not provided

    # ==================== GOOGLE DRIVE ENDPOINTS ====================

    @router.post("/drive/sync", response_model=SyncResponse)
    async def trigger_drive_sync(
        background_tasks: BackgroundTasks,
        folder_names: Optional[List[str]] = None,
        # admin = require_admin()
    ):
        """
        Manually trigger Google Drive sync

        Args:
            folder_names: List of folder names to sync (default: all configured folders)

        Returns:
            Sync status with task ID
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google Drive integration is not available"
            )

        try:
            # Default folders
            if not folder_names:
                folder_names = ["NETZ Clients", "NETZ Documents", "NETZ Formations"]

            # Run sync in background
            def sync_task():
                try:
                    sync = get_google_drive_sync()
                    results = sync.sync_folders(folder_names)

                    # Store in history
                    sync_history["google_drive"].append({
                        "timestamp": datetime.now().isoformat(),
                        "folder_count": len(results),
                        "total_files": sum(r["files_synced"] for r in results),
                        "status": "success"
                    })

                    logger.info(f"✅ Drive sync complete: {len(results)} folders")

                except Exception as e:
                    logger.error(f"❌ Drive sync failed: {e}")
                    sync_history["google_drive"].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "error",
                        "error": str(e)
                    })

            background_tasks.add_task(sync_task)

            return SyncResponse(
                success=True,
                message=f"Google Drive sync started for {len(folder_names)} folder(s)",
                task_id=f"drive-{datetime.now().timestamp()}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to trigger Drive sync: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start sync: {str(e)}"
            )

    # ==================== GMAIL ENDPOINTS ====================

    @router.post("/gmail/sync", response_model=SyncResponse)
    async def trigger_gmail_sync(
        background_tasks: BackgroundTasks,
        days_back: int = 365,
        max_results: int = 1000,
        # admin = require_admin()
    ):
        """
        Manually trigger Gmail sync

        Args:
            days_back: How many days back to fetch emails
            max_results: Maximum number of emails to fetch

        Returns:
            Sync status with task ID
        """
        if not GMAIL_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gmail integration is not available"
            )

        try:
            def sync_task():
                try:
                    sync = get_gmail_sync()
                    results = sync.sync_emails(days_back=days_back, max_results=max_results)

                    sync_history["gmail"].append({
                        "timestamp": datetime.now().isoformat(),
                        "emails_synced": len(results),
                        "days_back": days_back,
                        "status": "success"
                    })

                    logger.info(f"✅ Gmail sync complete: {len(results)} emails")

                except Exception as e:
                    logger.error(f"❌ Gmail sync failed: {e}")
                    sync_history["gmail"].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "error",
                        "error": str(e)
                    })

            background_tasks.add_task(sync_task)

            return SyncResponse(
                success=True,
                message=f"Gmail sync started (last {days_back} days, max {max_results} emails)",
                task_id=f"gmail-{datetime.now().timestamp()}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to trigger Gmail sync: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start sync: {str(e)}"
            )

    # ==================== WEDOF ENDPOINTS ====================

    @router.post("/wedof/sync", response_model=SyncResponse)
    async def trigger_wedof_sync(
        background_tasks: BackgroundTasks,
        sync_stagiaires: bool = True,
        sync_formations: bool = True,
        sync_attendance: bool = True,
        sync_contracts: bool = True,
        # admin = require_admin()
    ):
        """
        Manually trigger Wedof sync

        Args:
            sync_stagiaires: Sync stagiaire data
            sync_formations: Sync formation schedules
            sync_attendance: Sync attendance records
            sync_contracts: Sync contracts

        Returns:
            Sync status with task ID
        """
        if not WEDOF_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Wedof integration is not available"
            )

        try:
            def sync_task():
                try:
                    sync = get_wedof_sync()
                    results = sync.sync_all(
                        stagiaires=sync_stagiaires,
                        formations=sync_formations,
                        attendance=sync_attendance,
                        contracts=sync_contracts
                    )

                    total_records = sum(len(v) for v in results.values())

                    sync_history["wedof"].append({
                        "timestamp": datetime.now().isoformat(),
                        "records_synced": total_records,
                        "breakdown": {k: len(v) for k, v in results.items()},
                        "status": "success"
                    })

                    logger.info(f"✅ Wedof sync complete: {total_records} total records")

                except Exception as e:
                    logger.error(f"❌ Wedof sync failed: {e}")
                    sync_history["wedof"].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "error",
                        "error": str(e)
                    })

            background_tasks.add_task(sync_task)

            return SyncResponse(
                success=True,
                message="Wedof sync started (stagiaires, formations, attendance, contracts)",
                task_id=f"wedof-{datetime.now().timestamp()}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to trigger Wedof sync: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start sync: {str(e)}"
            )

    # ==================== STATUS ENDPOINTS ====================

    @router.get("/status", response_model=SyncStatusResponse)
    async def get_sync_status(
        # admin = require_admin()
    ):
        """
        Get sync status for all integrations

        Returns:
            Status for each integration with last sync time
        """
        def get_integration_status(integration_name: str, available: bool) -> Dict[str, Any]:
            """Get status for a single integration"""
            if not available:
                return {
                    "enabled": False,
                    "last_sync": None,
                    "records_count": 0,
                    "error": "Integration not available"
                }

            history = sync_history.get(integration_name, [])
            if not history:
                return {
                    "enabled": True,
                    "last_sync": None,
                    "records_count": 0,
                    "error": None
                }

            last_sync = history[-1]
            return {
                "enabled": True,
                "last_sync": last_sync.get("timestamp"),
                "records_count": last_sync.get("records_synced", last_sync.get("emails_synced", last_sync.get("total_files", 0))),
                "status": last_sync.get("status"),
                "error": last_sync.get("error")
            }

        return SyncStatusResponse(
            google_drive=get_integration_status("google_drive", GOOGLE_DRIVE_AVAILABLE),
            gmail=get_integration_status("gmail", GMAIL_AVAILABLE),
            pennylane=get_integration_status("pennylane", PENNYLANE_AVAILABLE),
            wedof=get_integration_status("wedof", WEDOF_AVAILABLE),
            last_updated=datetime.now().isoformat()
        )

    @router.get("/{integration}/history")
    async def get_sync_history(
        integration: str,
        limit: int = 10,
        # admin = require_admin()
    ):
        """
        Get sync history for specific integration

        Args:
            integration: Integration name (google_drive, gmail, pennylane, wedof)
            limit: Maximum number of history entries to return

        Returns:
            List of sync history entries
        """
        if integration not in sync_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration '{integration}' not found"
            )

        history = sync_history[integration]
        return {
            "integration": integration,
            "total_syncs": len(history),
            "history": history[-limit:] if limit > 0 else history
        }

    # ==================== SYNC ALL ENDPOINT ====================

    @router.post("/sync-all", response_model=SyncResponse)
    async def trigger_all_syncs(
        background_tasks: BackgroundTasks,
        # admin = require_admin()
    ):
        """
        Trigger sync for all available integrations

        Returns:
            Combined sync status
        """
        triggered = []
        errors = []

        # Google Drive
        if GOOGLE_DRIVE_AVAILABLE:
            try:
                await trigger_drive_sync(background_tasks)
                triggered.append("google_drive")
            except Exception as e:
                errors.append(f"Google Drive: {str(e)}")

        # Gmail
        if GMAIL_AVAILABLE:
            try:
                await trigger_gmail_sync(background_tasks)
                triggered.append("gmail")
            except Exception as e:
                errors.append(f"Gmail: {str(e)}")

        # Wedof
        if WEDOF_AVAILABLE:
            try:
                await trigger_wedof_sync(background_tasks)
                triggered.append("wedof")
            except Exception as e:
                errors.append(f"Wedof: {str(e)}")

        if not triggered:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No integrations available"
            )

        return SyncResponse(
            success=len(errors) == 0,
            message=f"Triggered {len(triggered)} integration(s): {', '.join(triggered)}",
            task_id=f"sync-all-{datetime.now().timestamp()}",
            error="; ".join(errors) if errors else None
        )

    return router


def add_integrations_routes(app, get_admin_user=None):
    """
    Add integrations routes to FastAPI app

    Args:
        app: FastAPI application instance
        get_admin_user: Optional admin authentication dependency
    """
    router = create_integrations_router(get_admin_user)
    app.include_router(router)
    logger.info("✅ Integrations API routes added")


# Example usage
if __name__ == "__main__":
    print("🔌 NETZ Integrations API Module")
    print("-" * 60)
    print(f"Google Drive: {'✅ Available' if GOOGLE_DRIVE_AVAILABLE else '❌ Not available'}")
    print(f"Gmail:        {'✅ Available' if GMAIL_AVAILABLE else '❌ Not available'}")
    print(f"PennyLane:    {'✅ Available' if PENNYLANE_AVAILABLE else '❌ Not available'}")
    print(f"Wedof:        {'✅ Available' if WEDOF_AVAILABLE else '❌ Not available'}")
    print("\nAPI Endpoints:")
    print("  POST /api/integrations/drive/sync")
    print("  POST /api/integrations/gmail/sync")
    print("  POST /api/integrations/wedof/sync")
    print("  POST /api/integrations/sync-all")
    print("  GET  /api/integrations/status")
    print("  GET  /api/integrations/{integration}/history")
