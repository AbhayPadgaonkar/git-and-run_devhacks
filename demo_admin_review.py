"""
Demo: Admin Review & Feedback System

This demo showcases the admin review feature where:
1. Admin creates experiment with review enabled
2. Clients submit updates
3. Admin reviews updates (approve/reject/request improvement)
4. Clients fetch feedback
5. System demonstrates auto-approval/rejection based on trust scores
"""
import requests
import time
import numpy as np
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

BASE_URL = "http://localhost:8000"

class Admin:
    def __init__(self, admin_id: str):
        self.admin_id = admin_id
        self.experiments = {}
        
    def log(self, message: str):
        print(f"{Fore.CYAN}[ADMIN {self.admin_id}] {message}{Style.RESET_ALL}")
    
    def create_experiment(
        self, 
        name: str, 
        require_admin_review: bool = True,
        auto_approve_trusted: bool = True,
        auto_reject_low_trust: bool = True
    ) -> str:
        """Create a federated learning experiment"""
        # Create simple initial weights
        initial_weights = {
            "layer1": np.random.randn(10, 5).tolist(),
            "layer2": np.random.randn(5, 2).tolist()
        }
        
        response = requests.post(
            f"{BASE_URL}/experiment/create",  # Fixed endpoint path
            json={
                "name": name,
                "aggregation_method": "fedavg",
                "enable_trust": True,
                "enable_clustering": False,
                "initial_weights": self._serialize_weights(initial_weights),
                "require_admin_review": require_admin_review,
                "auto_approve_trusted": auto_approve_trusted,
                "auto_approve_threshold": 0.8,
                "auto_reject_low_trust": auto_reject_low_trust,
                "auto_reject_threshold": 0.3,
                "max_staleness": 5
            }
        )
        
        data = response.json()
        exp_id = data["experiment_id"]
        self.experiments[exp_id] = data
        
        self.log(f"✅ Created experiment '{name}' (ID: {exp_id})")
        self.log(f"   Review settings:")
        self.log(f"   - Require admin review: {require_admin_review}")
        self.log(f"   - Auto-approve trusted: {auto_approve_trusted}")
        self.log(f"   - Auto-reject low trust: {auto_reject_low_trust}")
        
        return exp_id
    
    def get_pending_reviews(self, exp_id: str):
        """Get all pending reviews for an experiment"""
        response = requests.get(f"{BASE_URL}/experiment/{exp_id}/pending-reviews")
        pending = response.json()
        
        self.log(f"📋 {len(pending)} updates pending review")
        
        for p in pending:
            self.log(f"   - {p['update_id']} from {p['client_id']}")
            self.log(f"     Trust: {p['trust_score']:.2f}, Staleness: {p['staleness']}")
        
        return pending
    
    def review_update(
        self, 
        exp_id: str, 
        update_id: str, 
        status: str,
        feedback: str,
        suggestions: list = None
    ):
        """Review a client update"""
        response = requests.post(
            f"{BASE_URL}/experiment/{exp_id}/update/{update_id}/review",
            json={
                "status": status,
                "feedback": feedback,
                "admin_id": self.admin_id,
                "suggestions": suggestions or []
            }
        )
        
        # Check for errors
        if response.status_code != 200:
            self.log(f"❌ Error reviewing update: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        
        status_emoji = {
            "approved": "✅",
            "rejected": "❌",
            "needs_improvement": "🔄"
        }.get(status, "📝")
        
        self.log(f"{status_emoji} Reviewed {update_id}: {status.upper()}")
        self.log(f"   Feedback: {feedback}")
        if suggestions:
            self.log(f"   Suggestions: {', '.join(suggestions)}")
        if result.get("will_aggregate"):
            self.log(f"   ⚡ Update aggregated into global model")
        
        return result
    
    def _serialize_weights(self, weights):
        """Serialize weights to base64 string"""
        import base64
        import pickle
        return base64.b64encode(pickle.dumps(weights)).decode()


class Client:
    def __init__(self, client_id: str, color: str):
        self.client_id = client_id
        self.color = color
        self.current_weights = None
        self.current_version = 0
        self.update_history = []
        
    def log(self, message: str):
        print(f"{self.color}[CLIENT {self.client_id}] {message}{Style.RESET_ALL}")
    
    def fetch_global_model(self, exp_id: str, cluster_id: str = "cluster_0"):
        """Fetch current global model"""
        response = requests.get(
            f"{BASE_URL}/experiment/{exp_id}/global-model",
            params={"cluster_id": cluster_id}
        )
        
        data = response.json()
        self.current_weights = self._deserialize_weights(data["weights"])
        self.current_version = data["version"]
        
        self.log(f"📥 Fetched global model v{self.current_version}")
        return self.current_weights
    
    def train_local_model(self, num_samples: int = 100):
        """Simulate local training"""
        self.log(f"🔧 Training on {num_samples} local samples...")
        time.sleep(0.3)  # Simulate training
        
        # Generate random delta
        delta = {
            "layer1": (np.random.randn(10, 5) * 0.01).tolist(),
            "layer2": (np.random.randn(5, 2) * 0.01).tolist()
        }
        
        self.log(f"✅ Training complete")
        return delta
    
    def submit_update(self, exp_id: str, delta_weights):
        """Submit update to server"""
        response = requests.post(
            f"{BASE_URL}/experiment/{exp_id}/submit-update",
            json={
                "client_id": self.client_id,
                "delta_weights": self._serialize_weights(delta_weights),
                "model_version": self.current_version
            }
        )
        
        result = response.json()
        self.update_history.append(result)
        
        status_icon = "✅" if result.get("accepted") else "❌"
        self.log(f"{status_icon} Update submitted: {result['update_id']}")
        self.log(f"   Status: {result.get('message', result.get('status'))}")
        self.log(f"   Trust Score: {result['trust_score']:.2f}")
        
        if result.get("review_status"):
            self.log(f"   Review Status: {result['review_status']}")
        
        return result
    
    def get_feedback(self, exp_id: str):
        """Get all feedback from admin"""
        response = requests.get(
            f"{BASE_URL}/experiment/{exp_id}/client/{self.client_id}/feedback"
        )
        
        feedback_items = response.json()
        
        if not feedback_items:
            self.log(f"📫 No feedback available yet")
            return []
        
        self.log(f"📬 Received {len(feedback_items)} feedback items:")
        
        for item in feedback_items:
            status_emoji = {
                "approved": "✅",
                "auto_approved": "✅",
                "rejected": "❌",
                "needs_improvement": "🔄",
                "pending_review": "⏳"
            }.get(item["review_status"], "📝")
            
            self.log(f"   {status_emoji} {item['update_id']}: {item['review_status'].upper()}")
            if item.get("feedback"):
                self.log(f"      Feedback: {item['feedback']}")
            if item.get("suggestions"):
                self.log(f"      Suggestions: {', '.join(item['suggestions'])}")
            if item.get("aggregated"):
                self.log(f"      ⚡ Aggregated into global model")
        
        return feedback_items
    
    def _serialize_weights(self, weights):
        import base64
        import pickle
        return base64.b64encode(pickle.dumps(weights)).decode()
    
    def _deserialize_weights(self, weights_str):
        import base64
        import pickle
        return pickle.loads(base64.b64decode(weights_str))


def print_section(title: str):
    """Print a section divider"""
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{Style.RESET_ALL}\n")


def main():
    print(f"{Fore.MAGENTA}")
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║                      FederX Admin Review Demo                          ║")
    print("║            Quality Control & Feedback System for Federated Learning    ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)
    
    # Initialize participants
    admin = Admin("admin_alice")
    client1 = Client("client_bob", Fore.GREEN)
    client2 = Client("client_charlie", Fore.BLUE)
    client3 = Client("client_mallory", Fore.RED)  # Low trust client
    
    # ============================================================
    # SCENARIO 1: Manual Review Workflow
    # ============================================================
    print_section("SCENARIO 1: Manual Admin Review Workflow")
    
    admin.log("Creating experiment with MANUAL REVIEW for all updates")
    exp_id = admin.create_experiment(
        name="Manual Review Demo",
        require_admin_review=True,
        auto_approve_trusted=False,  # Disable auto-approval
        auto_reject_low_trust=False   # Disable auto-rejection
    )
    
    time.sleep(0.5)
    
    # Client 1 submits update
    client1.log("Starting Round 1...")
    client1.fetch_global_model(exp_id)
    delta1 = client1.train_local_model(200)
    client1.submit_update(exp_id, delta1)
    
    time.sleep(0.5)
    
    # Client 2 submits update
    client2.log("Starting Round 1...")
    client2.fetch_global_model(exp_id)
    delta2 = client2.train_local_model(150)
    client2.submit_update(exp_id, delta2)
    
    time.sleep(0.5)
    
    # Admin reviews pending updates
    admin.log("Checking pending reviews...")
    pending = admin.get_pending_reviews(exp_id)
    
    time.sleep(0.5)
    
    # Approve client 1
    if len(pending) >= 1:
        admin.review_update(
            exp_id,
            pending[0]["update_id"],
            "approved",
            "Excellent update! High quality gradients with good convergence.",
            suggestions=[]
        )
    
    time.sleep(0.3)
    
    # Request improvement from client 2
    if len(pending) >= 2:
        admin.review_update(
            exp_id,
            pending[1]["update_id"],
            "needs_improvement",
            "Update shows signs of overfitting. Please regularize your model.",
            suggestions=[
                "Add L2 regularization",
                "Reduce learning rate",
                "Use dropout layers"
            ]
        )
    
    time.sleep(0.5)
    
    # Clients fetch feedback
    client1.get_feedback(exp_id)
    time.sleep(0.3)
    client2.get_feedback(exp_id)
    
    # ============================================================
    # SCENARIO 2: Auto-Approval & Auto-Rejection
    # ============================================================
    print_section("SCENARIO 2: Auto-Approval & Auto-Rejection Based on Trust")
    
    admin.log("Creating experiment with AUTO-APPROVAL/REJECTION enabled")
    exp_id2 = admin.create_experiment(
        name="Auto Review Demo",
        require_admin_review=False,  # Manual review not required
        auto_approve_trusted=True,   # Auto-approve trusted clients (>= 0.8)
        auto_reject_low_trust=True   # Auto-reject low trust clients (< 0.3)
    )
    
    time.sleep(0.5)
    
    # Simulate building trust for client 1 (high trust)
    client1.log("Building trust with good updates...")
    for round_num in range(1, 4):
        client1.log(f"Round {round_num}...")
        client1.fetch_global_model(exp_id2)
        delta = client1.train_local_model(200)
        result = client1.submit_update(exp_id2, delta)
        time.sleep(0.3)
    
    time.sleep(0.5)
    
    # Client 3 simulates malicious behavior (low trust)
    client3.log("Attempting to submit update (simulated malicious client)...")
    client3.fetch_global_model(exp_id2)
    
    # Generate malicious delta (large magnitudes)
    malicious_delta = {
        "layer1": (np.random.randn(10, 5) * 100).tolist(),  # Very large
        "layer2": (np.random.randn(5, 2) * 100).tolist()
    }
    
    client3.submit_update(exp_id2, malicious_delta)
    time.sleep(0.5)
    
    # Check feedback
    client1.get_feedback(exp_id2)
    time.sleep(0.3)
    client3.get_feedback(exp_id2)
    
    # ============================================================
    # SCENARIO 3: Mixed Review Workflow
    # ============================================================
    print_section("SCENARIO 3: Mixed - Auto + Manual Review")
    
    admin.log("Creating experiment with MIXED review mode")
    exp_id3 = admin.create_experiment(
        name="Mixed Review Demo",
        require_admin_review=True,   # Manual review required for medium-trust
        auto_approve_trusted=True,   # But auto-approve high trust
        auto_reject_low_trust=True   # And auto-reject low trust
    )
    
    time.sleep(0.5)
    
    # Build trust for client 1 first
    client1.log("Building trust (3 good updates)...")
    for i in range(3):
        client1.fetch_global_model(exp_id3)
        delta = client1.train_local_model(200)
        client1.submit_update(exp_id3, delta)
        time.sleep(0.2)
    
    time.sleep(0.5)
    
    # Now client 1 should be auto-approved
    client1.log("Submitting update as trusted client...")
    client1.fetch_global_model(exp_id3)
    delta = client1.train_local_model(200)
    result = client1.submit_update(exp_id3, delta)
    
    time.sleep(0.3)
    
    # Client 2 (medium trust) requires manual review
    client2.log("Submitting update as medium-trust client...")
    client2.fetch_global_model(exp_id3)
    delta = client2.train_local_model(150)
    result = client2.submit_update(exp_id3, delta)
    
    time.sleep(0.5)
    
    # Admin reviews pending
    admin.log("Reviewing pending updates...")
    pending = admin.get_pending_reviews(exp_id3)
    
    if len(pending) > 0:
        time.sleep(0.3)
        admin.review_update(
            exp_id3,
            pending[0]["update_id"],
            "approved",
            "Good update from medium-trust client. Approved for aggregation."
        )
    
    time.sleep(0.5)
    
    # Summary
    print_section("Summary")
    
    admin.log("Review system demo complete! ✅")
    print(f"\n{Fore.WHITE}Key Features Demonstrated:{Style.RESET_ALL}")
    print(f"  ✅ Manual admin review with approve/reject/needs_improvement")
    print(f"  ✅ Detailed feedback and improvement suggestions")
    print(f"  ✅ Auto-approval for high-trust clients (>= 0.8)")
    print(f"  ✅ Auto-rejection for low-trust clients (< 0.3)")
    print(f"  ✅ Client feedback retrieval API")
    print(f"  ✅ Pending review queue for admins")
    print(f"  ✅ Mixed review mode (auto + manual)\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}❌ Error: Could not connect to server at {BASE_URL}")
        print(f"Please start the server first with: python -m backend.server{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
        raise
