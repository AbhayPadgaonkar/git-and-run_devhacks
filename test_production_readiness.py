"""
Production Readiness Tests for FederX Backend
Tests all aggregation methods, trust system, and error handling
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import requests
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "client"))
from federx_client.client import FederatedClient
from federx_client.adapters.pytorch import PyTorchAdapter
from federx_client.utils.serialization import serialize_weights


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        return torch.log_softmax(self.fc2(x), dim=1)


def train_epoch(model, device, train_loader, optimizer):
    model.train()
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = torch.nn.functional.nll_loss(output, target)
        loss.backward()
        optimizer.step()


def test_model(model, device, test_loader):
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += torch.nn.functional.nll_loss(output, target, reduction='sum').item()
            correct += output.argmax(dim=1).eq(target).sum().item()
    return test_loss / len(test_loader.dataset), 100.0 * correct / len(test_loader.dataset)


def run_fl_test(server_url, experiment_name, aggregation_method, enable_trust, num_rounds=2):
    """Run a federated learning test with specific configuration"""
    device = torch.device("cpu")
    
    print(f"\n{'='*70}")
    print(f"TEST: {experiment_name}")
    print(f"Aggregation: {aggregation_method} | Trust: {enable_trust}")
    print('='*70)
    
    # Load MNIST
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    train_dataset = datasets.MNIST('./data', train=True, download=False, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    # Create 3 clients
    num_clients = 3
    samples_per_client = 10000
    client_datasets = []
    for i in range(num_clients):
        start = i * samples_per_client
        indices = list(range(start, start + samples_per_client))
        client_datasets.append(Subset(train_dataset, indices))
    
    # Initialize model
    torch.manual_seed(42)
    init_model = SimpleCNN().to(device)
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(init_model)
    
    # Create experiment
    response = requests.post(
        f"{server_url}/experiment/create",
        json={
            "name": experiment_name,
            "aggregation_method": aggregation_method,
            "enable_trust": enable_trust,
            "enable_clustering": False,
            "initial_weights": serialize_weights(init_weights)
        }
    )
    
    if response.status_code != 200:
        print(f"  FAILED: {response.text}")
        return None
    
    experiment_id = response.json()["experiment_id"]
    
    # Run FL rounds
    results = []
    for round_num in range(num_rounds):
        # Each client trains
        for client_id in range(num_clients):
            fed_client = FederatedClient(
                server_url=server_url,
                experiment_id=experiment_id,
                client_id=f"client_{client_id}"
            )
            
            global_weights = fed_client.fetch_global_model()
            local_model = SimpleCNN().to(device)
            adapter.set_weights(local_model, global_weights)
            old_weights = adapter.get_weights(local_model)
            
            # Train
            train_loader = DataLoader(client_datasets[client_id], batch_size=32, shuffle=True)
            optimizer = optim.Adam(local_model.parameters(), lr=0.001)
            for _ in range(1):
                train_epoch(local_model, device, train_loader, optimizer)
            
            # Submit delta
            new_weights = adapter.get_weights(local_model)
            delta = {k: new_weights[k] - old_weights[k] for k in new_weights.keys()}
            fed_client.submit_update(delta)
        
        # Aggregate
        requests.post(f"{server_url}/experiment/{experiment_id}/aggregate", params={"cluster_id": "cluster_0"})
        
        # Test
        global_weights = fed_client.fetch_global_model()
        global_model = SimpleCNN().to(device)
        adapter.set_weights(global_model, global_weights)
        loss, acc = test_model(global_model, device, test_loader)
        results.append({"round": round_num + 1, "loss": loss, "accuracy": acc})
        print(f"  Round {round_num + 1}: Loss={loss:.4f}, Accuracy={acc:.2f}%")
    
    # Get final stats
    status_response = requests.get(f"{server_url}/experiment/{experiment_id}/status")
    if status_response.status_code == 200:
        status = status_response.json()
        print(f"\n  Final Stats:")
        print(f"    Total updates: {status['total_updates']}")
        print(f"    Accepted: {status['accepted_updates']}")
        print(f"    Rejected: {status['rejected_updates']}")
    
    return results


def test_malicious_detection(server_url):
    """Test malicious update detection"""
    print(f"\n{'='*70}")
    print("TEST: Malicious Update Detection")
    print('='*70)
    
    device = torch.device("cpu")
    torch.manual_seed(42)
    init_model = SimpleCNN().to(device)
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(init_model)
    
    # Create experiment with trust enabled
    response = requests.post(
        f"{server_url}/experiment/create",
        json={
            "name": "Malicious_Detection_Test",
            "aggregation_method": "fedavg",
            "enable_trust": True,
            "initial_weights": serialize_weights(init_weights)
        }
    )
    experiment_id = response.json()["experiment_id"]
    
    # Submit 3 normal updates first
    for i in range(3):
        fed_client = FederatedClient(server_url, experiment_id, f"honest_{i}")
        weights = fed_client.fetch_global_model()
        # Small normal delta
        delta = {k: np.random.randn(*v.shape).astype(np.float32) * 0.01 for k, v in weights.items()}
        fed_client.submit_update(delta)
    
    # Submit malicious update (10x larger)
    fed_client = FederatedClient(server_url, experiment_id, "malicious")
    weights = fed_client.fetch_global_model()
    malicious_delta = {k: np.random.randn(*v.shape).astype(np.float32) *10 for k, v in weights.items()}
    response = fed_client.submit_update(malicious_delta)
    
    if not response.get('accepted'):
        print(f"  SUCCESS: Malicious update detected and rejected")
        print(f"  Reason: {response.get('message', 'unknown')}")
        return True
    else:
        print(f"  WARNING: Malicious update was accepted (trust score: {response.get('trust_score')})")
        return False


def main():
    server_url = "http://localhost:8000"
    
    print("\n" + "="*70)
    print("FEDERX BACKEND - PRODUCTION READINESS TESTS")
    print("="*70)
    
    # Test 1: FedAvg
    run_fl_test(server_url, "Test_FedAvg", "fedavg", enable_trust=False)
    
    # Test 2: Median Aggregation
    run_fl_test(server_url, "Test_Median", "median", enable_trust=False)
    
    # Test 3: Trimmed Mean
    run_fl_test(server_url, "Test_TrimmedMean", "trimmed_mean", enable_trust=False)
    
    # Test 4: Trust-Weighted
    run_fl_test(server_url, "Test_TrustWeighted", "trust_weighted", enable_trust=True)
    
    # Test 5: Malicious Detection
    test_malicious_detection(server_url)
    
    print(f"\n{'='*70}")
    print("ALL TESTS COMPLETED")
    print('='*70)


if __name__ == "__main__":
    main()
