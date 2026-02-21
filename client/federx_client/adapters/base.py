"""Base adapter interface for federated learning models"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class BaseFLModel(ABC):
    """Base interface that all framework adapters must implement"""
    
    @abstractmethod
    def get_weights(self, model: Any) -> Dict[str, np.ndarray]:
        """
        Extract weights from model as NumPy dictionary
        
        Args:
            model: Framework-specific model object
            
        Returns:
            Dictionary mapping layer names to NumPy arrays
        """
        pass
    
    @abstractmethod
    def set_weights(self, model: Any, weights: Dict[str, np.ndarray]):
        """
        Load weights into model from NumPy dictionary
        
        Args:
            model: Framework-specific model object
            weights: Dictionary mapping layer names to NumPy arrays
        """
        pass
    
    @abstractmethod
    def get_output_shape(self, model: Any) -> tuple:
        """
        Get output shape of model
        
        Args:
            model: Framework-specific model object
            
        Returns:
            Tuple representing output shape
        """
        pass
