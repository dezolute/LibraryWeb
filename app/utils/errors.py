from fastapi import HTTPException
from starlette import status

Forbidden = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to perform this action."
)