from sqlmodel import create_engine, Session
import structlog
from fastapi import FastAPI
from sqlmodel import create_engine, Session
from structlog import BoundLogger

from src.bootstrap import bootstrap
from src.crosscutting import set_container, inject, logging_scope

container = bootstrap()
set_container(container)
app = FastAPI(title="Customer API", version="0.1.0")

@app.get("/")
async def root(logger: BoundLogger = inject(BoundLogger)):
    with logging_scope(operation="My stuff"):
        logger.info(f"My stuff", fay=2)
        return {"message": "Customer API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)