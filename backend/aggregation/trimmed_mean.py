"""Trimmed Mean aggregator - removes outliers before averaging"""
from typing import Dict, List
import numpy as np
from .base import BaseAggregator


class TrimmedMeanAggregator(BaseAggregator):
    """Remove top/bottom k% values, average remaining"""
    
    def __init__(self, trim_ratio: float = 0.1, **kwargs):
        """
        Args:
            trim_ratio: Fraction to trim from each end (default 10%)
        """
        super().__init__(**kwargs)
        self.trim_ratio = trim_ratio
    
    def aggregate(
        self, 
        updates: List[Dict[str, np.ndarray]], 
        client_ids: List[str] = None
    ) -> Dict[str, np.ndarray]:
        """Compute trimmed mean of updates"""
        if not updates:
            raise ValueError("No updates to aggregate")
        
        aggregated = {}
        n = len(updates)
        k = max(1, int(n * self.trim_ratio))  # At least 1
        
        # Need at least 3 updates for meaningful trimming
        if n < 3:
            # Fall back to simple average
            for key in updates[0].keys():
                stacked = np.stack([update[key] for update in updates])
                aggregated[key] = np.mean(stacked, axis=0)
            return aggregated
        
        for key in updates[0].keys():
            stacked = np.stack([update[key] for update in updates])
            # Sort along client axis (axis 0)
            sorted_vals = np.sort(stacked, axis=0)
            # Remove top k and bottom k
            trimmed = sorted_vals[k:n-k]
            # Average remaining
            aggregated[key] = np.mean(trimmed, axis=0)
        
        return aggregated
