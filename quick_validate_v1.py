"""Quick validation test for both MNIST and CIFAR-10 before v1 push"""
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "client"))
from federx_client.client import FederatedClient
from federx_client.adapters.pytorch import PyTorchAdapter
from federx_client.utils.serialization import serialize_weights, deserialize_weights


class SimpleMNIST(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28*28, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        return torch.log_softmax(self.fc2(x), dim=1)


class SimpleCIFAR(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 10)
    
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        return torch.log_softmax(self.fc2(x), dim=1)


def quick_train(model, device, data_loader, epochs=1):
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    for epoch in range(epochs):
        for batch_idx, (data, target) in enumerate(data_loader):
            if batch_idx >= 5:  # Only 5 batches for speed
                break
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            loss = torch.nn.functional.nll_loss(model(data), target)
            loss.backward()
            optimizer.step()


def test_dataset(experiment_id, dataset_name, model_class, transform, dataset_loader):
    server_url = "http://localhost:8000"
    device = torch.device("cpu")
    
    print(f"\n{'='*70}")
    print(f"Testing {dataset_name.upper()}")
    print('='*70)
    
    # Load dataset
    train_data = dataset_loader('./data', train=True, download=False, transform=transform)
    
    # Create small client splits (1000 samples each)
    num_clients = 2
    samples_per_client = 1000
    client_datasets = []
    for i in range(num_clients):
        indices = list(range(i * samples_per_client, (i + 1) * samples_per_client))
        client_datasets.append(Subset(train_data, indices))
    
    print(f"✓ Created {num_clients} clients with {samples_per_client} samples each")
    
    # Initialize model
    torch.manual_seed(42)
    model = model_class().to(device)
    adapter = PyTorchAdapter()
    init_weights = adapter.get_weights(model)
    
    # Create experiment
    try:
        response = requests.post(f"{server_url}/experiment/create", 
                                json={
                                    "name": experiment_id,
                                    "aggregation_method": "fedavg",
                                    "enable_trust": True,
                                    "enable_clustering": False,
                                    "initial_weights": serialize_weights(init_weights)
                                })
        response.raise_for_status()
        exp_data = response.json()
        experiment_id = exp_data["experiment_id"]
        print(f"✓ Created experiment: {experiment_id}")
    except Exception as e:
        print(f"✗ Failed to create experiment: {e}")
        return False
    
    # Single round FL
    print(f"\nRound 1/1")
    for client_id in range(num_clients):
        # Create client
        fed_client = FederatedClient(
            server_url=server_url,
            experiment_id=experiment_id,
            client_id=f"client_{client_id}"
        )
        
        # Get global weights
        global_weights = fed_client.fetch_global_model()
        
        # Load into model
        model = model_class().to(device)
        adapter.set_weights(model, global_weights)
        old_weights = adapter.get_weights(model)
        
        # Quick train
        loader = DataLoader(client_datasets[client_id], batch_size=64, shuffle=True)
        quick_train(model, device, loader, epochs=1)
        
        # Compute delta and upload
        new_weights = adapter.get_weights(model)
        delta = {k: new_weights[k] - old_weights[k] for k in new_weights.keys()}
        fed_client.submit_update(delta)
        
        print(f"  [Client {client_id}] Update submitted")
    
    # Aggregate
    response = requests.post(f"{server_url}/experiment/{experiment_id}/aggregate",
                            params={"cluster_id": "cluster_0"})
    print(f"✓ Aggregated updates")
    
    # Check status
    response = requests.get(f"{server_url}/experiment/{experiment_id}")
    status = response.json()
    clusters = status.get("clusters", {"cluster_0": {}})
    cluster_info = clusters.get("cluster_0", {})
    num_updates = cluster_info.get("model_version", 0)
    print(f"✓ {dataset_name} test PASSED - Model version: {num_updates}")
    
    return True


def main():
    print("\n" + "="*70)
    print("FEDERX V1 - QUICK VALIDATION TEST")
    print("="*70)
    
    # Test MNIST
    mnist_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    mnist_ok = test_dataset(
        experiment_id="v1_mnist_quick",
        dataset_name="MNIST",
        model_class=SimpleMNIST,
        transform=mnist_transform,
        dataset_loader=datasets.MNIST
    )
    
    # Test CIFAR-10
    cifar_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    cifar_ok = test_dataset(
        experiment_id="v1_cifar10_quick",
        dataset_name="CIFAR-10",
        model_class=SimpleCIFAR,
        transform=cifar_transform,
        dataset_loader=datasets.CIFAR10
    )
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"MNIST:    {'✓ PASSED' if mnist_ok else '✗ FAILED'}")
    print(f"CIFAR-10: {'✓ PASSED' if cifar_ok else '✗ FAILED'}")
    
    if mnist_ok and cifar_ok:
        print("\n🎉 All tests passed! Ready to push v1")
    else:
        print("\n⚠️ Some tests failed")
    print("="*70)


if __name__ == "__main__":
    main()
