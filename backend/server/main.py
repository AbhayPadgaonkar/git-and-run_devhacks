"""FastAPI server for federated learning"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime
import json
import os
from pathlib import Path

from ..aggregation import (
    FedAvgAggregator, MedianAggregator, 
    TrimmedMeanAggregator, TrustWeightedAggregator
)
from ..trust import MaliciousDetector, TrustScorer
from ..clustering import ClusterManager
from ..utils.serialization import (
    serialize_weights, deserialize_weights, 
    save_weights_to_file, load_weights_from_file,
    flatten_weights
)
from ..utils.logger import get_logger
from ..models.review import (
    ReviewStatus, AdminReviewRequest, AdminReviewResponse,
    ClientFeedbackItem, PendingUpdateSummary, ExperimentReviewConfig
)

logger = get_logger(__name__)

app = FastAPI(
    title="FederX - Federated Learning Server",
    description="Asynchronous federated learning with robust aggregation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# In-memory storage (will replace with Firestore later)
experiments: Dict[str, Dict] = {}
global_models: Dict[str, Dict[str, Any]] = {}  # {exp_id: {cluster_id: model_data}}
pending_updates: Dict[str, List[Dict]] = {}  # {exp_id: [updates]}
trust_scorers: Dict[str, TrustScorer] = {}
cluster_managers: Dict[str, ClusterManager] = {}
malicious_detectors: Dict[str, MaliciousDetector] = {}

# Review system storage
update_reviews: Dict[str, Dict] = {}  # {update_id: review_data}
pending_reviews: Dict[str, List[str]] = {}  # {exp_id: [update_ids]}
experiment_review_configs: Dict[str, ExperimentReviewConfig] = {}  # {exp_id: config}


# ============ Request/Response Models ============

class ExperimentConfig(BaseModel):
    name: str
    aggregation_method: str = Field(default="fedavg", pattern="^(fedavg|median|trimmed_mean|trust_weighted)$")
    enable_trust: bool = True
    enable_clustering: bool = False
    trust_alpha: float = Field(default=0.8, ge=0.0, le=1.0)
    cluster_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    initial_weights: Optional[str] = None  # Base64 encoded weights
    max_staleness: int = Field(default=5, ge=0)  # Max allowed version staleness (0 = strict)
    staleness_weighting: bool = Field(default=True)  # Reduce weight of stale updates
    # Review system configuration
    require_admin_review: bool = Field(default=False)  # Require admin review for all updates
    auto_approve_trusted: bool = Field(default=True)  # Auto-approve high trust clients
    auto_approve_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    auto_reject_low_trust: bool = Field(default=True)  # Auto-reject low trust clients
    auto_reject_threshold: float = Field(default=0.3, ge=0.0, le=1.0)


class UpdateRequest(BaseModel):
    client_id: str
    delta_weights: str  # Base64 encoded
    model_version: int


class UpdateResponse(BaseModel):
    update_id: str
    status: str
    cluster_id: str
    accepted: bool
    trust_score: float
    message: Optional[str] = None
    new_global_version: Optional[int] = None  # Version after async aggregation
    staleness: Optional[int] = None  # How many versions behind client was
    staleness_weight: Optional[float] = None  # Weight applied due to staleness
    review_status: Optional[str] = None  # Review status (pending_review, approved, etc.)


class GlobalModelResponse(BaseModel):
    version: int
    cluster_id: str
    weights: str  # Base64 encoded
    timestamp: str


class UpdateWeightsResponse(BaseModel):
    """Response containing complete update weights for external hashing/verification"""
    update_id: str
    client_id: str
    experiment_id: str
    cluster_id: str
    weights: str  # Base64 encoded delta weights
    timestamp: str
    base_version: int
    staleness: int
    trust_score: float
    review_status: str


# ============ API Endpoints ============

@app.get("/")
def root():
    return {
        "service": "FederX Federated Learning Server",
        "status": "running",
        "experiments": len(experiments)
    }


@app.post("/experiment/create")
def create_experiment(config: ExperimentConfig):
    """Create new federated learning experiment"""
    exp_id = f"exp_{len(experiments)}"
    
    # Create experiment directory
    exp_dir = DATA_DIR / exp_id
    exp_dir.mkdir(exist_ok=True)
    (exp_dir / "global_models").mkdir(exist_ok=True)
    (exp_dir / "updates").mkdir(exist_ok=True)
    
    # Initialize experiment
    experiments[exp_id] = {
        "id": exp_id,
        "config": config.dict(),
        "status": "running",
        "created_at": datetime.utcnow().isoformat(),
        "total_updates": 0,
        "accepted_updates": 0,
        "rejected_updates": 0
    }
    
    # Initialize global model
    if config.initial_weights:
        initial_weights = deserialize_weights(config.initial_weights)
    else:
        # None indicates no initial model - first aggregation will set it
        initial_weights = None
    
    global_models[exp_id] = {
        "cluster_0": {
            "version": 0,
            "weights": initial_weights,
            "last_updated": datetime.utcnow().isoformat()
        }
    }
    
    # Save initial weights if provided
    if initial_weights:
        save_weights_to_file(
            initial_weights, 
            exp_dir / "global_models" / "cluster_0_v0.pkl"
        )
    
    # Initialize components
    pending_updates[exp_id] = []
    trust_scorers[exp_id] = TrustScorer(alpha=config.trust_alpha)
    cluster_managers[exp_id] = ClusterManager(
        similarity_threshold=config.cluster_similarity_threshold
    )
    malicious_detectors[exp_id] = MaliciousDetector()
    
    # Initialize review system
    pending_reviews[exp_id] = []
    experiment_review_configs[exp_id] = ExperimentReviewConfig(
        require_admin_review=config.require_admin_review,
        auto_approve_trusted=config.auto_approve_trusted,
        auto_approve_threshold=config.auto_approve_threshold,
        auto_reject_low_trust=config.auto_reject_low_trust,
        auto_reject_threshold=config.auto_reject_threshold
    )
    
    logger.info(f"Created experiment {exp_id}: {config.name}")
    
    return {
        "experiment_id": exp_id,
        "status": "created",
        "config": config.dict()
    }


@app.get("/experiment/{exp_id}/status")
def get_experiment_status(exp_id: str):
    """Get experiment status"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    exp = experiments[exp_id]
    clusters = cluster_managers[exp_id].get_all_clusters()
    
    cluster_info = {}
    for cluster_id in global_models.get(exp_id, {}).keys():
        cluster_info[cluster_id] = {
            "version": global_models[exp_id][cluster_id]["version"],
            "client_count": len(clusters.get(cluster_id, {}).get("clients", [])),
            "last_updated": global_models[exp_id][cluster_id]["last_updated"]
        }
    
    return {
        **exp,
        "clusters": cluster_info,
        "pending_updates": len(pending_updates.get(exp_id, [])),
        "trust_scores": trust_scorers[exp_id].get_all_scores()
    }


