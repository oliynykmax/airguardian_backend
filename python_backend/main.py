import logging
from fastapi import FastAPI, HTTPException, Header, Depends
from .schemas import (
    HealthResponse, RootResponse, DronesResponse,
    ViolationResponse, NFZViolationsResponse
)
from .logic import fetch_drones
import os
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import Base, Violation
from .database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware


# Configure logging for FastAPI app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)



app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"success": "ok"}

@app.get("/", response_model=RootResponse)
def root():
    return RootResponse(message="Welcome to Airguardian API")

@app.get("/drones", response_model=DronesResponse)
def get_drones():
    try:
        data = fetch_drones()
        if data is None:
            logger.error("Failed to fetch drone data from external API")
            raise HTTPException(status_code=502, detail="Failed to fetch drone data")
        return DronesResponse(drones=data)
    except Exception as e:
        logger.error(f"Exception in /drones endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_secret(x_secret: str = Header(...)):
    secret = os.getenv("NFZ_SECRET_KEY")
    if not secret or x_secret != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/nfz", response_model=NFZViolationsResponse, dependencies=[Depends(verify_secret)])
def get_nfz_violations(db: Session = Depends(get_db)):
    try:
        since = datetime.now() - timedelta(hours=24)
        violations = db.query(Violation).filter(Violation.timestamp >= since).all()
        return NFZViolationsResponse(
            violations=[ViolationResponse.model_validate(v) for v in violations]
        )
    except Exception as e:
        logger.error(f"Exception in /nfz endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
