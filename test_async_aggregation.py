"""
Test Async Aggregation - Each update triggers immediate global model update
"""
import numpy as np
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "client"))
from federx_client.client import FederatedClient
from federx_client.adapters.pytorch import PyTorchAdapter
from federx_client.utils.serialization import serialize_weights

import torch
import torch.nn as nn
from sklearn.datasets import load_digits

print("\n" + "="*70)
print("⚡ ASYNC AGGREGATION TEST")
print("="*70)
print("Testing: Each client update immediately triggers global model update")
print("="*70)

SERVER_URL = "http://localhost:8000"

# Simple PyTorch model
class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Load data
print("\n📊 Loading digits dataset...")
digits = load_digits()
X_data = torch.FloatTensor(digits.data / 16.0)
y_data = torch.LongTensor(digits.target)

# Create experiment
print("\n🔬 Creating experiment...")
model = SimpleNet()
adapter = PyTorchAdapter()
init_weights = adapter.get_weights(model)

response = requests.post(
    f"{SERVER_URL}/experiment/create",
    json={
        "name": "Async Aggregation Test",
        "aggregation_method": "fedavg",
        "enable_trust": False,  # Disable trust for simple test
        "enable_clustering": False,
        "initial_weights": serialize_weights(init_weights)
    }
)
result = response.json()
exp_id = result["experiment_id"]
print(f"✓ Experiment created: {exp_id}")

# Check initial global model version
response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/global-model")
initial_version = response.json()["version"]
print(f"✓ Initial global model version: {initial_version}")

# Submit 5 client updates and watch version increment
print("\n⚡ Submitting 5 client updates (async aggregation):")
print("-" * 70)

for i in range(5):
    client_id = f"client_{i}"
    
    # Fetch current global model
    fl_client = FederatedClient(SERVER_URL, exp_id, client_id)
    global_weights = fl_client.fetch_global_model()
    current_version = fl_client.current_version
    
    # Set model to global weights
    adapter.set_weights(model, global_weights)
    
    # Train for 1 step (minimal training)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    
    # Use small batch
    batch_x = X_data[:32]
    batch_y = y_data[:32]
    
    optimizer.zero_grad()
    outputs = model(batch_x)
    loss = criterion(outputs, batch_y)
    loss.backward()
    optimizer.step()
    
    # Get new weights and compute delta
    new_weights = adapter.get_weights(model)
    delta = {k: new_weights[k] - global_weights[k] for k in global_weights.keys()}
    
    # Submit update
    print(f"\n  Client {i}:")
    print(f"    📤 Submitting update (current global v{current_version})...")
    
    update_response = fl_client.submit_update(delta)
    
    if update_response["accepted"]:
        new_version = update_response.get("new_global_version", "unknown")
        print(f"    ✅ Accepted! Global model immediately updated to v{new_version}")
        print(f"    💬 Message: {update_response['message']}")
        
        # Verify version actually changed
        if new_version == current_version + 1:
            print(f"    ✨ Confirmed: Version incremented {current_version} → {new_version}")
        else:
            print(f"    ⚠️  Warning: Expected v{current_version + 1}, got v{new_version}")
    else:
        print(f"    ❌ Rejected: {update_response.get('message')}")

# Final verification
print("\n" + "="*70)
print("📊 FINAL VERIFICATION")
print("="*70)

response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/status")
status = response.json()

print(f"✓ Initial version: {initial_version}")
print(f"✓ Final version: {status['clusters']['cluster_0']['version']}")
print(f"✓ Total updates submitted: {status['total_updates']}")
print(f"✓ Accepted updates: {status['accepted_updates']}")
print(f"✓ Expected version: {initial_version + status['accepted_updates']}")

final_version = status['clusters']['cluster_0']['version']
expected_version = initial_version + status['accepted_updates']

if final_version == expected_version:
    print("\n🎉 SUCCESS! Async aggregation working perfectly!")
    print(f"   Each of the {status['accepted_updates']} updates immediately triggered aggregation")
else:
    print(f"\n⚠️  WARNING: Version mismatch!")
    print(f"   Expected: v{expected_version}, Got: v{final_version}")

print("="*70)
