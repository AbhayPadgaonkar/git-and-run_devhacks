"""Cluster management for multi-task federated learning"""
from typing import Dict, List
import numpy as np
from ..utils.serialization import flatten_weights


class ClusterManager:
    """Manages client clusters for heterogeneous tasks"""
    
    def __init__(self, similarity_threshold: float = 0.7, max_clusters: int = 10):
        """
        Args:
            similarity_threshold: Minimum cosine similarity to join cluster
            max_clusters: Maximum number of clusters allowed
        """
        self.similarity_threshold = similarity_threshold
        self.max_clusters = max_clusters
        self.clusters: Dict[str, Dict] = {}
        self.client_to_cluster: Dict[str, str] = {}
    
    def assign_cluster(
        self, 
        client_id: str, 
        update: Dict[str, np.ndarray]
    ) -> str:
        """
        Assign client to existing cluster or create new one
        
        Returns:
            cluster_id
        """
        flat_update = flatten_weights(update)
        
        # If no clusters exist, create first one
        if not self.clusters:
            cluster_id = "cluster_0"
            self.clusters[cluster_id] = {
                "centroid": flat_update,
                "clients": [client_id],
                "update_count": 1
            }
            self.client_to_cluster[client_id] = cluster_id
            return cluster_id
        
        # Check if client already assigned
        if client_id in self.client_to_cluster:
            return self.client_to_cluster[client_id]
        
        # Find best matching cluster
        best_cluster = None
        best_similarity = -1
        
        for cluster_id, cluster_data in self.clusters.items():
            centroid = cluster_data["centroid"]
            similarity = self._cosine_similarity(flat_update, centroid)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = cluster_id
        
        # Assign to best cluster if similar enough
        if best_similarity >= self.similarity_threshold:
            self.clusters[best_cluster]["clients"].append(client_id)
            self.client_to_cluster[client_id] = best_cluster
            return best_cluster
        
        # Create new cluster if under max limit
        if len(self.clusters) < self.max_clusters:
            cluster_id = f"cluster_{len(self.clusters)}"
            self.clusters[cluster_id] = {
                "centroid": flat_update,
                "clients": [client_id],
                "update_count": 1
            }
            self.client_to_cluster[client_id] = cluster_id
            return cluster_id
        
        # Max clusters reached, assign to closest
        self.clusters[best_cluster]["clients"].append(client_id)
        self.client_to_cluster[client_id] = best_cluster
        return best_cluster
    
    def update_centroid(self, cluster_id: str, updates: List[np.ndarray]):
        """Update cluster centroid as mean of recent updates"""
        if cluster_id in self.clusters and updates:
            centroid = np.mean(np.stack(updates), axis=0)
            self.clusters[cluster_id]["centroid"] = centroid
            self.clusters[cluster_id]["update_count"] += len(updates)
    
    def get_cluster(self, client_id: str) -> str:
        """Get cluster ID for client"""
        return self.client_to_cluster.get(client_id, "cluster_0")
    
    def get_cluster_info(self, cluster_id: str) -> Dict:
        """Get cluster information"""
        return self.clusters.get(cluster_id, {})
    
    def get_all_clusters(self) -> Dict[str, Dict]:
        """Get all clusters"""
        return self.clusters.copy()
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
