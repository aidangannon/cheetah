from sqlmodel import create_engine, Session
import structlog
from fastapi import FastAPI
from sqlmodel import create_engine, Session

# Configure logging
app = FastAPI(title="Customer API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Customer API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)