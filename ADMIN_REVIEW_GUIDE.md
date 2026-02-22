# 🎯 Admin Review & Feedback System (v2.2)

## Overview

The Admin Review & Feedback System adds quality control and governance to FederX, allowing administrators to review, approve, reject, or request improvements for client updates before they are aggregated into the global model.

## Key Features

### 1. **Review Workflow**

Client updates can have the following statuses:

- **PENDING_REVIEW** - Awaiting admin decision
- **APPROVED** - Admin approved, aggregated into global model
- **REJECTED** - Admin rejected, not aggregated
- **NEEDS_IMPROVEMENT** - Admin requests changes, not aggregated (client can resubmit)
- **AUTO_APPROVED** - Automatically approved based on trust score

### 2. **Auto-Approval & Auto-Rejection**

The system can automatically handle updates based on client trust scores:

- **Auto-Approve**: Clients with trust ≥ 0.8 are automatically approved
- **Auto-Reject**: Clients with trust < 0.3 are automatically rejected
- Configurable thresholds per experiment

### 3. **Admin Review Capabilities**

Admins can:

- View pending reviews with client metadata (trust score, staleness, etc.)
- Approve/reject/request improvements with detailed feedback
- Provide actionable improvement suggestions as a list
- Track aggregation status (whether update was used in global model)

### 4. **Client Feedback API**

Clients can:

- Fetch all feedback for their submitted updates
- See review status, admin comments, and improvement suggestions
- Know if their update was aggregated into the global model

## API Endpoints

### Admin Endpoints

#### Get Pending Reviews

```http
GET /experiment/{exp_id}/pending-reviews
```

Returns list of updates awaiting admin review with metadata:

```json
[
  {
    "update_id": "upd_0",
    "experiment_id": "exp_0",
    "client_id": "client_bob",
    "submitted_at": "2026-02-22T03:09:00",
    "model_version": 0,
    "cluster_id": "cluster_0",
    "staleness": 0,
    "trust_score": 1.0,
    "num_samples": 200,
    "metadata": {}
  }
]
```

#### Submit Review

```http
POST /experiment/{exp_id}/update/{update_id}/review
```

Request body:

```json
{
  "status": "approved", // or "rejected", "needs_improvement"
  "feedback": "Great update! High quality gradients.",
  "admin_id": "admin_alice",
  "suggestions": ["Add L2 regularization", "Reduce learning rate"]
}
```

Response:

```json
{
  "update_id": "upd_0",
  "review_status": "approved",
  "feedback": "Great update! High quality gradients.",
  "reviewed_at": "2026-02-22T03:10:00",
  "will_aggregate": true
}
```

#### Get Review Status

```http
GET /experiment/{exp_id}/update/{update_id}/review-status
```

### Client Endpoints

#### Get All Feedback

```http
GET /experiment/{exp_id}/client/{client_id}/feedback
```

Returns all feedback items for a client:

```json
[
  {
    "update_id": "upd_0",
    "experiment_id": "exp_0",
    "submitted_at": "2026-02-22T03:09:00",
    "review_status": "approved",
    "feedback": "Great update!",
    "reviewed_at": "2026-02-22T03:10:00",
    "admin_id": "admin_alice",
    "suggestions": [],
    "aggregated": true
  }
]
```

#### Get Update Feedback

```http
GET /experiment/{exp_id}/update/{update_id}/feedback
```

## Configuration

When creating an experiment, configure review settings:

```python
response = requests.post(
    f"{BASE_URL}/experiment/create",
    json={
        "name": "My Experiment",
        "require_admin_review": True,  # Require manual review
        "auto_approve_trusted": True,  # Auto-approve high trust clients
        "auto_approve_threshold": 0.8,  # Trust threshold for auto-approval
        "auto_reject_low_trust": True,  # Auto-reject low trust clients
        "auto_reject_threshold": 0.3,   # Trust threshold for auto-rejection
        # ... other settings
    }
)
```

### Review Modes

#### Mode 1: Full Manual Review

All updates require admin review:

```python
{
  "require_admin_review": True,
  "auto_approve_trusted": False,
  "auto_reject_low_trust": False
}
```

#### Mode 2: Auto-Only (No Manual Review)

