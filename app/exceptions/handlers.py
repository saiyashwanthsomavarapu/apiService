import logging
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.exceptions.event_exceptions import BaseCustomException
from app.schemas.error_responses import ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)

async def custom_exception_handler(request: Request, exc: BaseCustomException):
    error_response = ErrorResponse(
        error=ErrorDetail(
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            timestamp=datetime.now().isoformat(),
            path=str(request.url.path)
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Handle specific SQLAlchemy errors
    if isinstance(exc, IntegrityError):
        message = "Data integrity constraint violation"
        status_code = status.HTTP_409_CONFLICT
    else:
        message = "Database operation failed"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            message=message,
            status_code=status_code,
            details={"error_type": type(exc).__name__},
            timestamp=datetime.now().isoformat(),
            path=str(request.url.path)
        )
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_response = ErrorResponse(
        error=ErrorDetail(
            message="Validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": exc.errors()},
            timestamp=datetime.now().isoformat(),
            path=str(request.url.path)
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}, {exc.status_code}, date: {datetime.now()}, path: {request.url.path}")
    error_response = ErrorResponse(
        error=ErrorDetail(
            message=exc.detail,
            status_code=exc.status_code,
            timestamp=datetime.now().isoformat(),
            path=str(request.url.path)
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )