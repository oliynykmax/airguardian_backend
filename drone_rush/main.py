from fastapi import FastAPI, HTTPException, Depends
from .schemas import HealthResponse
from .models import Base
from .database import engine
from .logic import fetch_and_store_violations, fetch_drones


app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"success": "ok"}

@app.get("/")
def root():
    return {"message": "Welcome to Airguardian API"}

@app.get("/drones")
def get_drones():
    data = fetch_drones()
    if data is None:
        raise HTTPException(status_code=502, detail="Failed to fetch drone data")
    return data
