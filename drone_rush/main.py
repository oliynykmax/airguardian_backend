from fastapi import FastAPI
from .schemas import HealthResponse
from .models import Base
from .database import engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"success": "ok"}

@app.get("/")
def root():
    return {"message": "Welcome to Airguardian API"}
