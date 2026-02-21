"""Example: Federated learning on MNIST with IID data"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import sys
import time
sys.path.append('..')

from federx_client import FederatedClient, PyTorchAdapter


# Simple CNN for MNIST
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def train_local(model, train_loader, epochs=1, lr=0.01):
    """Train model locally for specified epochs"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.train()
    
    optimizer = optim.SGD(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        print(f"  Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")


def evaluate(model, test_loader):
    """Evaluate model accuracy"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)
    
    accuracy = 100 * correct / total
    return accuracy


def main():
    # Configuration
    SERVER_URL = "http://localhost:8000"
    EXPERIMENT_ID = "exp_0"  # Will be created from server
    CLIENT_ID = f"client_{torch.randint(0, 1000, (1,)).item()}"
    NUM_ROUNDS = 10
    LOCAL_EPOCHS = 2
    BATCH_SIZE = 32
    
    print(f"Starting Federated Learning Client: {CLIENT_ID}")
    print(f"Server: {SERVER_URL}")
    print(f"Experiment: {EXPERIMENT_ID}")
    print("-" * 50)
    
    # Load MNIST dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    
    # Create IID split (take subset of data)
    num_samples = len(train_dataset) // 10  # Simulate 10 clients
    start_idx = torch.randint(0, len(train_dataset) - num_samples, (1,)).item()
    indices = list(range(start_idx, start_idx + num_samples))
    train_subset = Subset(train_dataset, indices)
    
    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    # Initialize model and client
    model = SimpleCNN()
    fl_client = FederatedClient(
        server_url=SERVER_URL,
        experiment_id=EXPERIMENT_ID,
        client_id=CLIENT_ID,
        adapter=PyTorchAdapter()
    )
    
    # Training loop
    for round_num in range(NUM_ROUNDS):
        print(f"\n{'=' * 50}")
        print(f"Round {round_num + 1}/{NUM_ROUNDS}")
        print(f"{'=' * 50}")
        
        try:
            # Fetch global model
            print("Fetching global model...")
            global_weights = fl_client.fetch_global_model()
            
            if global_weights:
                fl_client.adapter.set_weights(model, global_weights)
                print(f"Loaded global model version {fl_client.current_version}")
            
            # Save old weights
            old_weights = fl_client.adapter.get_weights(model)
            
            # Train locally
            print(f"Training locally for {LOCAL_EPOCHS} epochs...")
            train_local(model, train_loader, epochs=LOCAL_EPOCHS)
            
            # Evaluate
            accuracy = evaluate(model, test_loader)
            print(f"Local accuracy: {accuracy:.2f}%")
            
            # Compute delta
            new_weights = fl_client.adapter.get_weights(model)
            delta_weights = {
                key: new_weights[key] - old_weights[key]
                for key in new_weights.keys()
            }
            
            # Submit update
            print("Submitting update to server...")
            response = fl_client.submit_update(delta_weights)
            
            print(f"Update {response['update_id']}: {response['status']}")
            print(f"Accepted: {response['accepted']}")
            print(f"Trust Score: {response['trust_score']:.3f}")
            print(f"Cluster: {response['cluster_id']}")
            
            time.sleep(1)  # Brief pause
            
        except Exception as e:
            print(f"Error in round {round_num + 1}: {str(e)}")
            break
    
    print("\n" + "=" * 50)
    print("Training completed!")
    final_accuracy = evaluate(model, test_loader)
    print(f"Final accuracy: {final_accuracy:.2f}%")
    print(f"Final trust score: {fl_client.get_trust_score():.3f}")


if __name__ == "__main__":
    main()
