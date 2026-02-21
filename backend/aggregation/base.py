"""Base aggregator interface"""
from abc import ABC, abstractmethod
from typing import Dict, List
import numpy as np


class BaseAggregator(ABC):
    """Base class for all aggregation methods"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    @abstractmethod
    def aggregate(
        self, 
        updates: List[Dict[str, np.ndarray]], 
        client_ids: List[str] = None
    ) -> Dict[str, np.ndarray]:
        """
        Aggregate multiple client updates into single global update
        
        Args:
            updates: List of weight update dictionaries
            client_ids: Optional list of client IDs for trust weighting
            
        Returns:
            Aggregated weight update dictionary
        """
        pass
    
    def get_name(self) -> str:
        """Return aggregator name"""
        return self.__class__.__name__
