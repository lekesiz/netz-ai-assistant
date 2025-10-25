"""
Wedof Sync Integration
NETZ AI Project - Completed by YAGO recommendations

Features:
- API key authentication
- Stagiaire (intern) data sync
- Formation (training) schedules
- Contract tracking
- Attendance records
- Incremental updates
- Error handling & retry
- Progress tracking
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WedofSync:
    """
    Wedof API Synchronization Service

    Syncs stagiaire data, formations, and attendance from Wedof
    platform to local database for AI knowledge base.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.wedof.fr/v1",
        sync_history_file: str = "./wedof_sync_history.json",
        max_retries: int = 3
    ):
        """
        Initialize Wedof Sync

        Args:
            api_key: Wedof API key (or from WEDOF_API_KEY env var)
            api_url: Wedof API base URL
            sync_history_file: File to track sync history
            max_retries: Maximum retry attempts for failed requests
        """
        self.api_key = api_key or os.getenv("WEDOF_API_KEY")
        if not self.api_key:
            raise ValueError("Wedof API key is required. Set WEDOF_API_KEY environment variable.")

        self.api_url = api_url.rstrip('/')
        self.sync_history_file = Path(sync_history_file)
        self.max_retries = max_retries
        self.session = None

        # Create sync history file if it doesn't exist
        if not self.sync_history_file.exists():
            self._save_sync_history({})

        logger.info(f"✅ Wedof Sync initialized: {api_url}")

    def _get_session(self) -> requests.Session:
        """Get or create HTTP session with auth headers"""
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
        return self.session

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make HTTP request to Wedof API with retry logic

        Args:
            endpoint: API endpoint path (e.g., "/stagiaires")
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data

        Returns:
            Response data as dict, or None if failed
        """
        url = f"{self.api_url}{endpoint}"
        session = self._get_session()

        for attempt in range(self.max_retries):
            try:
                response = session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    logger.error(f"❌ Authentication failed: Invalid API key")
                    raise
                elif response.status_code == 429:
                    logger.warning(f"⚠️ Rate limited, retry {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    logger.error(f"❌ HTTP error {response.status_code}: {e}")
                    if attempt == self.max_retries - 1:
                        raise

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request failed: {e}")
                if attempt == self.max_retries - 1:
                    return None

        return None

    def _load_sync_history(self) -> Dict:
        """Load sync history from file"""
        try:
            with open(self.sync_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Could not load sync history: {e}")
            return {}

    def _save_sync_history(self, history: Dict):
        """Save sync history to file"""
        try:
            self.sync_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sync_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Could not save sync history: {e}")

    def _should_sync(self, entity_type: str, entity_id: str, modified_at: str) -> bool:
        """
        Check if entity should be synced based on modification time

        Args:
            entity_type: Type of entity (stagiaire, formation, etc.)
            entity_id: Unique ID of entity
            modified_at: ISO format modification timestamp

        Returns:
            True if entity is new or modified since last sync
        """
        history = self._load_sync_history()
        key = f"{entity_type}:{entity_id}"

        if key not in history:
            return True

        last_sync = history[key]
        return modified_at > last_sync

    def _mark_synced(self, entity_type: str, entity_id: str, modified_at: str):
        """Mark entity as synced"""
        history = self._load_sync_history()
        history[f"{entity_type}:{entity_id}"] = modified_at
        self._save_sync_history(history)

    def sync_stagiaires(
        self,
        active_only: bool = True,
        days_back: int = 365
    ) -> List[Dict[str, Any]]:
        """
        Sync stagiaire (intern) data from Wedof

        Args:
            active_only: Only fetch active stagiaires
            days_back: How many days back to fetch

        Returns:
            List of stagiaire records
        """
        logger.info("🔄 Starting stagiaire sync...")

        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        params = {
            "start_date": start_date,
            "status": "active" if active_only else None
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("/stagiaires", params=params)

        if not response or "data" not in response:
            logger.error("❌ Failed to fetch stagiaires")
            return []

        stagiaires = response["data"]
        logger.info(f"📥 Fetched {len(stagiaires)} stagiaire(s)")

        synced_count = 0
        results = []

        for stagiaire in stagiaires:
            try:
                stagiaire_id = stagiaire.get("id")
                modified_at = stagiaire.get("updated_at", stagiaire.get("created_at", ""))

                # Check if sync needed
                if not self._should_sync("stagiaire", stagiaire_id, modified_at):
                    logger.debug(f"⏭️ Skipping stagiaire {stagiaire_id} (already synced)")
                    continue

                # Process stagiaire data
                processed = self._process_stagiaire(stagiaire)
                results.append(processed)

                # Mark as synced
                self._mark_synced("stagiaire", stagiaire_id, modified_at)
                synced_count += 1

                logger.info(f"✅ Synced stagiaire: {processed['full_name']} (ID: {stagiaire_id})")

            except Exception as e:
                logger.error(f"❌ Error processing stagiaire {stagiaire.get('id')}: {e}")
                continue

        logger.info(f"✅ Stagiaire sync complete: {synced_count} new/updated")
        return results

    def _process_stagiaire(self, raw: Dict) -> Dict[str, Any]:
        """
        Process raw stagiaire data into structured format

        Args:
            raw: Raw stagiaire data from Wedof API

        Returns:
            Processed stagiaire dict
        """
        return {
            "stagiaire_id": raw.get("id"),
            "full_name": f"{raw.get('first_name', '')} {raw.get('last_name', '')}".strip(),
            "email": raw.get("email"),
            "phone": raw.get("phone"),
            "status": raw.get("status", "unknown"),
            "start_date": raw.get("start_date"),
            "end_date": raw.get("end_date"),
            "formation_id": raw.get("formation_id"),
            "company": raw.get("company", {}).get("name") if isinstance(raw.get("company"), dict) else raw.get("company"),
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at"),
            "metadata": {
                "address": raw.get("address"),
                "city": raw.get("city"),
                "postal_code": raw.get("postal_code"),
                "birth_date": raw.get("birth_date"),
                "notes": raw.get("notes"),
            }
        }

    def sync_formations(
        self,
        upcoming_only: bool = False,
        days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Sync formation (training) schedules from Wedof

        Args:
            upcoming_only: Only fetch upcoming formations
            days_ahead: How many days ahead to fetch

        Returns:
            List of formation records
        """
        logger.info("🔄 Starting formation sync...")

        params = {}
        if upcoming_only:
            end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            params["end_date_before"] = end_date
            params["start_date_after"] = datetime.now().strftime('%Y-%m-%d')

        response = self._make_request("/formations", params=params)

        if not response or "data" not in response:
            logger.error("❌ Failed to fetch formations")
            return []

        formations = response["data"]
        logger.info(f"📥 Fetched {len(formations)} formation(s)")

        synced_count = 0
        results = []

        for formation in formations:
            try:
                formation_id = formation.get("id")
                modified_at = formation.get("updated_at", formation.get("created_at", ""))

                if not self._should_sync("formation", formation_id, modified_at):
                    logger.debug(f"⏭️ Skipping formation {formation_id} (already synced)")
                    continue

                processed = self._process_formation(formation)
                results.append(processed)

                self._mark_synced("formation", formation_id, modified_at)
                synced_count += 1

                logger.info(f"✅ Synced formation: {processed['title']} (ID: {formation_id})")

            except Exception as e:
                logger.error(f"❌ Error processing formation {formation.get('id')}: {e}")
                continue

        logger.info(f"✅ Formation sync complete: {synced_count} new/updated")
        return results

    def _process_formation(self, raw: Dict) -> Dict[str, Any]:
        """Process raw formation data"""
        return {
            "formation_id": raw.get("id"),
            "title": raw.get("title"),
            "description": raw.get("description"),
            "category": raw.get("category"),
            "start_date": raw.get("start_date"),
            "end_date": raw.get("end_date"),
            "duration_hours": raw.get("duration_hours"),
            "location": raw.get("location"),
            "instructor": raw.get("instructor", {}).get("name") if isinstance(raw.get("instructor"), dict) else raw.get("instructor"),
            "max_participants": raw.get("max_participants"),
            "current_participants": raw.get("current_participants", 0),
            "status": raw.get("status", "scheduled"),
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at"),
            "metadata": {
                "certification": raw.get("certification"),
                "level": raw.get("level"),
                "prerequisites": raw.get("prerequisites"),
                "price": raw.get("price"),
            }
        }

    def sync_attendance(
        self,
        stagiaire_id: Optional[str] = None,
        formation_id: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Sync attendance records from Wedof

        Args:
            stagiaire_id: Filter by specific stagiaire
            formation_id: Filter by specific formation
            days_back: How many days back to fetch

        Returns:
            List of attendance records
        """
        logger.info("🔄 Starting attendance sync...")

        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        params = {
            "start_date": start_date,
            "stagiaire_id": stagiaire_id,
            "formation_id": formation_id
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("/attendance", params=params)

        if not response or "data" not in response:
            logger.error("❌ Failed to fetch attendance")
            return []

        attendance_records = response["data"]
        logger.info(f"📥 Fetched {len(attendance_records)} attendance record(s)")

        results = []
        for record in attendance_records:
            try:
                processed = {
                    "attendance_id": record.get("id"),
                    "stagiaire_id": record.get("stagiaire_id"),
                    "formation_id": record.get("formation_id"),
                    "date": record.get("date"),
                    "status": record.get("status", "unknown"),  # present, absent, excused, late
                    "hours_attended": record.get("hours_attended"),
                    "notes": record.get("notes"),
                    "created_at": record.get("created_at"),
                }
                results.append(processed)
                logger.info(f"✅ Synced attendance: {processed['date']} (ID: {record.get('id')})")

            except Exception as e:
                logger.error(f"❌ Error processing attendance {record.get('id')}: {e}")
                continue

        logger.info(f"✅ Attendance sync complete: {len(results)} records")
        return results

    def sync_contracts(
        self,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Sync contract data from Wedof

        Args:
            active_only: Only fetch active contracts

        Returns:
            List of contract records
        """
        logger.info("🔄 Starting contract sync...")

        params = {}
        if active_only:
            params["status"] = "active"

        response = self._make_request("/contracts", params=params)

        if not response or "data" not in response:
            logger.error("❌ Failed to fetch contracts")
            return []

        contracts = response["data"]
        logger.info(f"📥 Fetched {len(contracts)} contract(s)")

        results = []
        for contract in contracts:
            try:
                processed = {
                    "contract_id": contract.get("id"),
                    "stagiaire_id": contract.get("stagiaire_id"),
                    "type": contract.get("type", "unknown"),  # apprenticeship, internship, etc.
                    "company": contract.get("company", {}).get("name") if isinstance(contract.get("company"), dict) else contract.get("company"),
                    "start_date": contract.get("start_date"),
                    "end_date": contract.get("end_date"),
                    "status": contract.get("status", "unknown"),
                    "signed_date": contract.get("signed_date"),
                    "document_url": contract.get("document_url"),
                    "created_at": contract.get("created_at"),
                    "updated_at": contract.get("updated_at"),
                }
                results.append(processed)
                logger.info(f"✅ Synced contract: {processed['type']} (ID: {contract.get('id')})")

            except Exception as e:
                logger.error(f"❌ Error processing contract {contract.get('id')}: {e}")
                continue

        logger.info(f"✅ Contract sync complete: {len(results)} records")
        return results

    def sync_all(
        self,
        stagiaires: bool = True,
        formations: bool = True,
        attendance: bool = True,
        contracts: bool = True
    ) -> Dict[str, List]:
        """
        Sync all data types from Wedof

        Args:
            stagiaires: Sync stagiaire data
            formations: Sync formation schedules
            attendance: Sync attendance records
            contracts: Sync contracts

        Returns:
            Dict with results for each data type
        """
        logger.info("🚀 Starting full Wedof sync...")
        start_time = datetime.now()

        results = {}

        if stagiaires:
            results["stagiaires"] = self.sync_stagiaires()

        if formations:
            results["formations"] = self.sync_formations()

        if attendance:
            results["attendance"] = self.sync_attendance()

        if contracts:
            results["contracts"] = self.sync_contracts()

        elapsed = (datetime.now() - start_time).total_seconds()

        total_records = sum(len(v) for v in results.values())
        logger.info(f"✅ Full Wedof sync complete: {total_records} total records in {elapsed:.1f}s")

        return results


# Singleton instance
_wedof_sync_instance: Optional[WedofSync] = None

def get_wedof_sync() -> WedofSync:
    """Get singleton Wedof sync instance"""
    global _wedof_sync_instance
    if _wedof_sync_instance is None:
        _wedof_sync_instance = WedofSync()
    return _wedof_sync_instance


# Example usage
if __name__ == "__main__":
    import sys

    # Demo mode with mock data
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("🎭 DEMO MODE: Wedof Sync Integration")
        print("-" * 60)

        # Note: This requires valid Wedof API credentials
        try:
            sync = WedofSync()

            # Sync all data
            results = sync.sync_all()

            print("\n📊 Sync Results:")
            for data_type, records in results.items():
                print(f"  • {data_type}: {len(records)} records")

            print("\n✅ Demo complete!")

        except ValueError as e:
            print(f"❌ Error: {e}")
            print("\n💡 Set WEDOF_API_KEY environment variable to run this demo.")
            print("   export WEDOF_API_KEY=your_api_key_here")

    else:
        print("Usage: python wedof_sync.py --demo")