@app.get("/experiment/{exp_id}/global-model")
def get_global_model(exp_id: str, cluster_id: str = "cluster_0") -> GlobalModelResponse:
    """Get current global model for a cluster"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    if cluster_id not in global_models.get(exp_id, {}):
        # Return cluster_0 as default
        cluster_id = "cluster_0"
    
    model_data = global_models[exp_id][cluster_id]
    
    # Serialize weights (empty dict if None)
    weights_to_send = model_data["weights"] if model_data["weights"] is not None else {}
    
    return GlobalModelResponse(
        version=model_data["version"],
        cluster_id=cluster_id,
        weights=serialize_weights(weights_to_send),
        timestamp=model_data["last_updated"]
    )


@app.post("/experiment/{exp_id}/submit-update")
def submit_update(exp_id: str, update: UpdateRequest) -> UpdateResponse:
    """Submit client update"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    config = experiments[exp_id]["config"]
    update_id = f"upd_{experiments[exp_id]['total_updates']}"
    
    try:
        # Deserialize delta weights
        delta_weights = deserialize_weights(update.delta_weights)
        
        # Assign cluster (if enabled)
        if config["enable_clustering"]:
            cluster_id = cluster_managers[exp_id].assign_cluster(
                update.client_id, delta_weights
            )
        else:
            cluster_id = "cluster_0"
        
        # Ensure cluster exists in global models
        if cluster_id not in global_models[exp_id]:
            global_models[exp_id][cluster_id] = {
                "version": 0,
                "weights": {},
                "last_updated": datetime.utcnow().isoformat()
            }
        
        # Check staleness
        current_global_version = global_models[exp_id][cluster_id]["version"]
        staleness = current_global_version - update.model_version
        
        # Add to pending updates
        update_data = {
            "update_id": update_id,
            "client_id": update.client_id,
            "cluster_id": cluster_id,
            "delta_weights": delta_weights,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False,
            "base_version": update.model_version,  # Version client trained from
            "staleness": staleness
        }
        
        pending_updates[exp_id].append(update_data)
        experiments[exp_id]["total_updates"] += 1
        
        # Process update immediately for now (async aggregation later)
        result = _process_update(exp_id, update_data)
        
        logger.info(f"Update {update_id} from {update.client_id} - Accepted: {result['accepted']}")
        
        return UpdateResponse(
            update_id=update_id,
            status="processed",
            cluster_id=cluster_id,
            accepted=result["accepted"],
            trust_score=result["trust_score"],
            message=result.get("message"),
            new_global_version=result.get("new_global_version"),
            staleness=result.get("staleness"),
            staleness_weight=result.get("staleness_weight"),
            review_status=result.get("review_status")
        )
        
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _process_update(exp_id: str, update_data: Dict) -> Dict:
    """Process a single update (malicious detection + aggregation + staleness check)"""
    config = experiments[exp_id]["config"]
    cluster_id = update_data["cluster_id"]
    client_id = update_data["client_id"]
    delta_weights = update_data["delta_weights"]
    staleness = update_data["staleness"]
    
    # Check staleness threshold
    max_staleness = config.get("max_staleness", 5)
    if staleness > max_staleness:
        experiments[exp_id]["rejected_updates"] += 1
        update_data["rejected"] = True
        return {
            "accepted": False,
            "trust_score": 1.0,
            "message": f"Rejected: Update too stale (staleness={staleness}, max={max_staleness})",
            "staleness": staleness
        }
    
    # Get all recent updates for this cluster (for detection)
    cluster_updates = [
        u["delta_weights"] for u in pending_updates[exp_id]
        if u["cluster_id"] == cluster_id and not u.get("rejected", False)
    ]
    
    # Malicious detection (skip for initialization updates)
    is_malicious = False
    detection_metrics = {}
    is_init = client_id.startswith("init_") or client_id == "server_init"
    
    if config["enable_trust"] and len(cluster_updates) >= 3 and not is_init:
        detector = malicious_detectors[exp_id]
        is_malicious, detection_metrics = detector.detect(delta_weights, cluster_updates)
    
    # Update trust score
    trust_scorer = trust_scorers[exp_id]
    trust_scorer.update_trust(client_id, is_malicious)
    trust_score = trust_scorer.get_trust(client_id)
    
    # Accept or reject based on malicious detection
    accepted = not is_malicious
    
    if not accepted:
        experiments[exp_id]["rejected_updates"] += 1
        update_data["rejected"] = True
        return {
            "accepted": False,
            "trust_score": trust_score,
            "message": f"Rejected: {detection_metrics.get('flags', [])}",
            "metrics": detection_metrics
        }
    
    # ============ ADMIN REVIEW SYSTEM ============
    review_config = experiment_review_configs[exp_id]
    review_status = ReviewStatus.PENDING_REVIEW
    review_message = ""
    
    # Auto-reject low trust clients
    if review_config.auto_reject_low_trust and trust_score < review_config.auto_reject_threshold:
        review_status = ReviewStatus.REJECTED
        review_message = f"Auto-rejected: trust score {trust_score:.2f} < {review_config.auto_reject_threshold}"
        experiments[exp_id]["rejected_updates"] += 1
        update_data["rejected"] = True
        update_data["review_status"] = review_status
        
        # Store review data
        update_reviews[update_data["update_id"]] = {
            "experiment_id": exp_id,
            "update_id": update_data["update_id"],
            "client_id": client_id,
            "status": review_status,
            "feedback": review_message,
            "reviewed_at": datetime.utcnow().isoformat(),
            "admin_id": "auto_system",
            "trust_score": trust_score,
            "aggregated": False
        }
        
        return {
            "accepted": False,
            "trust_score": trust_score,
            "message": review_message,
            "review_status": review_status
        }
    
    # Auto-approve high trust clients
    if review_config.auto_approve_trusted and trust_score >= review_config.auto_approve_threshold:
        review_status = ReviewStatus.AUTO_APPROVED
        review_message = f"Auto-approved: trust score {trust_score:.2f} >= {review_config.auto_approve_threshold}"
        update_data["review_status"] = review_status
        
        # Store review data
        update_reviews[update_data["update_id"]] = {
            "experiment_id": exp_id,
            "update_id": update_data["update_id"],
            "client_id": client_id,
            "status": review_status,
            "feedback": review_message,
            "reviewed_at": datetime.utcnow().isoformat(),
            "admin_id": "auto_system",
            "trust_score": trust_score,
            "aggregated": False  # Will be set to True after aggregation
        }
    
    # Require manual review
    elif review_config.require_admin_review:
        review_status = ReviewStatus.PENDING_REVIEW
        review_message = "Awaiting admin review"
        update_data["review_status"] = review_status
        pending_reviews[exp_id].append(update_data["update_id"])
        
        # Store review data
        update_reviews[update_data["update_id"]] = {
            "experiment_id": exp_id,
            "update_id": update_data["update_id"],
            "client_id": client_id,
            "status": review_status,
            "submitted_at": update_data["timestamp"],
            "trust_score": trust_score,
            "staleness": staleness,
            "cluster_id": cluster_id,
            "model_version": update_data["base_version"],
            "aggregated": False
        }
        
        return {
            "accepted": True,
            "trust_score": trust_score,
            "message": review_message,
            "review_status": review_status,
            "staleness": staleness
        }
    
    # No review required - auto approve
    else:
        review_status = ReviewStatus.AUTO_APPROVED
        review_message = "Auto-approved: no review required"
        update_data["review_status"] = review_status
        
        # Store review data
        update_reviews[update_data["update_id"]] = {
            "experiment_id": exp_id,
            "update_id": update_data["update_id"],
            "client_id": client_id,
            "status": review_status,
            "feedback": review_message,
            "reviewed_at": datetime.utcnow().isoformat(),
            "admin_id": "auto_system",
            "trust_score": trust_score,
            "aggregated": False
        }
    
    experiments[exp_id]["accepted_updates"] += 1
    
    # Calculate staleness weight (if enabled)
    staleness_weight = 1.0
    if config.get("staleness_weighting", True) and staleness > 0:
        # Exponential decay: weight = 0.9^staleness
        # staleness=1 → 0.9, staleness=2 → 0.81, staleness=3 → 0.73
        staleness_weight = 0.9 ** staleness
        update_data["staleness_weight"] = staleness_weight
    
    # ✨ ASYNC AGGREGATION - Only aggregate if approved
    if review_status in [ReviewStatus.APPROVED, ReviewStatus.AUTO_APPROVED]:
        _aggregate_updates(exp_id, cluster_id)
        
        # Mark as aggregated in review
        if update_data["update_id"] in update_reviews:
            update_reviews[update_data["update_id"]]["aggregated"] = True
    
    # Get the updated global model version
    new_version = global_models[exp_id][cluster_id]["version"]
    
    message_parts = [f"Update {review_status}"]
    if review_status in [ReviewStatus.APPROVED, ReviewStatus.AUTO_APPROVED]:
        message_parts.append(f"& aggregated. Global model updated to v{new_version}")
    if staleness > 0:
        message_parts.append(f"(staleness={staleness}, weight={staleness_weight:.2f})")
    
    return {
        "accepted": True,
        "trust_score": trust_score,
        "message": " ".join(message_parts),
        "new_global_version": new_version if review_status in [ReviewStatus.APPROVED, ReviewStatus.AUTO_APPROVED] else None,
        "staleness": staleness,
        "staleness_weight": staleness_weight,
        "review_status": review_status
    }


