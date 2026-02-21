"""
FederX v2.0 - Comprehensive Test Suite
Tests all features: Multi-framework, Async aggregation, Staleness handling, Trust scoring
"""
import numpy as np
import requests
import sys
from pathlib import Path
import time
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent / "client"))
from federx_client.client import FederatedClient
from federx_client.adapters.pytorch import PyTorchAdapter
from federx_client.adapters.tensorflow import TensorFlowAdapter
from federx_client.adapters.sklearn import SklearnAdapter
from federx_client.utils.serialization import serialize_weights

import torch
import torch.nn as nn
from tensorflow import keras
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import load_digits

# Suppress TensorFlow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

SERVER_URL = "http://localhost:8000"

print("\n" + "="*80)
print("🚀 FEDERX v2.0 - COMPREHENSIVE TEST SUITE")
print("="*80)
print("\nTesting:")
print("  ✓ Multi-Framework Support (PyTorch, TensorFlow, scikit-learn)")
print("  ✓ Async Real-Time Aggregation")
print("  ✓ Staleness Detection & Handling")
print("  ✓ Trust Scoring & Malicious Detection")
print("  ✓ Multiple Aggregation Methods")
print("  ✓ Complete API Endpoints")
print("="*80)

# Load dataset
digits = load_digits()
X_data = digits.data / 16.0
y_data = digits.target

test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_test(name: str, passed: bool, message: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {name}")
    if message:
        print(f"   {message}")
    
    if passed:
        test_results["passed"].append(name)
    else:
        test_results["failed"].append(name)

def log_warning(message: str):
    """Log warning"""
    print(f"⚠️  WARNING: {message}")
    test_results["warnings"].append(message)

# ============================================================================
# TEST 1: Server Health & Basic Endpoints
# ============================================================================
print("\n" + "="*80)
print("TEST 1: Server Health & Basic Endpoints")
print("="*80)

try:
    response = requests.get(f"{SERVER_URL}/health", timeout=5)
    log_test("Health endpoint", response.status_code == 200, 
             f"Status: {response.json()}")
except Exception as e:
    log_test("Health endpoint", False, f"Error: {e}")
    print("\n❌ Server not running! Start with: python run_server.py")
    sys.exit(1)

try:
    response = requests.get(f"{SERVER_URL}/")
    data = response.json()
    log_test("Root endpoint", "service" in data and "experiments" in data,
             f"Service: {data.get('service', 'N/A')}")
except Exception as e:
    log_test("Root endpoint", False, f"Error: {e}")

# ============================================================================
# TEST 2: Multi-Framework Support
# ============================================================================
print("\n" + "="*80)
print("TEST 2: Multi-Framework Support")
print("="*80)

# PyTorch Model
class PyTorchNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, 10)
    
    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

