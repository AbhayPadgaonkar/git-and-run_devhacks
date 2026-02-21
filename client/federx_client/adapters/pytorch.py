"""PyTorch adapter for federated learning"""
from typing import Dict, Any
import numpy as np
from .base import BaseFLModel

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class PyTorchAdapter(BaseFLModel):
    """Adapter for PyTorch models"""
    
    def __init__(self):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not installed. Install with: pip install torch")
    
    def get_weights(self, model: nn.Module) -> Dict[str, np.ndarray]:
        """Extract weights from PyTorch model as numpy arrays (copies)"""
        return {
            name: param.detach().cpu().numpy().copy()  # .copy() prevents memory sharing
            for name, param in model.state_dict().items()
        }
    
    def set_weights(self, model: nn.Module, weights: Dict[str, np.ndarray]):
        """Load weights into PyTorch model"""
        state_dict = {
            name: torch.from_numpy(w).clone()  # .clone() prevents memory sharing
            for name, w in weights.items()
        }
        model.load_state_dict(state_dict)
    
    def get_output_shape(self, model: nn.Module) -> tuple:
        """Get output shape of last layer"""
        # Get last layer
        last_layer = list(model.children())[-1]
        if hasattr(last_layer, 'out_features'):
            return (last_layer.out_features,)
        return (0,)  # Unknown