def _aggregate_updates(exp_id: str, cluster_id: str):
    """Aggregate all pending updates for a cluster (with staleness weighting)"""
    config = experiments[exp_id]["config"]
    
    # Get accepted and approved updates for this cluster that haven't been aggregated yet
    cluster_updates = [
        u for u in pending_updates[exp_id]
        if u["cluster_id"] == cluster_id 
        and not u.get("rejected", False)
        and not u.get("aggregated", False)
        and u.get("review_status") in [ReviewStatus.APPROVED, ReviewStatus.AUTO_APPROVED]
    ]
    
    if not cluster_updates:
        return
    
    # Extract delta weights and client IDs
    deltas = [u["delta_weights"] for u in cluster_updates]
    client_ids = [u["client_id"] for u in cluster_updates]
    
    # Apply staleness weighting if enabled
    if config.get("staleness_weighting", True):
        staleness_weights = [u.get("staleness_weight", 1.0) for u in cluster_updates]
        # Weight deltas by staleness
        weighted_deltas = []
        for delta, sw in zip(deltas, staleness_weights):
            # Convert to numpy arrays for multiplication, then back to lists/native types
            weighted_delta = {}
            for k, v in delta.items():
                # Convert to numpy array if it's a list
                v_arr = np.array(v) if isinstance(v, (list, tuple)) else v
                # Multiply by staleness weight
                weighted_arr = v_arr * sw
                # Convert back to list if it was originally a list
                weighted_delta[k] = weighted_arr.tolist() if isinstance(v, (list, tuple)) else weighted_arr
            weighted_deltas.append(weighted_delta)
        deltas = weighted_deltas
        logger.info(f"Applied staleness weights: {staleness_weights}")
    
    # Select aggregator
    aggregator_type = config["aggregation_method"]
    if aggregator_type == "fedavg":
        aggregator = FedAvgAggregator()
    elif aggregator_type == "median":
        aggregator = MedianAggregator()
    elif aggregator_type == "trimmed_mean":
        aggregator = TrimmedMeanAggregator(trim_ratio=0.1)
    elif aggregator_type == "trust_weighted":
        aggregator = TrustWeightedAggregator(trust_store=trust_scorers[exp_id])
    else:
        aggregator = FedAvgAggregator()
    
    # Aggregate
    aggregated_delta = aggregator.aggregate(deltas, client_ids)
    
    # Debug: Log delta statistics
    delta_norms = [np.linalg.norm(flatten_weights(d)) for d in deltas]
    agg_norm = np.linalg.norm(flatten_weights(aggregated_delta))
    logger.info(f"Delta norms: {delta_norms}, Aggregated norm: {agg_norm}")
    
    # Update global model
    current_model = global_models[exp_id][cluster_id]
    current_weights = current_model["weights"]
    
    if current_weights is None:
        # First aggregation - use aggregated delta as absolute weights
        logger.info(f"First aggregation for {cluster_id}, setting initial weights")
        new_weights = aggregated_delta
    else:
        # Apply delta: theta_new = theta_old + delta
        new_weights = {}
        for key in aggregated_delta.keys():
            # Convert to numpy arrays for addition, then back to original type
            curr = current_weights[key]
            delta = aggregated_delta[key]
            curr_arr = np.array(curr) if isinstance(curr, (list, tuple)) else curr
            delta_arr = np.array(delta) if isinstance(delta, (list, tuple)) else delta
            result_arr = curr_arr + delta_arr
            new_weights[key] = result_arr.tolist() if isinstance(curr, (list, tuple)) else result_arr
        
        # Debug: Check if weights changed
        old_norm = np.linalg.norm(flatten_weights(current_weights))
        new_norm = np.linalg.norm(flatten_weights(new_weights))
        logger.info(f"Weight norms - Old: {old_norm:.4f}, New: {new_norm:.4f}, Change: {new_norm - old_norm:.4f}")
    
    # Update global model
    new_version = current_model["version"] + 1
    global_models[exp_id][cluster_id] = {
        "version": new_version,
        "weights": new_weights,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    # Save to file
    exp_dir = DATA_DIR / exp_id
    save_weights_to_file(
        new_weights,
        exp_dir / "global_models" / f"{cluster_id}_v{new_version}.pkl"
    )
    
    # Mark updates as aggregated
    for u in cluster_updates:
        u["aggregated"] = True
    
    logger.info(f"Aggregated {len(deltas)} updates for {cluster_id}, version {new_version}")


@app.post("/experiment/{exp_id}/aggregate")
def trigger_aggregation(exp_id: str, cluster_id: str = "cluster_0"):
    """Manually trigger aggregation for a cluster"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Count pending updates before aggregation
    pending_count = len([
        u for u in pending_updates.get(exp_id, [])
        if u["cluster_id"] == cluster_id 
        and not u.get("rejected", False)
        and not u.get("aggregated", False)
    ])
    
    _aggregate_updates(exp_id, cluster_id)
    
    return {
        "status": "aggregated",
        "cluster_id": cluster_id,
        "aggregated_updates": pending_count,
        "new_version": global_models[exp_id][cluster_id]["version"]
    }


# ============ ADMIN REVIEW ENDPOINTS ============

@app.get("/experiment/{exp_id}/pending-reviews")
def get_pending_reviews(exp_id: str) -> List[PendingUpdateSummary]:
    """Get all updates pending admin review"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    pending_summaries = []
    for update_id in pending_reviews.get(exp_id, []):
        if update_id in update_reviews:
            review = update_reviews[update_id]
            # Find the update data
            update_data = next(
                (u for u in pending_updates[exp_id] if u["update_id"] == update_id),
                None
            )
            
            if update_data and review["status"] == ReviewStatus.PENDING_REVIEW:
                pending_summaries.append(PendingUpdateSummary(
                    update_id=update_id,
                    experiment_id=exp_id,
                    client_id=review["client_id"],
                    submitted_at=review.get("submitted_at", datetime.utcnow().isoformat()),
                    model_version=review.get("model_version", 0),
                    cluster_id=review.get("cluster_id", "cluster_0"),
                    staleness=review.get("staleness", 0),
                    trust_score=review.get("trust_score", 1.0),
                    num_samples=update_data.get("num_samples"),
                    metadata=update_data.get("metadata")
                ))
    
    return pending_summaries


@app.post("/experiment/{exp_id}/update/{update_id}/review")
def submit_admin_review(exp_id: str, update_id: str, review_request: AdminReviewRequest) -> AdminReviewResponse:
    """Submit admin review for an update"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    if update_id not in update_reviews:
        raise HTTPException(status_code=404, detail="Update not found")
    
    review = update_reviews[update_id]
    
    # Update review status
    review["status"] = review_request.status
    review["feedback"] = review_request.feedback
    review["reviewed_at"] = datetime.utcnow().isoformat()
    review["admin_id"] = review_request.admin_id
    review["suggestions"] = review_request.suggestions
    
    # Remove from pending if it was pending
    if update_id in pending_reviews.get(exp_id, []):
        pending_reviews[exp_id].remove(update_id)
    
    # If approved, trigger aggregation
    will_aggregate = False
    if review_request.status == ReviewStatus.APPROVED:
        # Find the update data and mark it for aggregation
        for update_data in pending_updates[exp_id]:
            if update_data["update_id"] == update_id:
                update_data["review_status"] = ReviewStatus.APPROVED
                cluster_id = update_data["cluster_id"]
                
                # Trigger aggregation
                _aggregate_updates(exp_id, cluster_id)
                
                # Mark as aggregated
                review["aggregated"] = True
                will_aggregate = True
                break
    
    # If rejected or needs improvement, mark update accordingly
    elif review_request.status in [ReviewStatus.REJECTED, ReviewStatus.NEEDS_IMPROVEMENT]:
        for update_data in pending_updates[exp_id]:
            if update_data["update_id"] == update_id:
                update_data["review_status"] = review_request.status
                if review_request.status == ReviewStatus.REJECTED:
                    update_data["rejected"] = True
                    experiments[exp_id]["rejected_updates"] += 1
                break
    
    logger.info(f"Admin {review_request.admin_id} reviewed {update_id}: {review_request.status}")
    
    return AdminReviewResponse(
        update_id=update_id,
        review_status=review_request.status,
        feedback=review_request.feedback,
        reviewed_at=review["reviewed_at"],
        will_aggregate=will_aggregate
    )


@app.get("/experiment/{exp_id}/update/{update_id}/review-status")
def get_review_status(exp_id: str, update_id: str) -> Dict:
    """Get review status for an update"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    if update_id not in update_reviews:
        raise HTTPException(status_code=404, detail="Update not found")
    
    review = update_reviews[update_id]
    return {
        "update_id": update_id,
        "status": review["status"],
        "feedback": review.get("feedback"),
        "reviewed_at": review.get("reviewed_at"),
        "admin_id": review.get("admin_id"),
        "aggregated": review.get("aggregated", False)
    }


# ============ CLIENT FEEDBACK ENDPOINTS ============

@app.get("/experiment/{exp_id}/client/{client_id}/feedback")
def get_client_feedback(exp_id: str, client_id: str) -> List[ClientFeedbackItem]:
    """Get all feedback for a specific client"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    feedback_items = []
    for update_id, review in update_reviews.items():
        if review.get("experiment_id") == exp_id and review.get("client_id") == client_id:
            feedback_items.append(ClientFeedbackItem(
                update_id=update_id,
                experiment_id=exp_id,
                submitted_at=review.get("submitted_at", datetime.utcnow().isoformat()),
                review_status=review["status"],
                feedback=review.get("feedback"),
                reviewed_at=review.get("reviewed_at"),
                admin_id=review.get("admin_id"),
                suggestions=review.get("suggestions"),
                aggregated=review.get("aggregated", False)
            ))
    
    # Sort by submitted_at (most recent first)
    feedback_items.sort(key=lambda x: x.submitted_at, reverse=True)
    return feedback_items


@app.get("/experiment/{exp_id}/update/{update_id}/feedback")
def get_update_feedback(exp_id: str, update_id: str) -> ClientFeedbackItem:
    """Get feedback for a specific update"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    if update_id not in update_reviews:
        raise HTTPException(status_code=404, detail="Update not found or no review available")
    
    review = update_reviews[update_id]
    
    return ClientFeedbackItem(
        update_id=update_id,
        experiment_id=exp_id,
        submitted_at=review.get("submitted_at", datetime.utcnow().isoformat()),
        review_status=review["status"],
        feedback=review.get("feedback"),
        reviewed_at=review.get("reviewed_at"),
        admin_id=review.get("admin_id"),
        suggestions=review.get("suggestions"),
        aggregated=review.get("aggregated", False)
    )


# ============ WEIGHT FETCHING ENDPOINT ============

@app.get("/experiment/{exp_id}/update/{update_id}/weights")
def get_update_weights(exp_id: str, update_id: str) -> UpdateWeightsResponse:
    """
    Fetch complete weight data for a specific update
    
    This endpoint allows retrieving the exact weights submitted by a client.
    The weights can be passed to external hash functions for verification.
    """
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Find update in pending_updates
    update_data = None
    for update in pending_updates.get(exp_id, []):
        if update["update_id"] == update_id:
            update_data = update
            break
    
    if not update_data:
        raise HTTPException(status_code=404, detail="Update not found")
    
    # Get review data for trust score
    review = update_reviews.get(update_id, {})
    
    # Serialize weights for response
    weights_serialized = serialize_weights(update_data["delta_weights"])
    
    return UpdateWeightsResponse(
        update_id=update_id,
        client_id=update_data["client_id"],
        experiment_id=exp_id,
        cluster_id=update_data["cluster_id"],
        weights=weights_serialized,
        timestamp=update_data["timestamp"],
        base_version=update_data["base_version"],
        staleness=update_data["staleness"],
        trust_score=review.get("trust_score", 0.5),
        review_status=update_data.get("review_status", "unknown")
    )


@app.get("/health")
def health():
    return {"status": "healthy"}
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
