from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from typing import Annotated
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from app.util.db_dependency import get_db
from app.util.authentication import (
    authenticate_user,
    create_access_token,
)
from app.schemas.auth_schemas import Token


router = APIRouter(prefix="/token", tags=["token"])


@router.post("/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db=Depends(get_db),
) -> Token:
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
        data={"sub": user.username, "refresh": False},
        expires_delta=access_token_expires,
    )
    # Create a refresh token - just an access token with a longer expiry
    # and more restrictions ("refresh" is True)
    refresh_token_expires = timedelta(days=1)
    refresh_token = create_access_token(
        data={"sub": user.username, "refresh": True},
        expires_delta=refresh_token_expires,
    )
    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, samesite="lax"
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, samesite="lax"
    )
    return response
