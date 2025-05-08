from fastapi import FastAPI

from src.web.bootstrap import bootstrap

app = FastAPI(title="Customer API", version="0.1.0")
bootstrap(app=app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)