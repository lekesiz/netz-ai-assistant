"""
Admin API for Knowledge Management and Approval System
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging

from learning_approval_system import (
    LearningApprovalSystem,
    UserContribution,
    AdminReview,
    ApprovalStatus,
    get_learning_system
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NETZ Admin API - Knowledge Management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    admin_id: str
    message: str

class ContributionResponse(BaseModel):
    contributions: List[Dict]
    total: int
    pending: int
    approved: int
    rejected: int

class ReviewRequest(BaseModel):
    contribution_id: str
    action: str  # "approve", "reject", "review"
    approved_content: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []

class BulkReviewRequest(BaseModel):
    contribution_ids: List[str]
    action: str
    category: Optional[str] = None
    notes: Optional[str] = None

def verify_admin_token(x_admin_token: str = Header(...)) -> str:
    """Verify admin token from header"""
    learning_system = get_learning_system()
    if not learning_system._verify_admin(x_admin_token):
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return x_admin_token

@app.post("/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """Admin login endpoint"""
    # Simple authentication (in production, use proper auth)
    if request.username == "mikail" and request.password == "netz_admin_2025":
        return LoginResponse(
            token="netz_admin_2025",
            admin_id="admin_mikail",
            message="Login successful"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/admin/contributions", response_model=ContributionResponse)
async def get_contributions(
    status: Optional[str] = "pending",
    admin_token: str = Depends(verify_admin_token)
):
    """Get contributions for review"""
    try:
        learning_system = get_learning_system()
        
        # Get statistics
        stats = learning_system.get_statistics(admin_token)
        
        # Get contributions based on status
        if status == "pending":
            contributions = learning_system.get_pending_contributions(admin_token)
        else:
            contributions = []  # TODO: Implement approved/rejected retrieval
        
        # Convert to dict for response
        contribution_dicts = []
        for cont in contributions:
            cont_dict = cont.dict()
            # Add preview
            cont_dict["preview"] = cont.user_statement[:200] + "..." if len(cont.user_statement) > 200 else cont.user_statement
            contribution_dicts.append(cont_dict)
        
        return ContributionResponse(
            contributions=contribution_dicts,
            total=len(contribution_dicts),
            pending=stats["pending_count"],
            approved=stats["approved_count"],
            rejected=stats["rejected_count"]
        )
        
    except Exception as e:
        logger.error(f"Error getting contributions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/review")
async def review_contribution(
    request: ReviewRequest,
    admin_token: str = Depends(verify_admin_token)
):
    """Review a single contribution"""
    try:
        learning_system = get_learning_system()
        
        # Map action to status
        action_map = {
            "approve": ApprovalStatus.APPROVED,
            "reject": ApprovalStatus.REJECTED,
            "review": ApprovalStatus.UNDER_REVIEW
        }
        
        if request.action not in action_map:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Create review
        review = AdminReview(
            contribution_id=request.contribution_id,
            admin_id="admin_mikail",  # Get from token in production
            action=action_map[request.action],
            approved_content=request.approved_content,
            category=request.category,
            notes=request.notes,
            tags=request.tags
        )
        
        # Process review
        success = learning_system.review_contribution(admin_token, review)
        
        if success:
            return {
                "status": "success",
                "message": f"Contribution {request.contribution_id} {request.action}ed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Contribution not found")
            
    except Exception as e:
        logger.error(f"Error reviewing contribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/bulk-review")
async def bulk_review(
    request: BulkReviewRequest,
    admin_token: str = Depends(verify_admin_token)
):
    """Bulk review multiple contributions"""
    try:
        learning_system = get_learning_system()
        
        # Map action to status
        action_map = {
            "approve": ApprovalStatus.APPROVED,
            "reject": ApprovalStatus.REJECTED
        }
        
        if request.action not in action_map:
            raise HTTPException(status_code=400, detail="Invalid action for bulk review")
        
        processed = 0
        errors = []
        
        for cont_id in request.contribution_ids:
            try:
                review = AdminReview(
                    contribution_id=cont_id,
                    admin_id="admin_mikail",
                    action=action_map[request.action],
                    category=request.category,
                    notes=request.notes
                )
                
                if learning_system.review_contribution(admin_token, review):
                    processed += 1
                else:
                    errors.append(cont_id)
                    
            except Exception as e:
                errors.append(f"{cont_id}: {str(e)}")
        
        return {
            "status": "success",
            "processed": processed,
            "total": len(request.contribution_ids),
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error in bulk review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/statistics")
async def get_statistics(admin_token: str = Depends(verify_admin_token)):
    """Get learning system statistics"""
    try:
        learning_system = get_learning_system()
        stats = learning_system.get_statistics(admin_token)
        
        return {
            "status": "success",
            "statistics": stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/categories")
async def get_categories(admin_token: str = Depends(verify_admin_token)):
    """Get available categories for knowledge"""
    return {
        "categories": [
            {"id": "technical", "name": "Technical Knowledge", "description": "Programming, software, systems"},
            {"id": "business", "name": "Business Information", "description": "Finance, management, operations"},
            {"id": "training", "name": "Training Content", "description": "Courses, certifications, pedagogy"},
            {"id": "company", "name": "Company Information", "description": "NETZ specific data"},
            {"id": "general", "name": "General Knowledge", "description": "Other useful information"}
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "admin_api",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)  # Different port for admin API