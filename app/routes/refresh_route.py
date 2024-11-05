from fastapi import Depends, APIRouter
from fastapi.responses import RedirectResponse
from datetime import timedelta
from typing import Annotated

from app.util.authentication import (
    create_access_token,
    refresh_get_current_user,
)
from app.schemas.auth_schemas import Token, User


router = APIRouter(prefix="/refresh", tags=["refresh"])


# Full native JWT support is not complete in FastAPI yet :(
# Part of that is token refresh, so we must implement it ourselves
@router.post("/")
async def refresh_access_token(
    current_user: Annotated[User, Depends(refresh_get_current_user)],
) -> Token:
    """
    Return a new access token if the refresh token is valid
    """
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.username, "refresh": False},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
    )
