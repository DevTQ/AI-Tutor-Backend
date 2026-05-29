from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc),
            "path": str(request.url.path),
        },
    )