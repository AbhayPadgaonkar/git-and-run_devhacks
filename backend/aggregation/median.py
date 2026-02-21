"""Coordinate-wise median aggregator (Byzantine-robust)"""
from typing import Dict, List
import numpy as np
from .base import BaseAggregator


class MedianAggregator(BaseAggregator):
    """Coordinate-wise median - robust to outliers"""
    
    def aggregate(
        self, 
        updates: List[Dict[str, np.ndarray]], 
        client_ids: List[str] = None
    ) -> Dict[str, np.ndarray]:
        """Compute coordinate-wise median across all updates"""
        if not updates:
            raise ValueError("No updates to aggregate")
        
        aggregated = {}
        
        for key in updates[0].keys():
            # Stack all updates for this layer
            stacked = np.stack([update[key] for update in updates])
            # Median along axis 0 (across clients)
            aggregated[key] = np.median(stacked, axis=0)
        
        return aggregated
