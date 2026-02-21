"""
Tests for Admin Review & Feedback System
"""
import requests
import base64
import pickle
import numpy as np
from backend.models.review import ReviewStatus

BASE_URL = "http://localhost:8000"


def serialize_weights(weights):
    """Helper to serialize weights"""
    return base64.b64encode(pickle.dumps(weights)).decode()


def test_manual_review_workflow():
    """Test manual admin review workflow"""
    # Create experiment with manual review required
    initial_weights = {
        "layer1": np.random.randn(5, 3).tolist(),
        "layer2": np.random.randn(3, 2).tolist()
    }
    
    response = requests.post(
        f"{BASE_URL}/experiment/create",
        json={
            "name": "Manual Review Test",
            "require_admin_review": True,
            "auto_approve_trusted": False,
            "auto_reject_low_trust": False,
            "initial_weights": serialize_weights(initial_weights)
        }
    )
    
    assert response.status_code == 200
    exp_id = response.json()["experiment_id"]
    
    # Client submits update
    delta_weights = {
        "layer1": (np.random.randn(5, 3) * 0.01).tolist(),
        "layer2": (np.random.randn(3, 2) * 0.01).tolist()
    }
    
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/submit-update",
        json={
            "client_id": "test_client",
            "delta_weights": serialize_weights(delta_weights),
            "model_version": 0
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    update_id = result["update_id"]
    # ReviewStatus enum values are returned as strings
    assert result.get("review_status") in [ReviewStatus.PENDING_REVIEW, "pending_review"]
    
    # Check pending reviews
    response = requests.get(f"{BASE_URL}/experiment/{exp_id}/pending-reviews")
    assert response.status_code == 200
    pending = response.json()
    assert len(pending) == 1
    assert pending[0]["update_id"] == update_id
    
    # Admin approves update
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/update/{update_id}/review",
        json={
            "status": ReviewStatus.APPROVED,
            "feedback": "Great update!",
            "admin_id": "admin_test",
            "suggestions": []
        }
    )
    
    assert response.status_code == 200
    review_result = response.json()
    assert review_result["review_status"] == ReviewStatus.APPROVED
    assert review_result["will_aggregate"] is True
    
    # Client fetches feedback
    response = requests.get(f"{BASE_URL}/experiment/{exp_id}/client/test_client/feedback")
    assert response.status_code == 200
    feedback = response.json()
    assert len(feedback) == 1
    assert feedback[0]["review_status"] == ReviewStatus.APPROVED
    assert feedback[0]["aggregated"] is True
    
    print("✅ Manual review workflow test passed")


