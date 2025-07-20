from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HealthResponse(BaseModel):
    success: str

class RootResponse(BaseModel):
    message: str

class Drone(BaseModel):
    id: str
    x: float
    y: float
    z: float
    owner_id: int

class DronesResponse(BaseModel):
    drones: List[Drone]


class ViolationResponse(BaseModel):
    id: int
    timestamp: datetime
    drone_id: str
    position_x: float
    position_y: float
    position_z: float
    owner_first_name: str
    owner_last_name: str
    owner_ssn: str
    owner_phone: str
    owner_email: str
    owner_purchase_date: datetime

    model_config = {"from_attributes": True}


class NFZViolationsResponse(BaseModel):
    violations: List[ViolationResponse]
