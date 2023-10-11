from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from .config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token", auto_error=False
)  # use token authentication


def auth_query_param(key: str | None = None) -> str | None:
    return key


def api_key_auth(
    key_via_header: str | None = Depends(oauth2_scheme),
    key_via_param: str | None = Depends(auth_query_param),
) -> None:
    api_key = key_via_header or key_via_param
    if not api_key or api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden"
        )
