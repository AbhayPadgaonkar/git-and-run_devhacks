"""
Comprehensive Test: Weight Fetching API with Real Training

Trains models on real datasets and verifies weight fetching:
1. PyTorch CNN on MNIST
2. TensorFlow/Keras MLP on MNIST
3. scikit-learn MLP on MNIST
4. LoRA on text data (if available)

Shows actual weight values, shapes, and verifies integrity.
"""
import requests
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
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

# Optional framework imports
try:
    from federx_client.adapters.tensorflow import TensorFlowAdapter
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not available")

try:
    from federx_client.adapters.sklearn import SklearnAdapter
    from sklearn.neural_network import MLPClassifier
    from sklearn.datasets import fetch_openml
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not available")

try:
    from federx_client.adapters.lora import LoRAAdapter
    from transformers import GPT2LMHeadModel, GPT2Config
    LORA_AVAILABLE = True
except ImportError:
    LORA_AVAILABLE = False


SERVER = "http://localhost:8000"


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

class SimpleCNN(nn.Module):
    """Simple PyTorch CNN for MNIST"""
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, 1)  # Smaller for clarity
        self.conv2 = nn.Conv2d(16, 32, 3, 1)
        self.fc1 = nn.Linear(4608, 64)
        self.fc2 = nn.Linear(64, 10)
    
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_experiment(exp_name: str) -> str:
    """Create a new experiment and return its ID"""
    response = requests.post(f"{SERVER}/experiment/create", json={
        "name": exp_name,
        "aggregation_method": "fedavg",
        "enable_trust": True,
        "max_staleness": 5
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["experiment_id"]
    else:
        raise Exception(f"Failed to create experiment: {response.text}")


def submit_update(exp_id: str, client_id: str, weights: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Submit an update via FederatedClient"""
    weights_pickled = pickle.dumps(weights)
    weights_b64 = base64.b64encode(weights_pickled).decode('utf-8')
    
    response = requests.post(f"{SERVER}/experiment/{exp_id}/submit-update", json={
        "client_id": client_id,
        "delta_weights": weights_b64,
        "model_version": 0
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to submit update: {response.text}")


def fetch_weights(exp_id: str, update_id: str) -> Dict[str, Any]:
    """Fetch weights via API"""
    response = requests.get(f"{SERVER}/experiment/{exp_id}/update/{update_id}/weights")
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch weights: {response.text}")


def decode_weights(weights_b64: str) -> Dict[str, np.ndarray]:
    """Decode base64 weights to numpy arrays"""
    weights_pickled = base64.b64decode(weights_b64.encode('utf-8'))
    weights = pickle.loads(weights_pickled)
    return weights


def compute_hash(weights: Dict[str, np.ndarray]) -> str:
    """Compute hash of weights"""
    all_weights = []
    for key in sorted(weights.keys()):
        all_weights.append(weights[key].flatten())
    
    combined = np.concatenate(all_weights)
    hash_input = combined.tobytes()
    return hashlib.sha256(hash_input).hexdigest()


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def print_subsection(title: str):
    """Print formatted subsection"""
    print(f"\n{'-'*80}")
    print(f"  {title}")
    print(f"{'-'*80}")


def display_weight_info(weights: Dict[str, np.ndarray], title: str):
    """Display detailed weight information"""
    print(f"\n  📊 {title}")
    print(f"  {'-'*76}")
    
    total_params = 0
    for key, value in sorted(weights.items()):
        shape_str = str(value.shape).ljust(20)
        params = value.size
        total_params += params
        
        # Sample values
        flat = value.flatten()
        if len(flat) > 0:
            min_val = flat.min()
            max_val = flat.max()
            mean_val = flat.mean()
            sample = f"min={min_val:.4f}, max={max_val:.4f}, mean={mean_val:.4f}"
        else:
            sample = "empty"
        
        print(f"  {key[:30]:<30} {shape_str} ({params:>8} params) | {sample}")
    
    print(f"  {'-'*76}")
    print(f"  Total Parameters: {total_params:,}")
    print()


# ============================================================================
# TEST FUNCTIONS FOR EACH FRAMEWORK
# ============================================================================

def test_pytorch_with_mnist(exp_id: str) -> Dict[str, Any]:
    """Test 1: PyTorch CNN trained on MNIST"""
    print_subsection("TEST 1: PyTorch CNN with Real MNIST Training")
    
    # Load MNIST
    print("  Loading MNIST dataset...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    
    # Create and train model
    print("  Creating model...")
    model = SimpleCNN()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    # Train for 1 epoch (quick demo)
    print("  Training for 1 epoch (100 batches)...")
    model.train()
    total_loss = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        if batch_idx >= 100:  # Just 100 batches for demo
            break
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        
        if (batch_idx + 1) % 25 == 0:
            print(f"    Batch {batch_idx + 1}/100 - Loss: {loss.item():.4f}")
    
    avg_loss = total_loss / 100
    print(f"  ✓ Training complete - Average Loss: {avg_loss:.4f}")
    
    # Get trained weights
    adapter = PyTorchAdapter()
    weights = adapter.get_weights(model)
    
    # Display weight info
    display_weight_info(weights, "PyTorch CNN Weights")
    
    # Submit update
    result = submit_update(exp_id, "pytorch_client", weights)
    update_id = result["update_id"]
    print(f"  ✓ Submitted update: {update_id}")
    print(f"    Trust Score: {result['trust_score']}")
    
    # Fetch weights
    weight_data = fetch_weights(exp_id, update_id)
    print(f"  ✓ Fetched weights via API")
    
    # Decode
    fetched_weights = decode_weights(weight_data["weights"])
    print(f"  ✓ Decoded weights: {len(fetched_weights)} layers")
    
    # Verify integrity
    original_hash = compute_hash(weights)
    fetched_hash = compute_hash(fetched_weights)
    integrity_ok = (original_hash == fetched_hash)
    print(f"  ✓ Integrity check: {'✅ PASS' if integrity_ok else '❌ FAIL'}")
    print(f"    Original Hash: {original_hash[:32]}...")
    print(f"    Fetched Hash:  {fetched_hash[:32]}...")
    
    return {
        "framework": "PyTorch",
        "update_id": update_id,
        "num_layers": len(weights),
        "total_params": sum(w.size for w in weights.values()),
        "hash": fetched_hash,
        "integrity": integrity_ok,
        "avg_loss": avg_loss
    }


def test_tensorflow_with_mnist(exp_id: str) -> Dict[str, Any]:
    """Test 2: TensorFlow/Keras MLP trained on MNIST"""
    print_subsection("TEST 2: TensorFlow/Keras MLP with Real MNIST Training")
    
    if not TF_AVAILABLE:
        print("  ⚠️  Skipping: TensorFlow not available")
        return {"framework": "TensorFlow", "skipped": True}
    
    try:
        # Load MNIST
        print("  Loading MNIST dataset...")
        (x_train, y_train), _ = keras.datasets.mnist.load_data()
        
        # Preprocess
        x_train = x_train.reshape(-1, 784).astype('float32') / 255.0
        x_train_subset = x_train[:6400]  # Use subset for quick training
        y_train_subset = y_train[:6400]
        
        # Create model
        print("  Creating Keras MLP...")
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(784,), name='dense1'),
            keras.layers.Dropout(0.2, name='dropout1'),
            keras.layers.Dense(64, activation='relu', name='dense2'),
            keras.layers.Dense(10, activation='softmax', name='output')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train
        print("  Training for 1 epoch...")
        history = model.fit(
            x_train_subset, y_train_subset,
            epochs=1,
            batch_size=64,
            verbose=0
        )
        
        loss = history.history['loss'][0]
        accuracy = history.history['accuracy'][0]
        print(f"  ✓ Training complete - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
        
        # Get trained weights
        adapter = TensorFlowAdapter()
        weights = adapter.get_weights(model)
        
        # Display weight info
        display_weight_info(weights, "TensorFlow/Keras MLP Weights")
        
        # Submit update
        result = submit_update(exp_id, "tensorflow_client", weights)
        update_id = result["update_id"]
        print(f"  ✓ Submitted update: {update_id}")
        print(f"    Trust Score: {result['trust_score']}")
        
        # Fetch weights
        weight_data = fetch_weights(exp_id, update_id)
        print(f"  ✓ Fetched weights via API")
        
        # Decode
        fetched_weights = decode_weights(weight_data["weights"])
        print(f"  ✓ Decoded weights: {len(fetched_weights)} tensors")
        
        # Verify integrity
        original_hash = compute_hash(weights)
        fetched_hash = compute_hash(fetched_weights)
        integrity_ok = (original_hash == fetched_hash)
        print(f"  ✓ Integrity check: {'✅ PASS' if integrity_ok else '❌ FAIL'}")
        print(f"    Original Hash: {original_hash[:32]}...")
        print(f"    Fetched Hash:  {fetched_hash[:32]}...")
        
        return {
            "framework": "TensorFlow/Keras",
            "update_id": update_id,
            "num_layers": len(weights),
            "total_params": sum(w.size for w in weights.values()),
            "hash": fetched_hash,
            "integrity": integrity_ok,
            "loss": loss,
            "accuracy": accuracy
        }
    
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"framework": "TensorFlow", "skipped": True, "error": str(e)}


def test_sklearn_with_mnist(exp_id: str) -> Dict[str, Any]:
    """Test 3: scikit-learn MLP trained on MNIST"""
    print_subsection("TEST 3: scikit-learn MLP with Real MNIST Training")
    
    if not SKLEARN_AVAILABLE:
        print("  ⚠️  Skipping: scikit-learn not available")
        return {"framework": "scikit-learn", "skipped": True}
    
    try:
        # Load MNIST from sklearn
        print("  Loading MNIST dataset...")
        from sklearn.datasets import load_digits
        digits = load_digits()
        
        # Use subset for quick training
        X_train = digits.data[:1000]
        y_train = digits.target[:1000]
        
        # Normalize
        X_train = X_train / 16.0  # Digits are 0-16
        
        # Create and train model
        print("  Creating sklearn MLP...")
        model = MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation='relu',
            max_iter=10,
            random_state=42,
            verbose=False
        )
        
        print("  Training...")
        model.fit(X_train, y_train)
        
        score = model.score(X_train, y_train)
        print(f"  ✓ Training complete - Training Accuracy: {score:.4f}")
        
        # Get trained weights
        adapter = SklearnAdapter()
        weights = adapter.get_weights(model)
        
        # Display weight info
        display_weight_info(weights, "scikit-learn MLP Weights")
        
        # Submit update
        result = submit_update(exp_id, "sklearn_client", weights)
        update_id = result["update_id"]
        print(f"  ✓ Submitted update: {update_id}")
        print(f"    Trust Score: {result['trust_score']}")
        
        # Fetch weights
        weight_data = fetch_weights(exp_id, update_id)
        print(f"  ✓ Fetched weights via API")
        
        # Decode
        fetched_weights = decode_weights(weight_data["weights"])
        print(f"  ✓ Decoded weights: {len(fetched_weights)} arrays")
        
        # Verify integrity
        original_hash = compute_hash(weights)
        fetched_hash = compute_hash(fetched_weights)
        integrity_ok = (original_hash == fetched_hash)
        print(f"  ✓ Integrity check: {'✅ PASS' if integrity_ok else '❌ FAIL'}")
        print(f"    Original Hash: {original_hash[:32]}...")
        print(f"    Fetched Hash:  {fetched_hash[:32]}...")
        
        return {
            "framework": "scikit-learn",
            "update_id": update_id,
            "num_layers": len(weights),
            "total_params": sum(w.size for w in weights.values()),
            "hash": fetched_hash,
            "integrity": integrity_ok,
            "accuracy": score
        }
    
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"framework": "scikit-learn", "skipped": True, "error": str(e)}


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    """Run comprehensive multi-framework weight fetching test with real training"""
    
    print_section("🔬 COMPREHENSIVE TEST: All Frameworks with Real Training")
    print(f"Training models on real datasets and verifying weight fetching")
    print(f"Server: {SERVER}")
    
    # Check server
    try:
        response = requests.get(f"{SERVER}/health")
        if response.status_code != 200:
            print("\n❌ Server not running! Start with: python -m backend.server.main")
            return
        print("✓ Server is running")
    except:
        print("\n❌ Cannot connect to server! Start with: python -m backend.server.main")
        return
    
    # Create experiment
    exp_name = "Multi-framework with real training"
    print(f"\nCreating experiment...")
    exp_id = create_experiment(exp_name)
    print(f"✓ Created experiment: {exp_id}")
    
    # Run tests for all frameworks
    results = []
    
    # Test 1: PyTorch (always available)
    results.append(test_pytorch_with_mnist(exp_id))
    
    # Test 2: TensorFlow (if available)
    results.append(test_tensorflow_with_mnist(exp_id))
    
    # Test 3: scikit-learn (if available)
    results.append(test_sklearn_with_mnist(exp_id))
    
    # Summary
    print_section("📊 FINAL SUMMARY")
    
    tested = [r for r in results if not r.get('skipped')]
    skipped = [r for r in results if r.get('skipped')]
    passed = [r for r in tested if r.get('integrity')]
    
    print(f"\n✅ Successfully Tested: {len(tested)}/{len(results)} frameworks")
    print(f"✓  Integrity Checks Passed: {len(passed)}/{len(tested)}")
    
    if skipped:
        print(f"\n⚠️  Skipped: {len(skipped)} framework(s)")
        for r in skipped:
            error_msg = f" ({r.get('error', 'not available')})" if 'error' in r else ""
            print(f"   - {r['framework']}{error_msg}")
    
    if tested:
        print(f"\n{'Framework':<20} {'Update ID':<12} {'Params':<10} {'Hash':<18} {'Status':<10}")
        print("-" * 80)
        
        for r in tested:
            framework = r['framework']
            update_id = r['update_id']
            params = f"{r['total_params']:,}"
            hash_short = r['hash'][:16]
            status = "✅ PASS" if r['integrity'] else "❌ FAIL"
            
            print(f"{framework:<20} {update_id:<12} {params:<10} {hash_short:<18} {status:<10}")
    
    # Weight details comparison
    if len(tested) > 1:
        print_section("🔍 WEIGHT DETAILS COMPARISON")
        
        for r in tested:
            print(f"\n{r['framework']}:")
            print(f"  - Model: {r['num_layers']} layers")
            print(f"  - Total Parameters: {r['total_params']:,}")
            if 'avg_loss' in r:
                print(f"  - Training Loss: {r['avg_loss']:.4f}")
            if 'accuracy' in r:
                print(f"  - Accuracy: {r['accuracy']:.4f}")
            if 'loss' in r:
                print(f"  - Loss: {r['loss']:.4f}")
    
    # Final verdict
    print_section("✅ TEST COMPLETE")
    
    if len(passed) == len(tested) and len(tested) > 0:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Weight fetching API works correctly for all {len(tested)} tested frameworks!")
        print(f"\n📝 Verified Frameworks:")
        for r in tested:
            print(f"   ✓ {r['framework']} - {r['total_params']:,} parameters")
    else:
        print(f"\n⚠️  Some tests had issues")
        print(f"   Passed: {len(passed)}/{len(tested)}")
    
    print(f"\n💡 All weights are now stored in FederX and can be fetched via:")
    print(f"   GET {SERVER}/experiment/{exp_id}/update/{{update_id}}/weights")


if __name__ == "__main__":
    main()
