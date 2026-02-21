"""Malicious update detection"""
from typing import Dict, List, Tuple
import numpy as np
from ..utils.serialization import flatten_weights


class MaliciousDetector:
    """Detects potentially malicious updates using statistical methods"""
    
    def __init__(
        self,
        norm_threshold_multiplier: float = 2.0,
        cosine_threshold: float = 0.3,
        deviation_threshold: float = 3.0
    ):
        """
        Args:
            norm_threshold_multiplier: Flag if norm > multiplier * median_norm
            cosine_threshold: Flag if cosine similarity < threshold
            deviation_threshold: Flag if deviation > threshold * std
        """
        self.norm_threshold_multiplier = norm_threshold_multiplier
        self.cosine_threshold = cosine_threshold
        self.deviation_threshold = deviation_threshold
    
    def detect(
        self, 
        update: Dict[str, np.ndarray], 
        all_updates: List[Dict[str, np.ndarray]]
    ) -> Tuple[bool, Dict[str, float]]:
        """
        Detect if update is potentially malicious
        
        Returns:
            (is_malicious, metrics_dict)
        """
        if len(all_updates) < 3:
            # Not enough samples for statistical detection
            return False, {"reason": "insufficient_samples"}
        
        # Flatten all updates
        flat_update = flatten_weights(update)
        flat_all = [flatten_weights(u) for u in all_updates]
        
        metrics = {}
        flags = []
        
        # 1. Norm-based detection
        norms = [np.linalg.norm(u) for u in flat_all]
        median_norm = np.median(norms)
        update_norm = np.linalg.norm(flat_update)
        metrics['norm'] = float(update_norm)
        metrics['median_norm'] = float(median_norm)
        
        if update_norm > self.norm_threshold_multiplier * median_norm:
            flags.append('high_norm')
        
        # 2. Cosine similarity with median
        median_update = np.median(np.stack(flat_all), axis=0)
        cosine_sim = self._cosine_similarity(flat_update, median_update)
        metrics['cosine_similarity'] = float(cosine_sim)
        
        if cosine_sim < self.cosine_threshold:
            flags.append('low_similarity')
        
        # 3. Deviation from mean
        mean_update = np.mean(np.stack(flat_all), axis=0)
        std_update = np.std(np.stack(flat_all), axis=0)
        deviation = np.linalg.norm(flat_update - mean_update)
        expected_deviation = np.linalg.norm(std_update)
        metrics['deviation'] = float(deviation)
        metrics['expected_deviation'] = float(expected_deviation)
        
        if deviation > self.deviation_threshold * expected_deviation:
            flags.append('high_deviation')
        
        # Mark as malicious if 2+ flags triggered
        is_malicious = len(flags) >= 2
        metrics['flags'] = flags
        metrics['is_malicious'] = is_malicious
        
        return is_malicious, metrics
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
