"""
Learning and Approval System for User-Contributed Knowledge
Allows users to submit new information that requires admin approval
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class KnowledgeType(str, Enum):
    FACT = "fact"
    PROCEDURE = "procedure"
    DEFINITION = "definition"
    CORRECTION = "correction"
    EXAMPLE = "example"
    REFERENCE = "reference"

class UserContribution(BaseModel):
    """Model for user-contributed knowledge"""
    id: str = Field(default_factory=lambda: hashlib.md5(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12])
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Content
    original_query: str
    user_statement: str
    context: Dict[str, Any]
    knowledge_type: KnowledgeType
    
    # Metadata
    language: str
    confidence_score: float = 0.0
    tags: List[str] = []
    
    # Approval workflow
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewed_by: Optional[str] = None
    review_timestamp: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    # Learning data
    approved_content: Optional[str] = None
    category: Optional[str] = None
    priority: int = 5  # 1-10, higher is more important

class AdminReview(BaseModel):
    """Model for admin review actions"""
    contribution_id: str
    admin_id: str
    action: ApprovalStatus
    approved_content: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []

class LearningApprovalSystem:
    """Manages user contributions and admin approvals"""
    
    def __init__(self):
        self.data_dir = Path("learning_data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.pending_file = self.data_dir / "pending_contributions.json"
        self.approved_file = self.data_dir / "approved_knowledge.json"
        self.rejected_file = self.data_dir / "rejected_contributions.json"
        
        # Load existing data
        self.pending_contributions = self._load_contributions(self.pending_file)
        self.approved_knowledge = self._load_knowledge(self.approved_file)
        self.rejected_contributions = self._load_contributions(self.rejected_file)
        
        # Admin credentials (should be in secure storage)
        self.admin_tokens = {
            "admin_mikail": hashlib.sha256("netz_admin_2025".encode()).hexdigest()
        }
    
    def _load_contributions(self, file_path: Path) -> Dict[str, UserContribution]:
        """Load contributions from file"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    item['id']: UserContribution(**item)
                    for item in data
                }
        return {}
    
    def _load_knowledge(self, file_path: Path) -> List[Dict]:
        """Load approved knowledge"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_contributions(self, contributions: Dict[str, UserContribution], file_path: Path):
        """Save contributions to file"""
        data = [cont.dict() for cont in contributions.values()]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save_knowledge(self):
        """Save approved knowledge"""
        with open(self.approved_file, 'w', encoding='utf-8') as f:
            json.dump(self.approved_knowledge, f, indent=2, default=str)
    
    def extract_knowledge_from_conversation(
        self, 
        user_query: str, 
        ai_response: str, 
        user_feedback: str,
        session_id: str,
        user_id: str = "anonymous"
    ) -> Optional[UserContribution]:
        """Extract potential knowledge from user feedback"""
        
        # Keywords that indicate new information
        learning_indicators = [
            "actually", "correct", "should be", "it's not", "the right answer",
            "en fait", "correct est", "devrait être", "ce n'est pas",
            "aslında", "doğrusu", "olmalı", "değil", "doğru cevap"
        ]
        
        feedback_lower = user_feedback.lower()
        
        # Check if feedback contains learning indicators
        if not any(indicator in feedback_lower for indicator in learning_indicators):
            return None
        
        # Determine knowledge type
        knowledge_type = self._classify_knowledge(user_feedback)
        
        # Detect language
        language = self._detect_language(user_feedback)
        
        # Create contribution
        contribution = UserContribution(
            user_id=user_id,
            session_id=session_id,
            original_query=user_query,
            user_statement=user_feedback,
            context={
                "ai_response": ai_response,
                "conversation_timestamp": datetime.utcnow().isoformat()
            },
            knowledge_type=knowledge_type,
            language=language,
            confidence_score=self._calculate_confidence(user_feedback),
            tags=self._extract_tags(user_query, user_feedback)
        )
        
        # Add to pending
        self.pending_contributions[contribution.id] = contribution
        self._save_contributions(self.pending_contributions, self.pending_file)
        
        logger.info(f"New contribution {contribution.id} added for review")
        
        return contribution
    
    def _classify_knowledge(self, text: str) -> KnowledgeType:
        """Classify the type of knowledge"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["define", "definition", "means", "tanım", "définition"]):
            return KnowledgeType.DEFINITION
        elif any(word in text_lower for word in ["how to", "steps", "procedure", "nasıl", "comment faire"]):
            return KnowledgeType.PROCEDURE
        elif any(word in text_lower for word in ["example", "for instance", "örnek", "exemple"]):
            return KnowledgeType.EXAMPLE
        elif any(word in text_lower for word in ["wrong", "incorrect", "mistake", "yanlış", "incorrect"]):
            return KnowledgeType.CORRECTION
        elif any(word in text_lower for word in ["source", "reference", "kaynak", "référence"]):
            return KnowledgeType.REFERENCE
        else:
            return KnowledgeType.FACT
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Turkish indicators
        turkish_chars = set("çğıöşü")
        if any(char in text.lower() for char in turkish_chars):
            return "tr"
        
        # French indicators
        french_words = {"le", "la", "les", "de", "du", "des", "et", "est", "être", "avoir"}
        words = set(text.lower().split())
        if len(words.intersection(french_words)) >= 2:
            return "fr"
        
        # Default to English
        return "en"
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text characteristics"""
        score = 0.5  # Base score
        
        # Increase for specific phrases
        if any(phrase in text.lower() for phrase in ["i'm sure", "definitely", "certainly", "kesinlikle", "certainement"]):
            score += 0.2
        
        # Increase for detailed explanations
        if len(text.split()) > 20:
            score += 0.1
        
        # Increase for references
        if any(indicator in text for indicator in ["http", "www", "according to", "source:"]):
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_tags(self, query: str, feedback: str) -> List[str]:
        """Extract relevant tags from query and feedback"""
        tags = []
        
        # Technology keywords
        tech_keywords = [
            "python", "javascript", "excel", "wordpress", "autocad",
            "database", "api", "cloud", "security", "network"
        ]
        
        combined_text = f"{query} {feedback}".lower()
        
        for keyword in tech_keywords:
            if keyword in combined_text:
                tags.append(keyword)
        
        return tags
    
    def get_pending_contributions(self, admin_token: str) -> List[UserContribution]:
        """Get all pending contributions for admin review"""
        if not self._verify_admin(admin_token):
            raise ValueError("Invalid admin token")
        
        return list(self.pending_contributions.values())
    
    def review_contribution(
        self, 
        admin_token: str,
        review: AdminReview
    ) -> bool:
        """Review and process a contribution"""
        if not self._verify_admin(admin_token):
            raise ValueError("Invalid admin token")
        
        contribution_id = review.contribution_id
        
        if contribution_id not in self.pending_contributions:
            logger.error(f"Contribution {contribution_id} not found")
            return False
        
        contribution = self.pending_contributions[contribution_id]
        
        # Update contribution with review
        contribution.status = review.action
        contribution.reviewed_by = self._get_admin_id(admin_token)
        contribution.review_timestamp = datetime.utcnow()
        contribution.review_notes = review.notes
        
        if review.action == ApprovalStatus.APPROVED:
            # Process approved contribution
            contribution.approved_content = review.approved_content or contribution.user_statement
            contribution.category = review.category
            contribution.tags.extend(review.tags)
            
            # Add to approved knowledge
            self._add_to_knowledge_base(contribution)
            
            # Move to approved file
            del self.pending_contributions[contribution_id]
            
        elif review.action == ApprovalStatus.REJECTED:
            # Move to rejected
            self.rejected_contributions[contribution_id] = contribution
            del self.pending_contributions[contribution_id]
            self._save_contributions(self.rejected_contributions, self.rejected_file)
        
        # Save changes
        self._save_contributions(self.pending_contributions, self.pending_file)
        
        logger.info(f"Contribution {contribution_id} reviewed: {review.action}")
        
        return True
    
    def _add_to_knowledge_base(self, contribution: UserContribution):
        """Add approved contribution to knowledge base"""
        knowledge_entry = {
            "id": contribution.id,
            "content": contribution.approved_content,
            "metadata": {
                "source": "user_contribution",
                "contributor": contribution.user_id,
                "original_query": contribution.original_query,
                "type": contribution.knowledge_type,
                "language": contribution.language,
                "category": contribution.category,
                "tags": contribution.tags,
                "approved_by": contribution.reviewed_by,
                "approval_date": contribution.review_timestamp.isoformat(),
                "confidence": contribution.confidence_score
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to approved knowledge
        self.approved_knowledge.append(knowledge_entry)
        self._save_knowledge()
        
        # Also update the main knowledge base
        self._update_main_knowledge_base(knowledge_entry)
    
    def _update_main_knowledge_base(self, knowledge_entry: Dict):
        """Update the main simple_api_kb.json with new knowledge"""
        kb_file = Path("simple_api_kb.json")
        
        try:
            # Load existing KB
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
            else:
                kb = {"documents": [], "last_updated": None}
            
            # Add new knowledge as document
            doc = {
                "content": knowledge_entry["content"],
                "metadata": knowledge_entry["metadata"],
                "hash": hashlib.md5(knowledge_entry["content"].encode()).hexdigest(),
                "timestamp": knowledge_entry["timestamp"]
            }
            
            kb["documents"].append(doc)
            kb["last_updated"] = datetime.utcnow().isoformat()
            
            # Save updated KB
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(kb, f, ensure_ascii=False, indent=2)
            
            logger.info("Main knowledge base updated with user contribution")
            
        except Exception as e:
            logger.error(f"Error updating main KB: {e}")
    
    def _verify_admin(self, token: str) -> bool:
        """Verify admin token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash in self.admin_tokens.values()
    
    def _get_admin_id(self, token: str) -> str:
        """Get admin ID from token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        for admin_id, stored_hash in self.admin_tokens.items():
            if stored_hash == token_hash:
                return admin_id
        return "unknown"
    
    def get_statistics(self, admin_token: str) -> Dict:
        """Get learning system statistics"""
        if not self._verify_admin(admin_token):
            raise ValueError("Invalid admin token")
        
        return {
            "pending_count": len(self.pending_contributions),
            "approved_count": len(self.approved_knowledge),
            "rejected_count": len(self.rejected_contributions),
            "knowledge_types": self._count_by_type(),
            "languages": self._count_by_language(),
            "recent_contributions": self._get_recent_contributions(5)
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count contributions by type"""
        counts = {}
        for cont in self.pending_contributions.values():
            counts[cont.knowledge_type] = counts.get(cont.knowledge_type, 0) + 1
        return counts
    
    def _count_by_language(self) -> Dict[str, int]:
        """Count contributions by language"""
        counts = {}
        for cont in self.pending_contributions.values():
            counts[cont.language] = counts.get(cont.language, 0) + 1
        return counts
    
    def _get_recent_contributions(self, limit: int) -> List[Dict]:
        """Get recent contributions"""
        all_contributions = list(self.pending_contributions.values())
        all_contributions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "id": cont.id,
                "timestamp": cont.timestamp.isoformat(),
                "type": cont.knowledge_type,
                "preview": cont.user_statement[:100] + "..." if len(cont.user_statement) > 100 else cont.user_statement
            }
            for cont in all_contributions[:limit]
        ]

# Singleton instance
_learning_system = None

def get_learning_system() -> LearningApprovalSystem:
    """Get learning system instance"""
    global _learning_system
    if _learning_system is None:
        _learning_system = LearningApprovalSystem()
    return _learning_system