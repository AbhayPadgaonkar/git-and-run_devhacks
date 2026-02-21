"""Trust score management"""
from typing import Dict


class TrustScorer:
    """Manages trust scores for clients using exponential moving average"""
    
    def __init__(self, alpha: float = 0.8, initial_trust: float = 1.0):
        """
        Args:
            alpha: Decay factor for exponential moving average (0-1)
            initial_trust: Initial trust score for new clients
        """
        self.alpha = alpha
        self.initial_trust = initial_trust
        self.trust_scores: Dict[str, float] = {}
    
    def get_trust(self, client_id: str) -> float:
        """Get trust score for client (returns initial if new)"""
        return self.trust_scores.get(client_id, self.initial_trust)
    
    def update_trust(self, client_id: str, is_malicious: bool):
        """Update trust score based on update quality"""
        old_trust = self.get_trust(client_id)
        reliability = 0.0 if is_malicious else 1.0
        new_trust = self.alpha * old_trust + (1 - self.alpha) * reliability
        self.trust_scores[client_id] = max(0.0, min(1.0, new_trust))  # Clamp [0, 1]
    
    def get_all_scores(self) -> Dict[str, float]:
        """Get all trust scores"""
        return self.trust_scores.copy()
    
    def reset_trust(self, client_id: str):
        """Reset client trust to initial value"""
        self.trust_scores[client_id] = self.initial_trust
