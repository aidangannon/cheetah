from fastapi import FastAPI

from src.bootstrap import bootstrap
from src.web import lifespan

app = FastAPI(title="Metrics API", version="0.1.0", lifespan=lifespan)

bootstrap(app=app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)