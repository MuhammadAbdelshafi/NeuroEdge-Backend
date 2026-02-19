import uvicorn
import os

if __name__ == "__main__":
    # Ensure we are in the correct directory (user_service root)
    # This script should be run as `python run.py`
    
    # Check if .env is loaded (optional, python-dotenv usually handles this in app/main.py or settings)
    # But settings.py uses pydantic BaseSettings which reads .env automatically if present.
    
    print("Starting User Service on http://127.0.0.1:8001")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
