from fastapi import Header, HTTPException, status

from app.config import settings


def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    """
    Kiểm tra API key từ header X-API-Key.

    Moodle plugin sau này cần gửi:
    X-API-Key: <BACKEND_API_KEY>
    """

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if x_api_key != settings.BACKEND_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return True