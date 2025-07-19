from fastapi import FastAPI
from .schemas import HealthResponse

app = FastAPI()

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"success": "ok"}

@app.get("/")
def root():
    return {"message": "Welcome to Airguardian API"}
