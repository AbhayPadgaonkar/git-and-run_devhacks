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


# ============ Request/Response Models ============

class ExperimentConfig(BaseModel):
    name: str
    aggregation_method: str = Field(default="fedavg", pattern="^(fedavg|median|trimmed_mean|trust_weighted)$")
    enable_trust: bool = True
    enable_clustering: bool = False
    trust_alpha: float = Field(default=0.8, ge=0.0, le=1.0)
    cluster_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    initial_weights: Optional[str] = None  # Base64 encoded weights


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


class GlobalModelResponse(BaseModel):
    version: int
    cluster_id: str
    weights: str  # Base64 encoded
    timestamp: str


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
        
        # Add to pending updates
        update_data = {
            "update_id": update_id,
            "client_id": update.client_id,
            "cluster_id": cluster_id,
            "delta_weights": delta_weights,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
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
            message=result.get("message")
        )
        
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _process_update(exp_id: str, update_data: Dict) -> Dict:
    """Process a single update (malicious detection + aggregation)"""
    config = experiments[exp_id]["config"]
    cluster_id = update_data["cluster_id"]
    client_id = update_data["client_id"]
    delta_weights = update_data["delta_weights"]
    
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
    
    # Accept or reject
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
    
    experiments[exp_id]["accepted_updates"] += 1
    
    # Don't aggregate immediately - wait for manual trigger
    # This allows collecting multiple updates before aggregation
    # _aggregate_updates(exp_id, cluster_id)
    
    # Mark as ready for aggregation (not yet processed)
    update_data["aggregated"] = False
    
    return {
        "accepted": True,
        "trust_score": trust_score,
        "message": "Update accepted, awaiting aggregation"
    }


def _aggregate_updates(exp_id: str, cluster_id: str):
    """Aggregate all pending updates for a cluster"""
    config = experiments[exp_id]["config"]
    
    # Get accepted updates for this cluster that haven't been aggregated yet
    cluster_updates = [
        u for u in pending_updates[exp_id]
        if u["cluster_id"] == cluster_id 
        and not u.get("rejected", False)
        and not u.get("aggregated", False)
    ]
    
    if not cluster_updates:
        return
    
    # Extract delta weights and client IDs
    deltas = [u["delta_weights"] for u in cluster_updates]
    client_ids = [u["client_id"] for u in cluster_updates]
    
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
        new_weights = {
            key: current_weights[key] + aggregated_delta[key]
            for key in aggregated_delta.keys()
        }
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


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