def test_auto_approval():
    """Test auto-approval for high trust clients"""
    initial_weights = {
        "layer1": np.random.randn(5, 3).tolist()
    }
    
    response = requests.post(
        f"{BASE_URL}/experiment/create",
        json={
            "name": "Auto-Approve Test",
            "require_admin_review": False,
            "auto_approve_trusted": True,
            "auto_approve_threshold": 0.8,
            "initial_weights": serialize_weights(initial_weights)
        }
    )
    
    assert response.status_code == 200
    exp_id = response.json()["experiment_id"]
    
    # Submit update (trust score should be 1.0 initially)
    delta_weights = {"layer1": (np.random.randn(5, 3) * 0.01).tolist()}
    
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/submit-update",
        json={
            "client_id": "trusted_client",
            "delta_weights": serialize_weights(delta_weights),
            "model_version": 0
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result.get("review_status") == ReviewStatus.AUTO_APPROVED
    assert result.get("new_global_version") == 1  # Should aggregate immediately
    
    print("✅ Auto-approval test passed")


def test_needs_improvement_workflow():
    """Test needs improvement workflow"""
    initial_weights = {"layer1": np.random.randn(5, 3).tolist()}
    
    response = requests.post(
        f"{BASE_URL}/experiment/create",
        json={
            "name": "Needs Improvement Test",
            "require_admin_review": True,
            "auto_approve_trusted": False,
            "initial_weights": serialize_weights(initial_weights)
        }
    )
    
    exp_id = response.json()["experiment_id"]
    
    # Submit update
    delta_weights = {"layer1": (np.random.randn(5, 3) * 0.01).tolist()}
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/submit-update",
        json={
            "client_id": "improvable_client",
            "delta_weights": serialize_weights(delta_weights),
            "model_version": 0
        }
    )
    
    update_id = response.json()["update_id"]
    
    # Admin requests improvement
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/update/{update_id}/review",
        json={
            "status": ReviewStatus.NEEDS_IMPROVEMENT,
            "feedback": "Please add regularization",
            "admin_id": "admin_test",
            "suggestions": ["Add L2 regularization", "Reduce learning rate"]
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["review_status"] == ReviewStatus.NEEDS_IMPROVEMENT
    assert result["will_aggregate"] is False
    
    # Check client feedback includes suggestions
    response = requests.get(f"{BASE_URL}/experiment/{exp_id}/client/improvable_client/feedback")
    feedback = response.json()[0]
    assert feedback["review_status"] == ReviewStatus.NEEDS_IMPROVEMENT
    assert len(feedback["suggestions"]) == 2
    assert feedback["aggregated"] is False
    
    print("✅ Needs improvement workflow test passed")


def test_rejection_workflow():
    """Test rejection workflow"""
    initial_weights = {"layer1": np.random.randn(5, 3).tolist()}
    
    response = requests.post(
        f"{BASE_URL}/experiment/create",
        json={
            "name": "Rejection Test",
            "require_admin_review": True,
            "auto_approve_trusted": False,
            "initial_weights": serialize_weights(initial_weights)
        }
    )
    
    exp_id = response.json()["experiment_id"]
    
    # Submit update
    delta_weights = {"layer1": (np.random.randn(5, 3) * 0.5).tolist()}
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/submit-update",
        json={
            "client_id": "rejected_client",
            "delta_weights": serialize_weights(delta_weights),
            "model_version": 0
        }
    )
    
    update_id = response.json()["update_id"]
    
    # Admin rejects update
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/update/{update_id}/review",
        json={
            "status": ReviewStatus.REJECTED,
            "feedback": "Update quality too low",
            "admin_id": "admin_test",
            "suggestions": []
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["review_status"] == ReviewStatus.REJECTED
    assert result["will_aggregate"] is False
    
    # Verify global model not updated
    response = requests.get(f"{BASE_URL}/experiment/{exp_id}/global-model?cluster_id=cluster_0")
    global_model = response.json()
    assert global_model["version"] == 0  # Should still be 0
    
    print("✅ Rejection workflow test passed")


def test_mixed_review_mode():
    """Test mixed review mode (auto + manual)"""
    initial_weights = {"layer1": np.random.randn(5, 3).tolist()}
    
    response = requests.post(
        f"{BASE_URL}/experiment/create",
        json={
            "name": "Mixed Review Test",
            "require_admin_review": True,  # Manual review required
            "auto_approve_trusted": True,  # But auto-approve trusted
            "auto_approve_threshold": 0.8,
            "initial_weights": serialize_weights(initial_weights)
        }
    )
    
    exp_id = response.json()["experiment_id"]
    
    # First update - should be auto-approved (trust = 1.0)
    delta = {"layer1": (np.random.randn(5, 3) * 0.01).tolist()}
    response = requests.post(
        f"{BASE_URL}/experiment/{exp_id}/submit-update",
        json={
            "client_id": "client1",
            "delta_weights": serialize_weights(delta),
            "model_version": 0
        }
    )
    
    result = response.json()
    assert result.get("review_status") == ReviewStatus.AUTO_APPROVED
    assert result.get("new_global_version") == 1
    
    print("✅ Mixed review mode test passed")


def test_pending_reviews_list():
    """Test getting list of pending reviews"""
    initial_weights = {"layer1": np.random.randn(5, 3).tolist()}
    
    response = requests.post(
        f"{BASE_URL}/experiment/create",
        json={
            "name": "Pending Reviews Test",
            "require_admin_review": True,
            "auto_approve_trusted": False,
            "auto_reject_low_trust": False,
            "initial_weights": serialize_weights(initial_weights)
        }
    )
    
    exp_id = response.json()["experiment_id"]
    
    # Submit 3 updates
    update_ids = []
    for i in range(3):
        delta = {"layer1": (np.random.randn(5, 3) * 0.01).tolist()}
        response = requests.post(
            f"{BASE_URL}/experiment/{exp_id}/submit-update",
            json={
                "client_id": f"client_{i}",
                "delta_weights": serialize_weights(delta),
                "model_version": 0
            }
        )
        update_ids.append(response.json()["update_id"])
    
    # Check pending reviews
    response = requests.get(f"{BASE_URL}/experiment/{exp_id}/pending-reviews")
    pending = response.json()
    
    assert len(pending) == 3
    pending_ids = [p["update_id"] for p in pending]
    assert set(pending_ids) == set(update_ids)
    
    # All should have metadata
    for p in pending:
        assert "client_id" in p
        assert "trust_score" in p
        assert "staleness" in p
    
    print("✅ Pending reviews list test passed")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("  FederX Admin Review & Feedback System Tests")
    print("="*80 + "\n")
    
    try:
        test_manual_review_workflow()
        test_auto_approval()
        test_needs_improvement_workflow()
        test_rejection_workflow()
        test_mixed_review_mode()
        test_pending_reviews_list()
        
        print("\n" + "="*80)
        print("  ✅ ALL TESTS PASSED (6/6)")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at " + BASE_URL)
        print("Please start the server first with: python -m backend.server.main\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        raise
