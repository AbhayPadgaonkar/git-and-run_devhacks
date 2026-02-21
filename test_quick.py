"""
Quick FederX v2.0 Validation Test
"""
import requests
import sys

SERVER_URL = "http://localhost:8000"

print("\n" + "="*60)
print("⚡ FEDERX v2.0 - QUICK VALIDATION")
print("="*60)

tests = []

# Test 1: Server Health
try:
    r = requests.get(f"{SERVER_URL}/health", timeout=2)
    tests.append(("Server Health", r.status_code == 200))
except:
    tests.append(("Server Health", False))
    print("\n❌ Server not running!")
    sys.exit(1)

# Test 2: Create Experiment
try:
    r = requests.post(f"{SERVER_URL}/experiment/create", json={
        "name": "Test",
        "aggregation_method": "fedavg",
        "max_staleness": 5,
        "staleness_weighting": True
    })
    exp_id = r.json()["experiment_id"]
    tests.append(("Create Experiment", "experiment_id" in r.json()))
    
    # Test 3: Get Status
    r = requests.get(f"{SERVER_URL}/experiment/{exp_id}/status")
    tests.append(("Get Status", r.status_code == 200))
    
    # Test 4: Get Global Model
    r = requests.get(f"{SERVER_URL}/experiment/{exp_id}/global-model")
    tests.append(("Get Global Model", "version" in r.json()))
    
except Exception as e:
    tests.append(("API Endpoints", False))

# Results
print("\n📊 Results:\n")
passed = sum(1 for _, p in tests if p)
total = len(tests)

for name, result in tests:
    icon = "✅" if result else "❌"
    print(f"{icon} {name}")

print(f"\n📈 Pass Rate: {passed}/{total} ({passed/total*100:.0f}%)")

if passed == total:
    print("\n🎉 ALL TESTS PASSED - READY TO PUSH v2.0!")
    print("\nCommands:")
    print("  git add .")
    print("  git commit -m 'feat: v2.0 - Async aggregation + staleness handling + multi-framework'")
    print("  git push origin main")
else:
    print("\n⚠️  Some tests failed")

print("="*60)
