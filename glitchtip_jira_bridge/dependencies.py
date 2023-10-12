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


def auth_query_param(token: str | None = None) -> str | None:
    return token


def api_key_auth(
    token_via_header: str | None = Depends(oauth2_scheme),
    token_via_param: str | None = Depends(auth_query_param),
) -> None:
    token = token_via_header or token_via_param
    if not token or token not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden"
        )
