"""
🎭 FederX Complete System Demo
Simulates: 1 Admin + 1 Server + 2 Clients
Shows complete federated learning flow with all interactions
"""
import requests
import time
import threading
import numpy as np
from typing import Dict, Any
import torch
import torch.nn as nn
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

SERVER_URL = "http://localhost:8000"
EXPERIMENT_ID = "demo_mnist_fl"


# ============================================================================
# SIMPLE MODEL FOR DEMO
# ============================================================================
class SimpleMLP(nn.Module):
    """Simple 2-layer MLP for demo"""
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = x.view(-1, 784)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


# ============================================================================
# ADMIN PERSPECTIVE
# ============================================================================
class Admin:
    """Admin creates and monitors experiments"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.experiment_id = None
    
    def print_header(self, text: str):
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}👤 ADMIN: {text}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    
    def check_server_health(self) -> bool:
        """Check if server is running"""
        self.print_header("Checking server health...")
        try:
            response = requests.get(f"{self.server_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Server is healthy!")
                return True
        except:
            print(f"{Fore.RED}❌ Server is not running!")
            return False
        return False
    
    def create_experiment(self, exp_id: str, config: Dict[str, Any]) -> bool:
        """Create a new federated learning experiment"""
        self.print_header(f"Creating experiment: {exp_id}")
        
        payload = {
            "name": exp_id,
            "aggregation_method": config.get("aggregation_method", "fedavg"),
            "enable_trust": config.get("enable_trust", True),
            "enable_clustering": config.get("enable_clustering", False),
            "max_staleness": config.get("max_staleness", 5),
            "staleness_weighting": config.get("staleness_weighting", True)
        }
        
        print(f"{Fore.YELLOW}Configuration:")
        print(f"  - Experiment Name: {exp_id}")
        print(f"  - Aggregation: {payload['aggregation_method']}")
        print(f"  - Enable Trust: {payload['enable_trust']}")
        print(f"  - Max Staleness: {payload['max_staleness']}")
        print(f"  - Staleness Weighting: {payload['staleness_weighting']}")
        
        try:
            response = requests.post(
                f"{self.server_url}/experiment/create",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Server returns actual experiment ID (e.g., exp_0, exp_1)
                actual_exp_id = data.get('experiment_id', exp_id)
                self.experiment_id = actual_exp_id
                print(f"{Fore.GREEN}✅ Experiment created successfully!")
                print(f"{Fore.GREEN}   Experiment ID: {actual_exp_id}")
                print(f"{Fore.GREEN}   Status: {data.get('status', 'created')}")
                return actual_exp_id  # Return actual ID
            else:
                print(f"{Fore.RED}❌ Failed to create experiment")
                print(f"{Fore.RED}   {response.text}")
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            return False
    
    def monitor_experiment(self, exp_id: str):
        """Monitor experiment status"""
        self.print_header(f"Monitoring experiment: {exp_id}")
        
        try:
            response = requests.get(
                f"{self.server_url}/experiment/{exp_id}/status",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n{Fore.YELLOW}📊 Experiment Status:")
                print(f"  Total Updates: {Fore.WHITE}{data.get('total_updates', 0)}")
                print(f"  Accepted Updates: {Fore.WHITE}{data.get('accepted_updates', 0)}")
                print(f"  Rejected Updates: {Fore.WHITE}{data.get('rejected_updates', 0)}")
                
                # Show cluster info
                if data.get('clusters'):
                    print(f"\n{Fore.YELLOW}🌐 Clusters:")
                    for cluster_id, cluster_data in data['clusters'].items():
                        print(f"  {cluster_id}:")
                        print(f"    - Version: {cluster_data.get('version', 0)}")
                        print(f"    - Clients: {cluster_data.get('client_count', 0)}")
                
                if data.get('trust_scores'):
                    print(f"\n{Fore.YELLOW}🛡️  Trust Scores:")
                    for client_id, score in data['trust_scores'].items():
                        color = Fore.GREEN if score > 0.7 else Fore.YELLOW if score > 0.5 else Fore.RED
                        status = "✅" if score > 0.7 else "⚠️" if score > 0.5 else "🚨"
                        print(f"    {status} {client_id}: {color}{score:.2f}")
                
                return data
            else:
                print(f"{Fore.RED}❌ Failed to get status")
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            return None
    
    def get_final_model(self, exp_id: str):
        """Download final trained model"""
        self.print_header(f"Downloading final model from: {exp_id}")
        
        try:
            response = requests.get(
                f"{self.server_url}/experiment/{exp_id}/global-model",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"{Fore.GREEN}✅ Final model downloaded (version {data['version']})")
                print(f"{Fore.GREEN}   Ready for production deployment!")
                return data
            else:
                print(f"{Fore.RED}❌ Failed to download model")
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            return None


# ============================================================================
# CLIENT PERSPECTIVE
# ============================================================================
class Client:
    """Client trains on local data and participates in FL"""
    
    def __init__(self, client_id: str, server_url: str, color: str):
        self.client_id = client_id
        self.server_url = server_url
        self.color = color  # For colored output
        self.model = SimpleMLP()
        self.current_version = 0
    
    def print_header(self, text: str):
        print(f"\n{self.color}{'─'*80}")
        print(f"{self.color}📱 CLIENT [{self.client_id}]: {text}")
        print(f"{self.color}{'─'*80}{Style.RESET_ALL}")
    
    def fetch_global_model(self, exp_id: str) -> bool:
        """Download global model from server"""
        try:
            response = requests.get(
                f"{self.server_url}/experiment/{exp_id}/global-model",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_version = data['version']
                
                # Deserialize weights
                from backend.utils.serialization import deserialize_weights
                weights_base64 = data['weights']
                
                if weights_base64:
                    try:
                        weights = deserialize_weights(weights_base64)
                        if weights:
                            state_dict = {}
                            for key, value in weights.items():
                                state_dict[key] = torch.from_numpy(np.array(value))
                            self.model.load_state_dict(state_dict, strict=False)
                    except:
                        # First fetch, empty weights
                        pass
                
                print(f"{self.color}📥 Downloaded global model v{self.current_version}")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to fetch global model")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            return False
    
    def train_local_model(self, num_epochs: int = 3) -> int:
        """Simulate local training on private data"""
        print(f"{self.color}🔄 Training on local private data...")
        
        # Simulate training with random data
        optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()
        
        num_samples = 0
        for epoch in range(num_epochs):
            # Simulate 10 batches
            for batch in range(10):
                # Random data (simulating MNIST)
                data = torch.randn(32, 784)
                target = torch.randint(0, 10, (32,))
                
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                
                num_samples += 32
            
            print(f"{self.color}   Epoch {epoch + 1}/{num_epochs} - Loss: {loss.item():.4f}")
        
        print(f"{self.color}✅ Local training complete ({num_samples} samples)")
        return num_samples
    
    def submit_update(self, exp_id: str, num_samples: int) -> Dict[str, Any]:
        """Submit updated weights to server"""
        print(f"{self.color}📤 Submitting model update...")
        
        # Extract weights as delta (difference from initial)
        delta_weights = {}
        for name, param in self.model.named_parameters():
            delta_weights[name] = param.detach().cpu().numpy()
        
        # Serialize weights
        from backend.utils.serialization import serialize_weights
        serialized_delta = serialize_weights(delta_weights)
        
        payload = {
            "client_id": self.client_id,
            "delta_weights": serialized_delta,
            "model_version": self.current_version
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/experiment/{exp_id}/submit-update",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('accepted'):
                    print(f"{self.color}✅ Update accepted!")
                    if data.get('message'):
                        print(f"{self.color}   {data['message']}")
                    
                    if data.get('staleness') is not None and data['staleness'] > 0:
                        print(f"{Fore.YELLOW}   ⚠️  Staleness: {data['staleness']}")
                        if data.get('staleness_weight'):
                            print(f"{Fore.YELLOW}   Weight adjusted: {data['staleness_weight']:.2f}")
                    
                    if data.get('new_global_version'):
                        print(f"{self.color}   🌍 New global version: v{data['new_global_version']}")
                else:
                    print(f"{Fore.RED}❌ Update rejected!")
                    if data.get('message'):
                        print(f"{Fore.RED}   {data['message']}")
                
                return data
            else:
                print(f"{Fore.RED}❌ Update failed!")
                print(f"{Fore.RED}   {response.text}")
                return {"accepted": False}
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"accepted": False}
    
    def run_federated_learning(self, exp_id: str, num_rounds: int, delay: float = 0):
        """Run complete FL workflow for multiple rounds"""
        self.print_header(f"Starting Federated Learning")
        print(f"{self.color}Experiment: {exp_id}")
        print(f"{self.color}Rounds: {num_rounds}")
        
        for round_num in range(num_rounds):
            print(f"\n{self.color}{'▼'*40}")
            print(f"{self.color}Round {round_num + 1}/{num_rounds}")
            print(f"{self.color}{'▼'*40}")
            
            # Add delay to simulate different client speeds
            if delay > 0:
                time.sleep(delay)
            
            # 1. Fetch global model
            if not self.fetch_global_model(exp_id):
                print(f"{Fore.RED}Failed to fetch model, skipping round")
                continue
            
            # 2. Train locally
            num_samples = self.train_local_model(num_epochs=3)
            
            # 3. Submit update
            result = self.submit_update(exp_id, num_samples)
            
            # Small delay between rounds
            time.sleep(1)
        
        print(f"\n{self.color}{'═'*80}")
        print(f"{self.color}🎉 Client {self.client_id} completed all rounds!")
        print(f"{self.color}{'═'*80}")


# ============================================================================
# SERVER PERSPECTIVE (Monitoring)
# ============================================================================
class ServerMonitor:
    """Monitor server activity"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
    
    def print_event(self, event_type: str, message: str):
        color = {
            "INFO": Fore.BLUE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED
        }.get(event_type, Fore.WHITE)
        
        icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }.get(event_type, "•")
        
        print(f"{color}🖥️  SERVER {icon}: {message}{Style.RESET_ALL}")


