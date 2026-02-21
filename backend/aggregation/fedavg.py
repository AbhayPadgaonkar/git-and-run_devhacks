"""Federated Averaging (FedAvg) aggregator"""
from typing import Dict, List
import numpy as np
from .base import BaseAggregator


class FedAvgAggregator(BaseAggregator):
    """Simple averaging of all client updates"""
    
    def aggregate(
        self, 
        updates: List[Dict[str, np.ndarray]], 
        client_ids: List[str] = None
    ) -> Dict[str, np.ndarray]:
        """Average all updates element-wise"""
        if not updates:
            raise ValueError("No updates to aggregate")
        
        aggregated = {}
        n = len(updates)
        
        for key in updates[0].keys():
            # Stack all updates for this layer
            stacked = np.stack([update[key] for update in updates])
            # Simple average
            aggregated[key] = np.mean(stacked, axis=0)
        
        return aggregated