All updates handled automatically:

```python
{
  "require_admin_review": False,
  "auto_approve_trusted": True,
  "auto_reject_low_trust": True
}
```

#### Mode 3: Mixed (Recommended)

Trusted clients auto-approved, others require manual review:

```python
{
  "require_admin_review": True,   # Manual for medium trust
  "auto_approve_trusted": True,   # Auto for high trust (>= 0.8)
  "auto_reject_low_trust": True   # Auto for low trust (< 0.3)
}
```

## Demo

Run the comprehensive demo:

```bash
python demo_admin_review.py
```

This demonstrates 3 scenarios:

1. **Manual Review Workflow** - Admin approves one update, requests improvement on another
2. **Auto-Approval/Rejection** - System automatically handles updates based on trust
3. **Mixed Mode** - Combination of auto and manual review

## Testing

Run the test suite:

```bash
python test_admin_review.py
```

Tests cover:

- ✅ Manual review workflow
- ✅ Auto-approval for trusted clients
- ✅ Needs improvement workflow
- ✅ Rejection workflow
- ✅ Mixed review mode
- ✅ Pending reviews listing

**All 6 tests passing ✅**

## Use Cases

### 1. Research & Development

Manual review all updates to ensure quality and debug issues:

```python
{
  "require_admin_review": True,
  "auto_approve_trusted": False,
  "auto_reject_low_trust": False
}
```

### 2. Production Deployment

Auto-approve trusted clients, manual review for new/suspicious clients:

```python
{
  "require_admin_review": True,
  "auto_approve_trusted": True,
  "auto_approve_threshold": 0.85,
  "auto_reject_low_trust": True,
  "auto_reject_threshold": 0.25
}
```

### 3. Competitive FL

Strict quality control with improvement feedback:

```python
{
  "require_admin_review": True,
  "auto_approve_trusted": False,  # Review even trusted clients
  "auto_reject_low_trust": True
}
```

## Architecture

### Data Models

```python
class ReviewStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_IMPROVEMENT = "needs_improvement"
    AUTO_APPROVED = "auto_approved"

class AdminReviewRequest(BaseModel):
    status: ReviewStatus
    feedback: str
    admin_id: str
    suggestions: Optional[List[str]]

class ClientFeedbackItem(BaseModel):
    update_id: str
    experiment_id: str
    submitted_at: str
    review_status: ReviewStatus
    feedback: Optional[str]
    reviewed_at: Optional[str]
    admin_id: Optional[str]
    suggestions: Optional[List[str]]
    aggregated: bool
```

### Integration with Aggregation

Only approved updates are aggregated:

```python
def _aggregate_updates(exp_id: str, cluster_id: str):
    # Filter for approved updates
    cluster_updates = [
        u for u in pending_updates[exp_id]
        if u["cluster_id"] == cluster_id
        and not u.get("rejected", False)
        and not u.get("aggregated", False)
        and u.get("review_status") in [ReviewStatus.APPROVED, ReviewStatus.AUTO_APPROVED]
    ]

    # Aggregate only approved updates
    # ...
```

## Benefits

1. **Quality Control** - Ensure only high-quality updates are used
2. **Security** - Prevent malicious updates from corrupting the model
3. **Compliance** - Audit trail of all reviews and decisions
4. **Client Improvement** - Actionable feedback helps clients improve
5. **Flexibility** - Configurable auto/manual review per experiment
6. **Scalability** - Auto-approval reduces manual workload for trusted clients

## Version History

- **v2.2** (Feb 22, 2026) - Initial release of admin review & feedback system
  - 5 review statuses
  - Auto-approval/rejection based on trust
  - Admin review endpoints
  - Client feedback endpoints
  - 6 comprehensive tests
  - Demo with 3 scenarios

## Next Steps

Planned enhancements for v2.3:

- [ ] Review analytics dashboard
- [ ] Bulk review operations (approve/reject multiple)
- [ ] Review templates (common feedback messages)
- [ ] Review assignment (multiple admins)
- [ ] SLA tracking (review response time)
- [ ] Client appeal process for rejections

---

**Documentation Complete** ✅  
**All Tests Passing** ✅  
**Demo Working** ✅  
**Production Ready** ✅
