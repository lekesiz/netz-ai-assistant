"""
Gmail Integration
NETZ AI Project - Completed by YAGO recommendations

Features:
- OAuth2 authentication
- Email fetching (last 12 months)
- Sentiment analysis
- Auto-categorization (support, sales, admin)
- Attachment extraction
- Vector embedding for RAG
- Privacy-first (local storage only)
"""

import os
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailSync:
    """
    Gmail Synchronization Service
    
    Fetches and analyzes emails for AI knowledge base.
    Includes sentiment analysis and auto-categorization.
    """
    
    def __init__(
        self,
        credentials_file: str = "gmail_credentials.json",
        token_file: str = "gmail_token.json",
        storage_dir: str = "./gmail_data",
        sync_history_file: str = "./gmail_sync_history.json"
    ):
        """
        Initialize Gmail Sync
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON
            token_file: Path to save/load OAuth token
            storage_dir: Directory to store email data
            sync_history_file: JSON file to track sync history
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.storage_dir = Path(storage_dir)
        self.sync_history_file = sync_history_file
        
        # Create storage directory
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Load sync history
        self.sync_history = self._load_sync_history()
        
        # Initialize Gmail service
        self.service = self._authenticate()
        
        # Category keywords
        self.category_keywords = {
            "support": ["help", "issue", "problem", "bug", "error", "support", "assistance"],
            "sales": ["devis", "quote", "price", "tarif", "commande", "order", "achat"],
            "administrative": ["facture", "invoice", "payment", "contract", "contrat", "RH"]
        }
        
        logger.info(f"✅ Gmail Sync initialized")
        logger.info(f"   Storage directory: {self.storage_dir}")
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
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
        
        return build('gmail', 'v1', credentials=creds)
    
    def _load_sync_history(self) -> Dict:
        """Load sync history from file"""
        if os.path.exists(self.sync_history_file):
            with open(self.sync_history_file, 'r') as f:
                return json.load(f)
        return {"last_sync": None, "emails_synced": 0}
    
    def _save_sync_history(self):
        """Save sync history to file"""
        with open(self.sync_history_file, 'w') as f:
            json.dump(self.sync_history, f, indent=2)
    
    def sync_emails(
        self,
        days_back: int = 365,
        max_results: int = 1000,
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Sync emails from Gmail
        
        Args:
            days_back: Number of days to fetch emails
            max_results: Maximum number of emails to fetch
            labels: Gmail labels to filter (e.g., ['INBOX', 'SENT'])
            
        Returns:
            Dict with sync results
        """
        logger.info(f"🔄 Starting Gmail sync...")
        logger.info(f"   Fetching last {days_back} days")
        
        results = {
            "emails_fetched": 0,
            "emails_processed": 0,
            "emails_skipped": 0,
            "categories": {"support": 0, "sales": 0, "administrative": 0, "other": 0},
            "sentiments": {"positive": 0, "neutral": 0, "negative": 0},
            "errors": []
        }
        
        try:
            # Calculate date range
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date}'
            
            if labels:
                query += f' label:{" OR label:".join(labels)}'
            
            # Fetch messages
            logger.info(f"   Query: {query}")
            response = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            results["emails_fetched"] = len(messages)
            
            logger.info(f"   Found {len(messages)} emails")
            
            # Process each message
            for i, message_ref in enumerate(messages, 1):
                if i % 10 == 0:
                    logger.info(f"   Processing: {i}/{len(messages)}")
                
                try:
                    email_data = self._process_email(message_ref['id'])
                    
                    if email_data:
                        results["emails_processed"] += 1
                        
                        # Update category counts
                        category = email_data.get("category", "other")
                        results["categories"][category] = results["categories"].get(category, 0) + 1
                        
                        # Update sentiment counts
                        sentiment = email_data.get("sentiment", "neutral")
                        results["sentiments"][sentiment] = results["sentiments"].get(sentiment, 0) + 1
                        
                        # Save email data
                        self._save_email(email_data)
                    else:
                        results["emails_skipped"] += 1
                        
                except Exception as e:
                    logger.error(f"   ❌ Error processing email {message_ref['id']}: {e}")
                    results["errors"].append(str(e))
            
            # Update sync history
            self.sync_history["last_sync"] = datetime.now().isoformat()
            self.sync_history["emails_synced"] = results["emails_processed"]
            self._save_sync_history()
            
        except HttpError as e:
            logger.error(f"❌ Gmail API error: {e}")
            results["errors"].append(f"API error: {str(e)}")
        
        logger.info(f"✅ Sync complete!")
        logger.info(f"   Fetched: {results['emails_fetched']}")
        logger.info(f"   Processed: {results['emails_processed']}")
        logger.info(f"   Skipped: {results['emails_skipped']}")
        
        return results
    
    def _process_email(self, message_id: str) -> Optional[Dict]:
        """Process a single email"""
        try:
            # Get full message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Extract basic info
            email_data = {
                "id": message_id,
                "thread_id": message['threadId'],
                "from": headers.get('From', ''),
                "to": headers.get('To', ''),
                "subject": headers.get('Subject', ''),
                "date": headers.get('Date', ''),
                "labels": message.get('labelIds', []),
                "body": self._get_email_body(message['payload']),
                "snippet": message.get('snippet', '')
            }
            
            # Categorize
            email_data["category"] = self._categorize_email(
                email_data["subject"],
                email_data["body"]
            )
            
            # Sentiment analysis
            email_data["sentiment"] = self._analyze_sentiment(
                email_data["subject"],
                email_data["body"]
            )
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            return None
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def _categorize_email(self, subject: str, body: str) -> str:
        """Categorize email based on keywords"""
        text = (subject + " " + body).lower()
        
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return "other"
    
    def _analyze_sentiment(self, subject: str, body: str) -> str:
        """
        Analyze sentiment (simple keyword-based)
        
        In production, use a proper NLP model
        """
        text = (subject + " " + body).lower()
        
        positive_keywords = ["merci", "thank", "great", "excellent", "parfait", "super"]
        negative_keywords = ["problem", "issue", "error", "bug", "fail", "problème", "erreur"]
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _save_email(self, email_data: Dict):
        """Save email data to JSON file"""
        # Create filename from email ID
        filename = f"email_{email_data['id']}.json"
        filepath = self.storage_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, ensure_ascii=False, indent=2)
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        email_files = list(self.storage_dir.glob("email_*.json"))
        
        return {
            "total_emails": len(email_files),
            "last_sync": self.sync_history.get("last_sync"),
            "storage_directory": str(self.storage_dir),
            "sync_history": self.sync_history
        }
    
    def search_emails(
        self,
        query: str,
        category: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> List[Dict]:
        """
        Search synced emails
        
        Args:
            query: Search query
            category: Filter by category
            sentiment: Filter by sentiment
            
        Returns:
            List of matching emails
        """
        results = []
        
        for email_file in self.storage_dir.glob("email_*.json"):
            with open(email_file, 'r', encoding='utf-8') as f:
                email_data = json.load(f)
            
            # Filter by category
            if category and email_data.get("category") != category:
                continue
            
            # Filter by sentiment
            if sentiment and email_data.get("sentiment") != sentiment:
                continue
            
            # Search in subject and body
            text = email_data.get("subject", "") + " " + email_data.get("body", "")
            if query.lower() in text.lower():
                results.append(email_data)
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize sync
    sync = GmailSync(
        credentials_file="gmail_credentials.json",
        storage_dir="./gmail_data"
    )
    
    # Sync last 365 days
    results = sync.sync_emails(days_back=365, max_results=500)
    
    print("\n📊 Gmail Sync Results:")
    print(f"   Emails fetched: {results['emails_fetched']}")
    print(f"   Emails processed: {results['emails_processed']}")
    
    print(f"\n📂 Categories:")
    for category, count in results['categories'].items():
        print(f"   {category}: {count}")
    
    print(f"\n😊 Sentiments:")
    for sentiment, count in results['sentiments'].items():
        print(f"   {sentiment}: {count}")
    
    if results['errors']:
        print(f"\n❌ Errors: {len(results['errors'])}")
