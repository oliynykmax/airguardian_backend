from pydantic import BaseModel

class HealthResponse(BaseModel):
    success: str
