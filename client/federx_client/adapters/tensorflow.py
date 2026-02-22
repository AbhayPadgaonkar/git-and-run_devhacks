"""TensorFlow/Keras adapter for federated learning"""
from typing import Dict, Any
import numpy as np
from .base import BaseFLModel

try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class TensorFlowAdapter(BaseFLModel):
    """Adapter for TensorFlow/Keras models"""
    
    def __init__(self):
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow not installed. Install with: pip install tensorflow")
    
    def get_weights(self, model: keras.Model) -> Dict[str, np.ndarray]:
        """
        Extract weights from TensorFlow/Keras model as numpy arrays
        
        Args:
            model: Keras Model instance
            
        Returns:
            Dictionary mapping layer names to weight arrays
        """
        weights_dict = {}
        for layer in model.layers:
            layer_weights = layer.get_weights()
            if layer_weights:  # Skip layers without weights
                for i, weight_array in enumerate(layer_weights):
                    # Name format: layer_name_weight_0, layer_name_bias_0, etc. (no slashes for compatibility)
                    key = f"{layer.name}_weight_{i}"
                    weights_dict[key] = weight_array.copy()  # Copy to prevent memory sharing
        return weights_dict
    
    def set_weights(self, model: keras.Model, weights: Dict[str, np.ndarray]):
        """
        Load weights into TensorFlow/Keras model
        
        Args:
            model: Keras Model instance
            weights: Dictionary mapping layer names to weight arrays
        """
        # Group weights by layer name
        layer_weights = {}
        for key, weight_array in weights.items():
            # Split on underscore and take first part as layer name
            parts = key.split('_weight_')
            if len(parts) == 2:
                layer_name = parts[0]
            else:
                # Fallback: try to extract layer name
                layer_name = key.rsplit('_', 2)[0]
            
            if layer_name not in layer_weights:
                layer_weights[layer_name] = []
            layer_weights[layer_name].append(weight_array.copy())
        
        # Set weights for each layer
        for layer in model.layers:
            if layer.name in layer_weights:
                layer.set_weights(layer_weights[layer.name])
    
    def get_output_shape(self, model: keras.Model) -> tuple:
        """
        Get output shape of model
        
        Args:
            model: Keras Model instance
            
        Returns:
            Output shape tuple
        """
        return tuple(model.output_shape[1:])  # Skip batch dimension


class KerasAdapter(TensorFlowAdapter):
    """Alias for TensorFlowAdapter (Keras is part of TensorFlow 2.x)"""
    pass
