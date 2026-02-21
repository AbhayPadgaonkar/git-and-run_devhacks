"""
Test federated learning withCIFAR-10 dataset
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


class CIFAR10CNN(nn.Module):
    """CNN for CIFAR-10 (32x32 RGB images, 10 classes)"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 10)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = torch.flatten(x, 1)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)


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
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += torch.nn.functional.nll_loss(output, target, reduction='sum').item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    
    test_loss /= len(test_loader.dataset)
    accuracy = 100.0 * correct / len(test_loader.dataset)
    return test_loss, accuracy


def main():
    server_url = "http://localhost:8000"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("="*70)
    print("FEDERATED LEARNING - CIFAR-10 TEST")
    print("="*70)
    
    # Load CIFAR-10
    print("\n1. Loading CIFAR-10 dataset...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    train_dataset = datasets.CIFAR10('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.CIFAR10('./data', train=False, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    # Create IID client data splits
    num_clients = 3
    samples_per_client = len(train_dataset) // num_clients
    client_datasets = []
    for i in range(num_clients):
        start = i * samples_per_client
        end = start + samples_per_client if i < num_clients - 1 else len(train_dataset)
        indices = list(range(start, end))
        client_datasets.append(Subset(train_dataset, indices))
    
    print(f"Created {num_clients} clients with ~{samples_per_client} samples each")
    
    # Initialize shared model
    print("\n2. Initializing global model...")
    torch.manual_seed(42)
    init_model = CIFAR10CNN().to(device)
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(init_model)
    
    # Create experiment
    print("\n3. Creating experiment...")
    response = requests.post(
        f"{server_url}/experiment/create",
        json={
            "name": "CIFAR10_FL_Test",
            "aggregation_method": "fedavg",
            "enable_trust": True,
            "enable_clustering": False,
            "initial_weights": serialize_weights(init_weights)
        }
    )
    
    if response.status_code != 200:
        print(f"Failed to create experiment: {response.text}")
        return
    
    experiment_id = response.json()["experiment_id"]
    print(f"Created experiment: {experiment_id}")
    
    # Test initial model
    print("\n4. Testing initial model...")
    init_test_model = CIFAR10CNN().to(device)
    adapter.set_weights(init_test_model, init_weights)
    loss, acc = test_model(init_test_model, device, test_loader)
    print(f"   Initial model - Loss: {loss:.4f}, Accuracy: {acc:.2f}%")
    
    # Federated learning
    num_rounds = 3
    local_epochs = 2
    
    for round_num in range(num_rounds):
        print(f"\n{'='*70}")
        print(f"ROUND {round_num + 1}/{num_rounds}")
        print('='*70)
        
        for client_id in range(num_clients):
            print(f"\n[Client {client_id}] Training...")
            
            fed_client = FederatedClient(
                server_url=server_url,
                experiment_id=experiment_id,
                client_id=f"client_{client_id}"
            )
            
            global_weights = fed_client.fetch_global_model()
            local_model = CIFAR10CNN().to(device)
            adapter.set_weights(local_model, global_weights)
            old_weights = adapter.get_weights(local_model)
            
            # Train locally
            train_loader = DataLoader(client_datasets[client_id], batch_size=64, shuffle=True)
            optimizer = optim.Adam(local_model.parameters(), lr=0.001)
            
            for epoch in range(local_epochs):
                train_epoch(local_model, device, train_loader, optimizer)
            
            # Compute and submit delta
            new_weights = adapter.get_weights(local_model)
            delta = {k: new_weights[k] - old_weights[k] for k in new_weights.keys()}
            response = fed_client.submit_update(delta)
            
            if response.get('accepted'):
                print(f"   Update accepted (trust: {response['trust_score']:.2f})")
            else:
                print(f"   Update rejected: {response.get('message', 'unknown')}")
        
        # Aggregate
        print(f"\n{'-'*70}")
        print("Aggregating updates...")
        agg_response = requests.post(
            f"{server_url}/experiment/{experiment_id}/aggregate",
            params={"cluster_id": "cluster_0"}
        )
        
        if agg_response.status_code == 200:
            agg_data = agg_response.json()
            print(f"Aggregated {agg_data.get('aggregated_updates', 0)} updates (version {agg_data.get('new_version')})")
        
        # Test global model
        print(f"\n{'-'*70}")
        print("Testing global model...")
        global_weights = fed_client.fetch_global_model()
        global_model = CIFAR10CNN().to(device)
        adapter.set_weights(global_model, global_weights)
        loss, acc = test_model(global_model, device, test_loader)
        print(f"Global Model - Loss: {loss:.4f}, Accuracy: {acc:.2f}%")
    
    print(f"\n{'='*70}")
    print("FEDERATED LEARNING COMPLETE!")
    print('='*70)


if __name__ == "__main__":
    main()