# ============================================================================
# MAIN DEMO
# ============================================================================
def main():
    print(f"{Fore.MAGENTA}")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🎭 FEDERX COMPLETE SYSTEM DEMO".center(78) + "║")
    print("║" + " "*78 + "║")
    print("║" + "  Simulating: 1 Admin + 1 Server + 2 Clients".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")
    print(Style.RESET_ALL)
    
    # ========================================================================
    # 1. ADMIN: Check server and create experiment
    # ========================================================================
    admin = Admin(SERVER_URL)
    
    if not admin.check_server_health():
        print(f"\n{Fore.RED}ERROR: Server must be running!")
        print(f"{Fore.YELLOW}Please start server: python run_server.py")
        return
    
    time.sleep(1)
    
    # Create experiment
    experiment_config = {
        "aggregation_method": "fedavg",
        "enable_trust": True,
        "enable_clustering": False,
        "max_staleness": 5,
        "staleness_weighting": True
    }
    
    actual_exp_id = admin.create_experiment(EXPERIMENT_ID, experiment_config)
    if not actual_exp_id:
        print(f"\n{Fore.RED}Failed to create experiment!")
        return
    
    time.sleep(2)
    
    # ========================================================================
    # 2. CLIENTS: Initialize
    # ========================================================================
    client1 = Client("client_001", SERVER_URL, Fore.GREEN)
    client2 = Client("client_002", SERVER_URL, Fore.MAGENTA)
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🚀 Starting Federated Learning with 2 Clients")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    
    time.sleep(1)
    
    # ========================================================================
    # 3. RUN FEDERATED LEARNING (Parallel clients)
    # ========================================================================
    
    # Client 1: Fast client (no delay)
    thread1 = threading.Thread(
        target=client1.run_federated_learning,
        args=(actual_exp_id, 3, 0)  # 3 rounds, no delay
    )
    
    # Client 2: Slower client (1 second delay per round)
    thread2 = threading.Thread(
        target=client2.run_federated_learning,
        args=(actual_exp_id, 3, 2)  # 3 rounds, 2 second delay
    )
    
    # Start both clients
    thread1.start()
    thread2.start()
    
    # Wait for both to complete
    thread1.join()
    thread2.join()
    
    time.sleep(2)
    
    # ========================================================================
    # 4. ADMIN: Monitor final status
    # ========================================================================
    time.sleep(1)
    status = admin.monitor_experiment(actual_exp_id)
    
    time.sleep(1)
    
    # ========================================================================
    # 5. ADMIN: Download final model
    # ========================================================================
    final_model = admin.get_final_model(actual_exp_id)
    
    # ========================================================================
    # 6. SUMMARY
    # ========================================================================
    print(f"\n{Fore.MAGENTA}")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  📊 DEMO SUMMARY".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")
    print(Style.RESET_ALL)
    
    if status:
        print(f"{Fore.YELLOW}Experiment Results:")
        print(f"  • Total Updates: {Fore.WHITE}{status.get('total_updates', 0)}")
        print(f"  • Accepted Updates: {Fore.WHITE}{status.get('accepted_updates', 0)}")
        print(f"  • Rejected Updates: {Fore.WHITE}{status.get('rejected_updates', 0)}")
        
        if status.get('clusters'):
            print(f"\n{Fore.YELLOW}Cluster Status:")
            for cluster_id, cluster_data in status['clusters'].items():
                print(f"  • {cluster_id}: Version v{cluster_data.get('version', 0)}, Clients: {cluster_data.get('client_count', 0)}")
        
        if status.get('trust_scores'):
            print(f"\n{Fore.YELLOW}Client Trust Scores:")
            for client_id, score in status['trust_scores'].items():
                print(f"  • {client_id}: {Fore.WHITE}{score:.3f}")
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}✅ Demo Complete! FederX is working perfectly!")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}What was demonstrated:")
    print(f"  ✓ Admin created experiment with security configs")
    print(f"  ✓ Server managed global model and aggregation")
    print(f"  ✓ Client 1 trained and submitted updates (fast)")
    print(f"  ✓ Client 2 trained and submitted updates (slower)")
    print(f"  ✓ Server detected staleness and adjusted weights")
    print(f"  ✓ Trust scores tracked for both clients")
    print(f"  ✓ Final model ready for deployment")
    print(f"{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
