# FederX Demonstration Guide

## 🎯 Quick Start

### 1. Start the Server

```powershell
python -m backend.server.main
```

The server will start on `http://localhost:8000`

### 2. Run the Live Demo

In a **new terminal**:

```powershell
python demo_live_presentation.py
```

## 🎬 What You'll See

The demonstration showcases:

### **Federated Learning Workflow**

```
Round 1 → Round 2 → Round 3
   ↓         ↓         ↓
[Client Training]
   ↓         ↓         ↓
[Weight Submission]
   ↓         ↓         ↓
[Server Aggregation]
   ↓         ↓         ↓
[Model Improvement]
```

### **Live Output Example**

```
================================================================================
        🚀 FederX - Federated Learning Demonstration
================================================================================

Configuration:
  • Server: http://localhost:8000
  • Clients: 4
  • Federated Rounds: 3
  • Dataset: MNIST
  • Model: Convolutional Neural Network

────────────────────────────────────────────────────────────────────────────
  Round 1/3
────────────────────────────────────────────────────────────────────────────
[client_1] ✓ Trained on 15000 samples (loss: 0.8432)
[client_1] ✓ Update submitted: upd_0 (trust: 1.00, status: auto_approved)
[client_2] ✓ Trained on 15000 samples (loss: 0.7821)
[client_2] ✓ Update submitted: upd_1 (trust: 1.00, status: auto_approved)
...
  🔀 Server aggregating updates...
  ✓ Aggregated 4 updates → Global Model v1
  ✓ Global Model Accuracy: 85.23%
```

## 📊 Features Demonstrated

### 1. **Multi-Client Training**

- 4 clients train on private data (non-IID distribution)
- Each client keeps data local (privacy preserved)
- Shows real training progress with loss values

### 2. **Secure Aggregation**

- Server aggregates weight updates using FedAvg
- Trust scoring for each client
- Automatic approval based on trust thresholds

### 3. **Model Evolution**

- Shows accuracy improvement over rounds
- Visual progress bars for each round
- Clear performance metrics

### 4. **Weight Verification API**

- Demonstrates weight fetching endpoint
- Shows weight statistics (shape, mean, std)
- Ready for external hash function integration

### 5. **Admin Review System**

- Trust scores displayed for each update
- Review status (auto_approved/pending/rejected)
- Configurable approval thresholds

## 🎨 Presentation Tips

### For Live Demo:

1. **Start Server First** - Show the server starting
2. **Explain Architecture** - While demo runs, explain FL concepts
3. **Highlight Privacy** - Emphasize data never leaves clients
4. **Show Improvement** - Point out accuracy gains
5. **API Integration** - Demonstrate weight fetching

### Key Talking Points:

- **"Data stays private"** - Clients never share raw data
- **"Collaborative learning"** - Multiple parties improve one model
- **"Trust & Security"** - Built-in malicious client detection
- **"Production-ready"** - Admin review, staleness handling, multi-framework

## ⚙️ Customization

Edit `demo_live_presentation.py` to change:

```python
NUM_CLIENTS = 4      # Number of federated clients
NUM_ROUNDS = 3       # Number of training rounds
local_epochs = 2     # Epochs each client trains
```

### Quick Demo (1 minute):

```python
NUM_CLIENTS = 2
NUM_ROUNDS = 2
```

### Comprehensive Demo (5 minutes):

```python
NUM_CLIENTS = 5
NUM_ROUNDS = 5
```

## 🔍 Alternative Demos

### 1. **Complete Flow Demo** (All Perspectives)

```powershell
python demo_complete_flow.py
```

Shows server, admin, and client perspectives with detailed logging.

### 2. **Simple MNIST Demo**

```powershell
python -m client.examples.mnist_simple --experiment-id exp_demo --clients 3 --rounds 2
```

Basic federated learning example.

### 3. **Weight Fetching Test**

```powershell
python test_weights_detailed.py
```

Detailed weight inspection across all frameworks.

## 📝 Pre-Demo Checklist

- [ ] Server is running (`python -m backend.server.main`)
- [ ] Virtual environment activated (if using)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] MNIST data will auto-download (requires internet first time)
- [ ] Port 8000 is available

## 🐛 Troubleshooting

### Server Connection Error

```
✗ Cannot connect to server!
```

**Solution:** Start the server in another terminal first.

### Port Already in Use

```powershell
# Kill process on port 8000
netstat -ano | findstr :8000 | ForEach-Object { $_ -match '\s+(\d+)$' | Out-Null; $matches[1] } | Select-Object -First 1 | ForEach-Object { taskkill /F /PID $_ }
```

### Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Further Reading

- **Architecture**: See `STATUS.md` for complete system overview
- **API Documentation**: See `API_GUIDE.md` for all endpoints
- **Admin Review**: See `ADMIN_REVIEW_GUIDE.md` for review system
- **User Flow**: See `COMPLETE_USER_FLOW.md` for detailed walkthrough

## 🎓 For Different Audiences

### Technical Audience:

- Emphasize architecture and implementation details
- Show code snippets from adapters
- Discuss aggregation algorithms
- Demonstrate API endpoints

### Business Audience:

- Focus on privacy benefits
- Highlight collaborative learning
- Show clear accuracy improvements
- Emphasize production-readiness

### Academic Audience:

- Discuss FedAvg, FedProx algorithms
- Explain staleness and trust mechanisms
- Show multi-framework support
- Reference research papers

---

**Ready to present FederX!** 🚀
