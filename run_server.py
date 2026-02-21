"""Start the FastAPI server"""
import uvicorn
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.server.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("FederX - Federated Learning Server")
    print("=" * 60)
    print("Starting server at http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
