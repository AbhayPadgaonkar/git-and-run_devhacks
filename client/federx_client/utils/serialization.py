"""Weight serialization for client"""
import numpy as np
import pickle
import base64
from typing import Dict


def serialize_weights(weights: Dict[str, np.ndarray]) -> str:
    """Serialize NumPy weight dictionary to base64 string"""
    pickled = pickle.dumps(weights)
    return base64.b64encode(pickled).decode('utf-8')


def deserialize_weights(serialized: str) -> Dict[str, np.ndarray]:
    """Deserialize base64 string to NumPy weight dictionary"""
    pickled = base64.b64decode(serialized.encode('utf-8'))
    return pickle.loads(pickled)
