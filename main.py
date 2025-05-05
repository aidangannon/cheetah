from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field,Boolean,  create_engine, Session, select, Column
from sqlalchemy import Index, text, String, DateTime, Numeric
from fastapi import FastAPI, 
import structlog






# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),

    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/intropy-test"

# Create engine only when needed (not during imports for Alembic)
def get_engine():
    return create_engine(DATABASE_URL, echo=True)

def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session

# FastAPI app
app = FastAPI(title="Customer API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Customer API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)