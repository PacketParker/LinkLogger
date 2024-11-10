from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response, JSONResponse
from datetime import timedelta
from typing import Annotated

from api.util.authentication import (
    create_access_token,
    authenticate_user,
)
from api.util.db_dependency import get_db


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
    access_token_expires = timedelta(minutes=1)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires,
    )
    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents client-side access
        # secure=True,  # Cookies are only sent over HTTPS
    )
    return response
