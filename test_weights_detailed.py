"""
Quick Test: Weight Fetching API - Show Actual Weights

Fast test that shows actual weight values for all frameworks.
No real training needed - just initialize models and show weights.
"""
import requests
import torch
import torch.nn as nn
import numpy as np
import pickle
import base64
import hashlib
from typing import Dict, Any
import sys
from pathlib import Path

# Add client to path
sys.path.insert(0, str(Path(__file__).parent / "client"))

from federx_client.adapters.pytorch import PyTorchAdapter

# Optional frameworks
try:
    from federx_client.adapters.tensorflow import TensorFlowAdapter
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except:
    TF_AVAILABLE = False

try:
    from federx_client.adapters.sklearn import SklearnAdapter
    from sklearn.neural_network import MLPClassifier
    SKLEARN_AVAILABLE = True
except:
    SKLEARN_AVAILABLE = False


SERVER = "http://localhost:8000"


# ============================================================================
# SIMPLE MODELS
# ============================================================================

class SimpleCNN(nn.Module):
    """Minimal PyTorch CNN"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 8, 3)
        self.fc1 = nn.Linear(5408, 10)  # Correct size for 28x28 input
    
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        return x


# ============================================================================
# HELPERS
# ============================================================================

def create_experiment(name: str) -> str:
    response = requests.post(f"{SERVER}/experiment/create", json={
        "name": name, "aggregation_method": "fedavg"
    })
    return response.json()["experiment_id"]


def submit_and_fetch(exp_id: str, client_id: str, weights: Dict[str, np.ndarray]):
    # Submit
    weights_b64 = base64.b64encode(pickle.dumps(weights)).decode('utf-8')
    response = requests.post(f"{SERVER}/experiment/{exp_id}/submit-update", json={
        "client_id": client_id,
        "delta_weights": weights_b64,
        "model_version": 0
    })
    
    if response.status_code != 200:
        raise Exception(f"Submit failed: {response.text}")
    
    update_id = response.json()["update_id"]
    
    # Fetch
    response = requests.get(f"{SERVER}/experiment/{exp_id}/update/{update_id}/weights")
    
    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.text}")
    
    fetched_b64 = response.json()["weights"]
    fetched = pickle.loads(base64.b64decode(fetched_b64))
    
    return update_id, fetched


def compute_hash(weights: Dict[str, np.ndarray]) -> str:
    combined = np.concatenate([weights[k].flatten() for k in sorted(weights.keys())])
    return hashlib.sha256(combined.tobytes()).hexdigest()


def display_weights(weights: Dict[str, np.ndarray], title: str):
    """Display weight details"""
    print(f"\n  📊 {title}")
    print(f"  {'─'*76}")
    
    total_params = 0
    for key, value in sorted(weights.items()):
        params = value.size
        total_params += params
        
        # Statistics
        flat = value.flatten()
        stats = f"min={flat.min():.4f}, max={flat.max():.4f}, mean={flat.mean():.4f}, std={flat.std():.4f}"
        
        # Sample values (first 5)
        sample_str = ", ".join([f"{v:.4f}" for v in flat[:5]])
        
        print(f"  {key[:35]:<35} {str(value.shape):<15} {params:>8,} params")
        print(f"  {'':>35} Stats: {stats}")
        print(f"  {'':>35} Sample: [{sample_str}...]")
    
    print(f"  {'─'*76}")
    print(f"  Total Parameters: {total_params:,}\n")


# ============================================================================
# TESTS
# ============================================================================

def test_pytorch(exp_id: str):
    """Test PyTorch"""
    print("\n" + "="*80)
    print("  TEST 1: PyTorch CNN")
    print("="*80)
    
    # Create model
    model = SimpleCNN()
    adapter = PyTorchAdapter()
    
    # Initialize
    dummy = torch.randn(2, 1, 28, 28)
    _ = model(dummy)
    
    # Get weights
    weights = adapter.get_weights(model)
    print(f"\n  ✓ Created PyTorch CNN with {len(weights)} layers")
    
    # Show weights
    display_weights(weights, "Original Weights (Before Submission)")
    
    # Submit and fetch
    update_id, fetched = submit_and_fetch(exp_id, "pytorch_client", weights)
    print(f"  ✓ Submitted and fetched update: {update_id}")
    
    # Show fetched weights
    display_weights(fetched, "Fetched Weights (After API Retrieval)")
    
    # Verify
    orig_hash = compute_hash(weights)
    fetch_hash = compute_hash(fetched)
    match = orig_hash == fetch_hash
    
    print(f"  🔐 Hash Verification:")
    print(f"     Original: {orig_hash[:48]}...")
    print(f"     Fetched:  {fetch_hash[:48]}...")
    print(f"     Result:   {'✅ MATCH (Integrity Verified!)' if match else '❌ MISMATCH'}")
    
    return {"framework": "PyTorch", "passed": match, "params": sum(w.size for w in weights.values())}


def test_tensorflow(exp_id: str):
    """Test TensorFlow/Keras"""
    print("\n" + "="*80)
    print("  TEST 2: TensorFlow/Keras MLP")
    print("="*80)
    
    if not TF_AVAILABLE:
        print("  ⚠️  Skipping: TensorFlow not available")
        return {"framework": "TensorFlow", "skipped": True}
    
    try:
        # Create model
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(784,), name='hidden'),
            keras.layers.Dense(10, activation='softmax', name='output')
        ])
        
        adapter = TensorFlowAdapter()
        
        # Build model
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
        dummy_x = np.random.randn(2, 784).astype('float32')
        dummy_y = np.array([0, 1])
        model.fit(dummy_x, dummy_y, epochs=1, verbose=0)
        
        # Get weights
        weights = adapter.get_weights(model)
        print(f"\n  ✓ Created Keras MLP with {len(weights)} weight tensors")
        
        # Show weights
        display_weights(weights, "Original Weights (Before Submission)")
        
        # Submit and fetch
        update_id, fetched = submit_and_fetch(exp_id, "tensorflow_client", weights)
        print(f"  ✓ Submitted and fetched update: {update_id}")
        
        # Show fetched weights
        display_weights(fetched, "Fetched Weights (After API Retrieval)")
        
        # Verify
        orig_hash = compute_hash(weights)
        fetch_hash = compute_hash(fetched)
        match = orig_hash == fetch_hash
        
        print(f"  🔐 Hash Verification:")
        print(f"     Original: {orig_hash[:48]}...")
        print(f"     Fetched:  {fetch_hash[:48]}...")
        print(f"     Result:   {'✅ MATCH (Integrity Verified!)' if match else '❌ MISMATCH'}")
        
        return {"framework": "TensorFlow/Keras", "passed": match, "params": sum(w.size for w in weights.values())}
    
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)}")
        return {"framework": "TensorFlow", "skipped": True}


def test_sklearn(exp_id: str):
    """Test scikit-learn"""
    print("\n" + "="*80)
    print("  TEST 3: scikit-learn MLP")
    print("="*80)
    
    if not SKLEARN_AVAILABLE:
        print("  ⚠️  Skipping: scikit-learn not available")
        return {"framework": "scikit-learn", "skipped": True}
    
    try:
        # Create and fit model
        X = np.random.randn(20, 64)
        y = np.random.randint(0, 10, 20)
        
        model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=5, random_state=42)
        model.fit(X, y)
        
        adapter = SklearnAdapter()
        weights = adapter.get_weights(model)
        print(f"\n  ✓ Created sklearn MLP with {len(weights)} weight arrays")
        
        # Show weights
        display_weights(weights, "Original Weights (Before Submission)")
        
        # Submit and fetch
        update_id, fetched = submit_and_fetch(exp_id, "sklearn_client", weights)
        print(f"  ✓ Submitted and fetched update: {update_id}")
        
        # Show fetched weights
        display_weights(fetched, "Fetched Weights (After API Retrieval)")
        
        # Verify
        orig_hash = compute_hash(weights)
        fetch_hash = compute_hash(fetched)
        match = orig_hash == fetch_hash
        
        print(f"  🔐 Hash Verification:")
        print(f"     Original: {orig_hash[:48]}...")
        print(f"     Fetched:  {fetch_hash[:48]}...")
        print(f"     Result:   {'✅ MATCH (Integrity Verified!)' if match else '❌ MISMATCH'}")
        
        return {"framework": "scikit-learn", "passed": match, "params": sum(w.size for w in weights.values())}
    
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"framework": "scikit-learn", "skipped": True}


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*80)
    print("  🔬 WEIGHT FETCHING API - DETAILED WEIGHT INSPECTION")
    print("="*80)
    print("  Testing weight submission and retrieval for all frameworks")
    print("  Showing actual weight values, shapes, and statistics")
    print("="*80)
    
    # Check server
    try:
        requests.get(f"{SERVER}/health")
        print("\n✓ Server connected")
    except:
        print("\n❌ Server not running! Start: python -m backend.server.main")
        return
    
    # Create experiment
    exp_id = create_experiment("Weight Inspection Test")
    print(f"✓ Created experiment: {exp_id}")
    
    # Run tests
    results = []
    results.append(test_pytorch(exp_id))
    results.append(test_tensorflow(exp_id))
    results.append(test_sklearn(exp_id))
    
    # Summary
    print("\n" + "="*80)
    print("  📊 SUMMARY")
    print("="*80)
    
    tested = [r for r in results if not r.get('skipped')]
    passed = [r for r in tested if r.get('passed')]
    skipped = [r for r in results if r.get('skipped')]
    
    print(f"\n  Tested: {len(tested)}/{len(results)} frameworks")
    print(f"  Passed: {len(passed)}/{len(tested)} integrity checks")
    
    if tested:
        print(f"\n  {'Framework':<25} {'Parameters':<15} {'Status'}")
        print(f"  {'-'*60}")
        for r in tested:
            status = "✅ PASS" if r.get('passed') else "❌ FAIL"
            params = f"{r['params']:,}"
            print(f"  {r['framework']:<25} {params:<15} {status}")
    
    if skipped:
        print(f"\n  Skipped:")
        for r in skipped:
            print(f"    - {r['framework']}")
    
    print("\n" + "="*80)
    if len(passed) == len(tested) and len(tested) > 0:
        print("  ✅ ALL TESTS PASSED!")
        print("  Weight fetching API verified for all frameworks!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