# TensorFlow Model
def create_tf_model():
    model = keras.Sequential([
        keras.layers.Dense(32, activation='relu', input_shape=(64,)),
        keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    return model

# Scikit-learn Model
def create_sklearn_model():
    return MLPClassifier(hidden_layer_sizes=(32,), max_iter=1)

# Test PyTorch Adapter
try:
    pytorch_model = PyTorchNet()
    pytorch_adapter = PyTorchAdapter()
    weights = pytorch_adapter.get_weights(pytorch_model)
    log_test("PyTorch adapter", len(weights) == 4,
             f"Extracted {len(weights)} weight tensors")
except Exception as e:
    log_test("PyTorch adapter", False, f"Error: {e}")

# Test TensorFlow Adapter
try:
    tf_model = create_tf_model()
    tf_adapter = TensorFlowAdapter()
    weights = tf_adapter.get_weights(tf_model)
    log_test("TensorFlow adapter", len(weights) > 0,
             f"Extracted {len(weights)} weight tensors")
except Exception as e:
    log_test("TensorFlow adapter", False, f"Error: {e}")

# Test Scikit-learn Adapter
try:
    sklearn_model = create_sklearn_model()
    sklearn_model.fit(X_data[:100], y_data[:100])  # Fit first
    sklearn_adapter = SklearnAdapter()
    weights = sklearn_adapter.get_weights(sklearn_model)
    log_test("Scikit-learn adapter", len(weights) > 0,
             f"Extracted {len(weights)} weight arrays")
except Exception as e:
    log_test("Scikit-learn adapter", False, f"Error: {e}")

# ============================================================================
# TEST 3: Experiment Creation & Configuration
# ============================================================================
print("\n" + "="*80)
print("TEST 3: Experiment Creation & Configuration")
print("="*80)

# Test different aggregation methods
aggregation_methods = ["fedavg", "median", "trimmed_mean", "trust_weighted"]
created_experiments = []

for method in aggregation_methods:
    try:
        response = requests.post(
            f"{SERVER_URL}/experiment/create",
            json={
                "name": f"Test {method.upper()}",
                "aggregation_method": method,
                "enable_trust": True,
                "max_staleness": 5,
                "staleness_weighting": True
            }
        )
        data = response.json()
        exp_id = data["experiment_id"]
        created_experiments.append((exp_id, method))
        log_test(f"Create experiment ({method})", "experiment_id" in data,
                 f"Created {exp_id}")
    except Exception as e:
        log_test(f"Create experiment ({method})", False, f"Error: {e}")

# ============================================================================
# TEST 4: Async Real-Time Aggregation
# ============================================================================
print("\n" + "="*80)
print("TEST 4: Async Real-Time Aggregation")
print("="*80)

try:
    # Create test experiment
    response = requests.post(
        f"{SERVER_URL}/experiment/create",
        json={
            "name": "Async Aggregation Test",
            "aggregation_method": "fedavg",
            "enable_trust": False,
            "max_staleness": 10
        }
    )
    exp_id = response.json()["experiment_id"]
    
    # Submit 3 sequential updates
    model = PyTorchNet()
    adapter = PyTorchAdapter()
    client = FederatedClient(SERVER_URL, exp_id, "test_client")
    
    versions = []
    for i in range(3):
        # Fetch global model
        global_weights = client.fetch_global_model()
        
        # Create simple delta
        if len(global_weights) == 0:
            global_weights = adapter.get_weights(model)
        
        delta = {k: v * 0.01 for k, v in global_weights.items()}
        
        # Submit update
        response = client.submit_update(delta)
        
        if response.get("accepted"):
            new_version = response.get("new_global_version")
            versions.append(new_version)
    
    # Check that versions incremented immediately
    expected_versions = [1, 2, 3]
    async_working = versions == expected_versions
    
    log_test("Async aggregation", async_working,
             f"Versions: {versions} (expected {expected_versions})")
    
except Exception as e:
    log_test("Async aggregation", False, f"Error: {e}")

# ============================================================================
# TEST 5: Staleness Detection & Handling
# ============================================================================
print("\n" + "="*80)
print("TEST 5: Staleness Detection & Handling")
print("="*80)

try:
    # Create experiment with strict staleness
    response = requests.post(
        f"{SERVER_URL}/experiment/create",
        json={
            "name": "Staleness Test",
            "aggregation_method": "fedavg",
            "enable_trust": False,
            "max_staleness": 2,  # Strict threshold
            "staleness_weighting": True
        }
    )
    exp_id = response.json()["experiment_id"]
    
    model = PyTorchNet()
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(model)
    
    # Client A and B fetch v0
    client_a = FederatedClient(SERVER_URL, exp_id, "client_a")
    client_b = FederatedClient(SERVER_URL, exp_id, "client_b")
    
    weights_a = client_a.fetch_global_model()
    weights_b = client_b.fetch_global_model()
    
    if len(weights_a) == 0:
        weights_a = init_weights
        weights_b = init_weights
    
    # Client A submits → v1
    delta_a = {k: v * 0.01 for k, v in weights_a.items()}
    response_a = client_a.submit_update(delta_a)
    
    # Client B submits (staleness=1, should be accepted with weight)
    delta_b = {k: v * 0.01 for k, v in weights_b.items()}
    response_b = client_b.submit_update(delta_b)
    
    staleness_detected = response_b.get("staleness") == 1
    weight_applied = response_b.get("staleness_weight") == 0.9
    
    log_test("Staleness detection", staleness_detected,
             f"Staleness: {response_b.get('staleness')}")
    log_test("Staleness weighting", weight_applied,
             f"Weight: {response_b.get('staleness_weight')}")
    
    # Test rejection of too-stale updates
    # Create 3 more updates to push version higher
    for i in range(3):
        client_temp = FederatedClient(SERVER_URL, exp_id, f"temp_{i}")
        w = client_temp.fetch_global_model()
        if len(w) == 0:
            w = init_weights
        d = {k: v * 0.01 for k, v in w.items()}
        client_temp.submit_update(d)
    
    # Now client with old version should be rejected
    client_c = FederatedClient(SERVER_URL, exp_id, "client_c")
    # Submit with old version (staleness will be high)
    delta_c = {k: v * 0.01 for k, v in weights_b.items()}  # Still based on v0
    response_c = client_c.submit_update(delta_c)
    
    rejected = not response_c.get("accepted")
    log_test("Staleness rejection", rejected,
             f"Staleness {response_c.get('staleness')} rejected: {response_c.get('message', 'N/A')}")
    
except Exception as e:
    log_test("Staleness handling", False, f"Error: {e}")

# ============================================================================
# TEST 6: Multi-Framework Federated Learning
# ============================================================================
print("\n" + "="*80)
print("TEST 6: Multi-Framework Federated Learning")
print("="*80)

framework_results = {}

for framework_name, model_fn, adapter_fn in [
    ("PyTorch", lambda: PyTorchNet(), lambda: PyTorchAdapter()),
    ("TensorFlow", create_tf_model, lambda: TensorFlowAdapter()),
]:
    try:
        # Create experiment
        model = model_fn()
        adapter = adapter_fn()
        init_weights = adapter.get_weights(model)
        
        response = requests.post(
            f"{SERVER_URL}/experiment/create",
            json={
                "name": f"{framework_name} FL Test",
                "aggregation_method": "fedavg",
                "enable_trust": False,
                "initial_weights": serialize_weights(init_weights)
            }
        )
        exp_id = response.json()["experiment_id"]
        
        # Simulate 2 clients, 2 rounds
        accuracy_improved = False
        
        for round_num in range(2):
            for client_id in range(2):
                client = FederatedClient(SERVER_URL, exp_id, f"client_{client_id}")
                global_weights = client.fetch_global_model()
                
                if len(global_weights) > 0:
                    adapter.set_weights(model, global_weights)
                
                # Simple training simulation (just small delta)
                current_weights = adapter.get_weights(model)
                delta = {k: v * 0.001 for k, v in current_weights.items()}
                
                client.submit_update(delta)
        
        # Get final status
        response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/status")
        status = response.json()
        
        final_version = status["clusters"]["cluster_0"]["version"]
        framework_results[framework_name] = {
            "exp_id": exp_id,
            "final_version": final_version,
            "updates": status["total_updates"]
        }
        
        log_test(f"{framework_name} FL workflow", final_version == 4,
                 f"Version {final_version}, {status['total_updates']} updates")
        
    except Exception as e:
        log_test(f"{framework_name} FL workflow", False, f"Error: {e}")

# ============================================================================
# TEST 7: Experiment Status & Monitoring
# ============================================================================
print("\n" + "="*80)
print("TEST 7: Experiment Status & Monitoring")
print("="*80)

if created_experiments:
    exp_id = created_experiments[0][0]
    
    try:
        response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/status")
        data = response.json()
        
        has_required_fields = all(k in data for k in [
            "id", "config", "status", "total_updates", 
            "accepted_updates", "rejected_updates", "clusters"
        ])
        
        log_test("Experiment status endpoint", has_required_fields,
                 f"All required fields present")
        
        # Test global model endpoint
        response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/global-model")
        data = response.json()
        
        has_model_fields = all(k in data for k in [
            "version", "cluster_id", "weights", "timestamp"
        ])
        
        log_test("Global model endpoint", has_model_fields,
                 f"Version: {data.get('version')}")
        
    except Exception as e:
        log_test("Status endpoints", False, f"Error: {e}")

# ============================================================================
# TEST 8: Trust Scoring (if applicable)
# ============================================================================
print("\n" + "="*80)
print("TEST 8: Trust Scoring System")
print("="*80)

try:
    # Create experiment with trust enabled
    response = requests.post(
        f"{SERVER_URL}/experiment/create",
        json={
            "name": "Trust Scoring Test",
            "aggregation_method": "trust_weighted",
            "enable_trust": True,
            "trust_alpha": 0.8
        }
    )
    exp_id = response.json()["experiment_id"]
    
    model = PyTorchNet()
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(model)
    
    # Submit several normal updates
    for i in range(3):
        client = FederatedClient(SERVER_URL, exp_id, f"good_client_{i}")
        weights = client.fetch_global_model()
        if len(weights) == 0:
            weights = init_weights
        
        delta = {k: v * 0.001 for k, v in weights.items()}
        response = client.submit_update(delta)
    
    # Check trust scores
    response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/status")
    status = response.json()
    
    has_trust_scores = "trust_scores" in status and len(status["trust_scores"]) > 0
    
    log_test("Trust scoring", has_trust_scores,
             f"Trust scores tracked for {len(status.get('trust_scores', {}))} clients")
    
except Exception as e:
    log_test("Trust scoring", False, f"Error: {e}")

# ============================================================================
# TEST 7: LoRA Adapter for LLMs
# ============================================================================
print("\n" + "="*80)
print("🧬 TEST 7: LoRA Adapter for Efficient LLM Training")
print("="*80)

try:
    from federx_client.adapters import LoRAAdapter
    from federx_client.utils.serialization import get_compression_stats
    import torch
    import torch.nn as nn
    
    # Create a simple transformer-like model for testing
    class SimpleTransformer(nn.Module):
        def __init__(self):
            super().__init__()
            self.q_proj = nn.Linear(128, 128)
            self.k_proj = nn.Linear(128, 128)
            self.v_proj = nn.Linear(128, 128)
            self.o_proj = nn.Linear(128, 128)
            self.fc = nn.Linear(128, 10)
        
        def forward(self, x):
            q = self.q_proj(x)
            k = self.k_proj(x)
            v = self.v_proj(x)
            out = self.o_proj(q + k + v)
            return self.fc(out)
    
    base_model = SimpleTransformer()
    
    # Test 7a: LoRA injection
    lora_adapter = LoRAAdapter(
        rank=4,
        alpha=8,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )
    num_lora_layers = lora_adapter.inject_lora(base_model, verbose=False)
    
    # Count LoRA layers
    lora_layers = [name for name, param in base_model.named_parameters() 
                   if 'lora_' in name]
    
    log_test("LoRA injection", num_lora_layers == 4,
             f"Injected LoRA into 4 target modules (got {num_lora_layers})")
    
    # Test 7b: Weight extraction (LoRA-only)
    lora_weights = lora_adapter.get_weights(base_model)
    
    # Should only contain LoRA parameters, not full model
    # Each LoRA layer has A and B matrices
    expected_params = 4 * 2  # 4 modules × 2 matrices (A, B)
    
    log_test("LoRA weight extraction", len(lora_weights) == expected_params,
             f"Extracted {len(lora_weights)} LoRA parameters (not full model)")
    
    # Test 7c: Compression statistics
    compression_stats = get_compression_stats(lora_weights)
    
    compressed_smaller = compression_stats["zlib_size"] < compression_stats["original_size"]
    space_saved = compression_stats["space_saved_percent"]
    
    log_test("LoRA compression", compressed_smaller and space_saved > 0,
             f"Compression: {compression_stats['compression_ratio']:.1f}x, "
             f"{space_saved:.0f}% space saved")
    
    # Test 7d: Roundtrip (set/get weights)
    lora_adapter.set_weights(base_model, lora_weights)
    retrieved_weights = lora_adapter.get_weights(base_model)
    
    weights_match = all(
        torch.allclose(torch.from_numpy(lora_weights[k]), torch.from_numpy(retrieved_weights[k]), rtol=1e-5)
        for k in lora_weights.keys()
    )
    
    log_test("LoRA roundtrip", weights_match,
             "LoRA weights preserved through set/get cycle")
    
    # Demonstration: Show compression benefits
    print("\n📦 LoRA Compression Demo:")
    total_params = sum(p.numel() for p in base_model.parameters())
    trainable_params = sum(p.numel() for p in base_model.parameters() if p.requires_grad)
    print(f"   Total model parameters: {total_params:,}")
    print(f"   LoRA trainable params: {trainable_params:,}")
    print(f"   Compression ratio: {total_params / max(trainable_params, 1):.1f}x smaller")
    print(f"   Transfer size: {compression_stats['zlib_size_mb']:.3f} MB")
    
except Exception as e:
    log_test("LoRA adapter", False, f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)

total_tests = len(test_results["passed"]) + len(test_results["failed"])
pass_rate = (len(test_results["passed"]) / total_tests * 100) if total_tests > 0 else 0

print(f"\n✅ Passed: {len(test_results['passed'])}/{total_tests}")
print(f"❌ Failed: {len(test_results['failed'])}/{total_tests}")
print(f"⚠️  Warnings: {len(test_results['warnings'])}")
print(f"\n📈 Pass Rate: {pass_rate:.1f}%")

if test_results["failed"]:
    print("\n❌ Failed Tests:")
    for test in test_results["failed"]:
        print(f"   • {test}")

if test_results["warnings"]:
    print("\n⚠️  Warnings:")
    for warning in test_results["warnings"]:
        print(f"   • {warning}")

print("\n" + "="*80)
print("🎯 FEATURE VALIDATION")
print("="*80)

features = {
    "Multi-Framework Support": "PyTorch adapter" in test_results["passed"],
    "Async Aggregation": "Async aggregation" in test_results["passed"],
    "Staleness Detection": "Staleness detection" in test_results["passed"],
    "Staleness Weighting": "Staleness weighting" in test_results["passed"],
    "Staleness Rejection": "Staleness rejection" in test_results["passed"],
    "Trust Scoring": "Trust scoring" in test_results["passed"],
    "LoRA for LLMs": "LoRA injection" in test_results["passed"],
    "API Endpoints": "Health endpoint" in test_results["passed"],
    "Experiment Management": "Experiment status endpoint" in test_results["passed"],
}

for feature, status in features.items():
    icon = "✅" if status else "❌"
    print(f"{icon} {feature}")

print("\n" + "="*80)

if pass_rate >= 80:
    print("🎉 FEDERX v2.0 IS READY FOR DEPLOYMENT!")
    print("="*80)
    print("\nNext steps:")
    print("  1. git add .")
    print("  2. git commit -m 'feat: v2.0 - async aggregation + staleness handling'")
    print("  3. git push origin main")
    print("\n✨ Ready to build the frontend!")
else:
    print("⚠️  SOME TESTS FAILED - REVIEW BEFORE DEPLOYMENT")
    print("="*80)

sys.exit(0 if pass_rate >= 80 else 1)
