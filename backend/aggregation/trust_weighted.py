"""Trust-weighted aggregator - weights updates by client trust scores"""
from typing import Dict, List
import numpy as np
from .base import BaseAggregator


class TrustWeightedAggregator(BaseAggregator):
    """Weight updates by client trust scores"""
    
    def __init__(self, trust_store=None, **kwargs):
        """
        Args:
            trust_store: Object with get_trust(client_id) method
        """
        super().__init__(**kwargs)
        self.trust_store = trust_store
    
    def aggregate(
        self, 
        updates: List[Dict[str, np.ndarray]], 
        client_ids: List[str] = None
    ) -> Dict[str, np.ndarray]:
        """Weighted average by trust scores"""
        if not updates:
            raise ValueError("No updates to aggregate")
        
        if not client_ids or not self.trust_store:
            # Fall back to simple average if no trust info
            aggregated = {}
            for key in updates[0].keys():
                stacked = np.stack([update[key] for update in updates])
                aggregated[key] = np.mean(stacked, axis=0)
            return aggregated
        
        # Get trust scores
        trust_scores = [self.trust_store.get_trust(cid) for cid in client_ids]
        total_trust = sum(trust_scores)
        
        if total_trust == 0:
            # All clients untrusted, use uniform weights
            trust_scores = [1.0] * len(client_ids)
            total_trust = len(client_ids)
        
        aggregated = {}
        for key in updates[0].keys():
            weighted_sum = sum(
                trust * update[key] 
                for trust, update in zip(trust_scores, updates)
            )
            aggregated[key] = weighted_sum / total_trust
        
        return aggregated
