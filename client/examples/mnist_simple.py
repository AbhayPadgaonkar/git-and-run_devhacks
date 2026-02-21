"""
Simple MNIST Federated Learning Example  
Demonstrates basic FL pipeline with multiple clients
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from client.federx_client.client import FederatedClient
from client.federx_client.adapters.pytorch import PyTorchAdapter


# Simple CNN for MNIST
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = torch.relu(x)
        x = self.conv2(x)
        x = torch.relu(x)
        x = torch.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = torch.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)


def train_local(model, device, train_loader, optimizer, epochs=1):
    """Train model locally for a few epochs"""
    model.train()
    for epoch in range(epochs):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = nn.functional.nll_loss(output, target)
            loss.backward()
            optimizer.step()


def test_model(model, device, test_loader):
    """Test model accuracy"""
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += nn.functional.nll_loss(output, target, reduction='sum').item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    return test_loss, accuracy


def get_client_data(full_dataset, client_id, num_clients, iid=True):
    """Split dataset for client"""
    total_size = len(full_dataset)
    samples_per_client = total_size // num_clients
    
    if iid:
        # IID split - random contiguous chunk
        start_idx = client_id * samples_per_client
        end_idx = start_idx + samples_per_client
        indices = list(range(start_idx, end_idx))
    else:
        # Non-IID split - each client gets only 2 digits
        # Client 0 gets digits 0,1  Client 1 gets 2,3 etc.
        digit1 = (client_id * 2) % 10
        digit2 = (client_id * 2 + 1) % 10
        
        indices = []
        for idx, (_, label) in enumerate(full_dataset):
            if label in [digit1, digit2]:
                indices.append(idx)
        
        # Limit to samples_per_client
        if len(indices) > samples_per_client:
            indices = indices[:samples_per_client]
    
    return Subset(full_dataset, indices)


def run_federated_learning(
    server_url="http://localhost:8000",
    experiment_id="exp_0",
    num_clients=5,
    num_rounds=10,
    local_epochs=1,
    iid=True
):
    """Run federated learning experiment"""
    print("\n" + "="*70)
    print(f"FEDERATED LEARNING - {'IID' if iid else 'Non-IID'} MNIST")
    print("="*70)
    print(f"Clients: {num_clients} | Rounds: {num_rounds} | Local Epochs: {local_epochs}")
    print("="*70 + "\n")
    
    device = torch.device("cpu")
    
    # Load MNIST data
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    print("Loading MNIST dataset...")
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    # Create clients
    clients = []
    for i in range(num_clients):
        client_data = get_client_data(train_dataset, i, num_clients, iid=iid)
        clients.append({
            "id": f"client_{i}",
            "data": client_data,
            "model": SimpleCNN().to(device)
        })
    
    print(f"Created {num_clients} clients with {len(clients[0]['data'])} samples each\n")
    
    # Initialize global model with shared random weights
    print("Initializing global model with shared weights...")
    torch.manual_seed(42)  # Fixed seed for reproducibility
    init_model = SimpleCNN().to(device)
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(init_model)
    
    # Upload initial weights to server by submitting as first "update"
    import requests
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from federx_client.utils.serialization import serialize_weights
    
    init_response = requests.post(
        f"{server_url}/experiment/{experiment_id}/submit-update",
        json={
            "client_id": "init_server",
            "delta_weights": serialize_weights(init_weights),  # Use full weights as "delta" for initialization
            "model_version": 0
        }
    )
    # Trigger aggregation to set global model
    requests.post(f"{server_url}/experiment/{experiment_id}/aggregate", params={"cluster_id": "cluster_0"})
    print("✓ Global model initialized\n")
    
    # Federated learning rounds
    for round_num in range(num_rounds):
        print(f"\n{'='*70}")
        print(f"ROUND {round_num + 1}/{num_rounds}")
        print(f"{'='*70}")
        
        # Each client trains locally and submits update
        for client in clients:
            print(f"\n[{client['id']}] Training locally...")
            
            # Create federated client
            fed_client = FederatedClient(
                server_url=server_url,
                experiment_id=experiment_id,
                client_id=client['id']
            )
            
            # Get global model
            try:
                global_weights = fed_client.fetch_global_model()
                if global_weights:
                    adapter = PyTorchAdapter()
                    adapter.set_weights(client['model'], global_weights)
                    print(f"  ✓ Loaded global model")
            except Exception as e:
                if round_num == 0:
                    print(f"  ⚠ No global model yet (first round)")
                else:
                    print(f"  ✗ Error fetching global model: {e}")
            
            # Save weights before training
            adapter = PyTorchAdapter()
            old_weights = adapter.get_weights(client['model'])
            
            # Train locally
            train_loader = DataLoader(client['data'], batch_size=32, shuffle=True)
            optimizer = optim.Adam(client['model'].parameters(), lr=0.001)
            train_local(client['model'], device, train_loader, optimizer, epochs=local_epochs)
            
            # Compute delta
            new_weights = adapter.get_weights(client['model'])
            delta = {k: new_weights[k] - old_weights[k] for k in new_weights.keys()}
            
            # Submit update
            response = fed_client.submit_update(delta)
            
            if response.get('accepted'):
                print(f"  ✓ Update accepted (trust: {response.get('trust_score', 'N/A'):.2f})")
            else:
                print(f"  ✗ Update rejected: {response.get('message', 'unknown')}")
        
        # Trigger aggregation
        print(f"\n{'─'*70}")
        print("Aggregating updates on server...")
        
        import requests
        agg_response = requests.post(
            f"{server_url}/experiment/{experiment_id}/aggregate",
            params={"cluster_id": "cluster_0"}
        )
        
        if agg_response.status_code == 200:
            agg_data = agg_response.json()
            print(f"✓ Aggregated {agg_data.get('aggregated_updates', 0)} updates")
            print(f"  New version: {agg_data.get('new_version', 'N/A')}")
        else:
            print(f"✗ Aggregation failed: {agg_response.status_code}")
        
        # Test global model
        print(f"\n{'─'*70}")
        print("Testing global model...")
        
        # Fetch latest global model
        fed_client = FederatedClient(server_url, experiment_id, "test_client")
        try:
            global_weights = fed_client.fetch_global_model()
            if global_weights:
                test_model_instance = SimpleCNN().to(device)
                adapter = PyTorchAdapter()
                adapter.set_weights(test_model_instance, global_weights)
                
                test_loss, accuracy = test_model(test_model_instance, device, test_loader)
                print(f"✓ Global Model Performance:")
                print(f"  Loss: {test_loss:.4f} | Accuracy: {accuracy:.2f}%")
        except Exception as e:
            print(f"✗ Error testing global model: {e}")
    
    print(f"\n{'='*70}")
    print("FEDERATED LEARNING COMPLETE!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MNIST Federated Learning')
    parser.add_argument('--experiment-id', type=str, default='exp_0', help='Experiment ID')
    parser.add_argument('--clients', type=int, default=5, help='Number of clients')
    parser.add_argument('--rounds', type=int, default=10, help='Number of FL rounds')
    parser.add_argument('--epochs', type=int, default=1, help='Local training epochs')
    parser.add_argument('--non-iid', action='store_true', help='Use non-IID data split')
    parser.add_argument('--server', type=str, default='http://localhost:8000', help='Server URL')
    
    args = parser.parse_args()
    
    run_federated_learning(
        server_url=args.server,
        experiment_id=args.experiment_id,
        num_clients=args.clients,
        num_rounds=args.rounds,
        local_epochs=args.epochs,
        iid=not args.non_iid
    )
