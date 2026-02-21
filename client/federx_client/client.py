"""Federated learning client SDK"""
import requests
from typing import Dict, Any, Optional
import numpy as np
from .adapters import PyTorchAdapter
from .utils.serialization import serialize_weights, deserialize_weights


class FederatedClient:
    """Client for federated learning with server"""
    
    def __init__(
        self, 
        server_url: str,
        experiment_id: str,
        client_id: str,
        adapter=None
    ):
        """
        Initialize federated client
        
        Args:
            server_url: URL of federated server (e.g., http://localhost:8000)
            experiment_id: Experiment ID from server
            client_id: Unique client identifier
            adapter: Model adapter (defaults to PyTorchAdapter)
        """
        self.server_url = server_url.rstrip('/')
        self.experiment_id = experiment_id
        self.client_id = client_id
        self.adapter = adapter or PyTorchAdapter()
        self.current_version = 0
        self.cluster_id = "cluster_0"
    
    def fetch_global_model(self) -> Dict[str, np.ndarray]:
        """
        Download global model from server
        
        Returns:
            NumPy weight dictionary
        """
        url = f"{self.server_url}/experiment/{self.experiment_id}/global-model"
        params = {"cluster_id": self.cluster_id}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        self.current_version = data["version"]
        self.cluster_id = data["cluster_id"]
        
        weights = deserialize_weights(data["weights"])
        return weights
    
    def submit_update(
        self, 
        delta_weights: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Submit weight update to server
        
        Args:
            delta_weights: Delta weights as NumPy dictionary
            
        Returns:
            Response from server
        """
        url = f"{self.server_url}/experiment/{self.experiment_id}/submit-update"
        
        payload = {
            "client_id": self.client_id,
            "delta_weights": serialize_weights(delta_weights),
            "model_version": self.current_version
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if "cluster_id" in result:
            self.cluster_id = result["cluster_id"]
        
        return result
    
    def train_and_submit(self, model, train_function, train_loader):
        """
        Complete training cycle: fetch → train → compute delta → submit
        
        Args:
            model: Neural network model
            train_function: Function that trains model (signature: fn(model, train_loader))
            train_loader: Data loader for training
            
        Returns:
            Response from server
        """
        # 1. Fetch global model
        global_weights = self.fetch_global_model()
        
        # 2. Load into local model
        if global_weights:  # Skip if empty initial model
            self.adapter.set_weights(model, global_weights)
        
        # 3. Save old weights
        old_weights = self.adapter.get_weights(model)
        
        # 4. Train locally
        train_function(model, train_loader)
        
        # 5. Get new weights
        new_weights = self.adapter.get_weights(model)
        
        # 6. Compute delta
        delta_weights = {
            key: new_weights[key] - old_weights[key]
            for key in new_weights.keys()
        }
        
        # 7. Submit to server
        return self.submit_update(delta_weights)
    
    def get_trust_score(self) -> float:
        """Get current trust score from server"""
        url = f"{self.server_url}/experiment/{self.experiment_id}/status"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        trust_scores = data.get("trust_scores", {})
        return trust_scores.get(self.client_id, 1.0)
