"""Weight serialization for client"""
import numpy as np
import pickle
import base64
import zlib
from typing import Dict, Optional


def serialize_weights(
    weights: Dict[str, np.ndarray], 
    compression: Optional[str] = None
) -> str:
    """
    Serialize NumPy weight dictionary to base64 string
    
    Args:
        weights: Dictionary of weight arrays
        compression: Compression method ('zlib', 'gzip', or None)
                    LoRA weights benefit from compression (~70% size reduction)
    
    Returns:
        Base64 encoded (and optionally compressed) string
    """
    pickled = pickle.dumps(weights, protocol=pickle.HIGHEST_PROTOCOL)
    
    if compression == 'zlib':
        # zlib compression (level 9 = maximum compression)
        compressed = zlib.compress(pickled, level=9)
        # Add compression marker
        result = b'ZLIB:' + compressed
    elif compression == 'gzip':
        import gzip
        compressed = gzip.compress(pickled, compresslevel=9)
        result = b'GZIP:' + compressed
    else:
        result = pickled
    
    return base64.b64encode(result).decode('utf-8')


def deserialize_weights(serialized: str) -> Dict[str, np.ndarray]:
    """
    Deserialize base64 string to NumPy weight dictionary
    Automatically detects and decompresses if needed
    
    Args:
        serialized: Base64 encoded string
    
    Returns:
        Dictionary of weight arrays
    """
    decoded = base64.b64decode(serialized.encode('utf-8'))
    
    # Check for compression markers
    if decoded.startswith(b'ZLIB:'):
        pickled = zlib.decompress(decoded[5:])  # Skip 'ZLIB:' prefix
    elif decoded.startswith(b'GZIP:'):
        import gzip
        pickled = gzip.decompress(decoded[5:])  # Skip 'GZIP:' prefix
    else:
        pickled = decoded
    
    return pickle.loads(pickled)


def get_weights_size(weights: Dict[str, np.ndarray]) -> int:
    """Calculate total size of weights in bytes"""
    return sum(w.nbytes for w in weights.values())


def get_compression_stats(weights: Dict[str, np.ndarray]) -> Dict[str, any]:
    """
    Get compression statistics for weights
    
    Returns:
        Dictionary with original size, compressed sizes, and compression ratios
    """
    original = serialize_weights(weights, compression=None)
    zlib_compressed = serialize_weights(weights, compression='zlib')
    
    original_bytes = len(original.encode('utf-8'))
    zlib_bytes = len(zlib_compressed.encode('utf-8'))
    
    return {
        'original_size': original_bytes,
        'original_size_mb': original_bytes / (1024 * 1024),
        'zlib_size': zlib_bytes,
        'zlib_size_mb': zlib_bytes / (1024 * 1024),
        'compression_ratio': original_bytes / zlib_bytes if zlib_bytes > 0 else 1.0,
        'space_saved_percent': 100 * (1 - zlib_bytes / original_bytes) if original_bytes > 0 else 0
    }
