from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response, JSONResponse
from datetime import timedelta
from typing import Annotated

from app.util.authentication import (
    create_access_token,
    authenticate_user,
    refresh_get_current_user,
)
from app.schemas.auth_schemas import Token, User
from app.util.db_dependency import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", summary="Authenticate and get an access token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db=Depends(get_db),
):
    """
    Return an access token for the user, if the given authentication details are correct
    """
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "refresh": False},
        expires_delta=access_token_expires,
    )
    # Create a refresh token - just an access token with a longer expiry
    # and more restrictions ("refresh" is True)
    refresh_token_expires = timedelta(days=1)
    refresh_token = create_access_token(
        data={"sub": user.id, "username": user.username, "refresh": True},
        expires_delta=refresh_token_expires,
    )
    response = JSONResponse(content={"success": True})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True
    )
    return response

    # For Swagger UI to work, must return the token
    # return Token(
    #     access_token=access_token,
    #     refresh_token=refresh_token,
    #     token_type="bearer",
    # )


# Full native JWT support is not complete in FastAPI yet :(
# Part of that is token refresh, so we must implement it ourselves
@router.post("/refresh")
async def refresh_access_token(
    current_user: Annotated[User, Depends(refresh_get_current_user)],
) -> Token:
    """
    Return a new access token if the refresh token is valid
    """
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.id, "refresh": False},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
    )
