"""
Admin Review & Client Feedback Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ReviewStatus(str, Enum):
    """Status of an update review"""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_IMPROVEMENT = "needs_improvement"
    AUTO_APPROVED = "auto_approved"  # Bypassed review


class AdminReviewRequest(BaseModel):
    """Admin's review of a client update"""
    status: ReviewStatus
    feedback: str = Field(..., min_length=1, max_length=1000)
    admin_id: str = "admin"
    suggestions: Optional[List[str]] = None  # Specific improvement suggestions


class AdminReviewResponse(BaseModel):
    """Response after admin reviews an update"""
    update_id: str
    review_status: ReviewStatus
    feedback: str
    reviewed_at: str
    will_aggregate: bool  # Whether update will be used in aggregation


class ClientFeedbackItem(BaseModel):
    """Feedback item for a specific update"""
    update_id: str
    experiment_id: str
    submitted_at: str
    review_status: ReviewStatus
    feedback: Optional[str] = None
    reviewed_at: Optional[str] = None
    admin_id: Optional[str] = None
    suggestions: Optional[List[str]] = None
    aggregated: bool  # Whether update was used in global model


class PendingUpdateSummary(BaseModel):
    """Summary of an update pending review"""
    update_id: str
    experiment_id: str
    client_id: str
    submitted_at: str
    model_version: int
    cluster_id: str
    staleness: int
    trust_score: float
    num_samples: Optional[int] = None
    metadata: Optional[dict] = None


class ExperimentReviewConfig(BaseModel):
    """Configure review requirements for an experiment"""
    require_admin_review: bool = False  # If True, all updates need admin approval
    auto_approve_trusted: bool = True  # Auto-approve if trust > threshold
    auto_approve_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    auto_reject_low_trust: bool = True  # Auto-reject if trust < threshold
    auto_reject_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
