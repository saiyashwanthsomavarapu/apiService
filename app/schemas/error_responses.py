from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorDetail(BaseModel):
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    path: Optional[str] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
    success: bool = False
