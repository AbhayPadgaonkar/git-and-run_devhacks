"""Example: Malicious client that sends corrupted updates"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import sys
import time
import numpy as np
sys.path.append('..')

from federx_client import FederatedClient, PyTorchAdapter


# Simple CNN for MNIST (same as normal client)
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


def main():
    # Configuration
    SERVER_URL = "http://localhost:8000"
    EXPERIMENT_ID = "exp_0"
    CLIENT_ID = "malicious_client_666"
    NUM_ROUNDS = 10
    ATTACK_MAGNITUDE = 10.0  # Multiply updates by this factor
    
    print(f"🔴 MALICIOUS CLIENT: {CLIENT_ID}")
    print(f"Attack magnitude: {ATTACK_MAGNITUDE}x")
    print("-" * 50)
    
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
            
            # Get current weights
            weights = fl_client.adapter.get_weights(model)
            
            # Create MALICIOUS update (random noise with high magnitude)
            print(f"Creating malicious update (magnitude: {ATTACK_MAGNITUDE}x)...")
            delta_weights = {}
            for key in weights.keys():
                # Random noise with high magnitude
                noise = np.random.randn(*weights[key].shape) * ATTACK_MAGNITUDE
                delta_weights[key] = noise.astype(weights[key].dtype)
            
            # Submit malicious update
            print("Submitting MALICIOUS update to server...")
            response = fl_client.submit_update(delta_weights)
            
            print(f"Update {response['update_id']}: {response['status']}")
            print(f"🎯 Accepted: {response['accepted']}")
            print(f"Trust Score: {response['trust_score']:.3f}")
            
            if not response['accepted']:
                print(f"✅ DETECTED AS MALICIOUS: {response.get('message', '')}")
            else:
                print(f"⚠️  ATTACK SUCCEEDED - Update accepted!")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            break
    
    print("\n" + "=" * 50)
    print(f"Final trust score: {fl_client.get_trust_score():.3f}")
    print("Malicious client finished")


if __name__ == "__main__":
    main()
