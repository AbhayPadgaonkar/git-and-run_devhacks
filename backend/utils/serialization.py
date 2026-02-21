"""Weight serialization utilities for framework-agnostic handling"""
import numpy as np
import pickle
import base64
from typing import Dict, Any
import json


def serialize_weights(weights: Dict[str, np.ndarray]) -> str:
    """Serialize NumPy weight dictionary to base64 string"""
    pickled = pickle.dumps(weights)
    return base64.b64encode(pickled).decode('utf-8')


def deserialize_weights(serialized: str) -> Dict[str, np.ndarray]:
    """Deserialize base64 string to NumPy weight dictionary"""
    pickled = base64.b64decode(serialized.encode('utf-8'))
    return pickle.loads(pickled)


def flatten_weights(weights: Dict[str, np.ndarray]) -> np.ndarray:
    """Flatten nested weight dictionary to single vector"""
    flattened = []
    for key in sorted(weights.keys()):  # Sort for consistency
        flattened.append(weights[key].flatten())
    return np.concatenate(flattened)


def unflatten_weights(flat: np.ndarray, reference: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Unflatten vector back to dictionary structure using reference"""
    weights = {}
    offset = 0
    for key in sorted(reference.keys()):
        shape = reference[key].shape
        size = reference[key].size
        weights[key] = flat[offset:offset + size].reshape(shape)
        offset += size
    return weights


def save_weights_to_file(weights: Dict[str, np.ndarray], filepath: str):
    """Save weights to pickle file"""
    with open(filepath, 'wb') as f:
        pickle.dump(weights, f)


def load_weights_from_file(filepath: str) -> Dict[str, np.ndarray]:
    """Load weights from pickle file"""
    with open(filepath, 'rb') as f:
        return pickle.load(f)
