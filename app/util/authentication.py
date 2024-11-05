import random
import bcrypt
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from typing import Annotated
import jwt

from app.util.db_dependency import get_db
from sqlalchemy.orm import sessionmaker
from app.schemas.auth_schemas import *
from models import User as UserModel

secret_key = random.randbytes(32)
algorithm = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

"""
Helper functions for authentication
"""


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_user(db, id: int):
    """
    Get the user object from the database
    """
    user = db.query(UserModel).filter(UserModel.id == id).first()
    if user:
        return UserInDB(**user.__dict__)


def authenticate_user(db, username: str, password: str):
    """
    Determine if the correct username and password were provided
    If so, return the user object
    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    """
    Return an encoded JWT token with the given data
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


async def get_current_user_from_cookie(
    access_token: str = Cookie(None), db=Depends(get_db)
):
    """
    Return the user based on the access token in the cookie

    Used for authentication into UI pages - so if no cookie
    exists, redirect to login page rather than returning a 401

    Also pass is_ui=True to alert get_current_user that we need
    to use RedirectResponse rather than raising an HTTPException
    """
    if access_token:
        return await get_current_user(access_token, is_ui=True, db=db)
    return RedirectResponse(url="/login")


async def get_current_user_from_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db=Depends(get_db),
):
    return await get_current_user(token, db=db)


# Backwards kinda of way to get refresh token support
# `refresh_get_current_user` is only called from /refresh
# and alerts `get_current_user` that it should expect a refresh token
async def refresh_get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db=Depends(get_db),
):
    return await get_current_user(token, is_refresh=True, db=db)


async def get_current_user(
    token: str,
    is_refresh: bool = False,
    is_ui: bool = False,
    db: sessionmaker = None,
):
    """
    Return the current user based on the token

    OR on error -
    If is_ui=True, the request is from a UI page and we should redirect to login
    Otherwise, the request is from an API and we should return a 401
    """

    def raise_unauthorized():
        if is_ui:
            return RedirectResponse(url="/login")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        id: int = payload.get("sub")
        refresh: bool = payload.get("refresh")
        if not id:
            return raise_unauthorized()
        # For some reason, an access token was passed when a refresh
        # token was expected - some likely malicious activity
        if not refresh and is_refresh:
            return raise_unauthorized()
        # If the token passed is a refresh token and the function
        # is not expecting a refresh token, raise an error
        if refresh and not is_refresh:
            return raise_unauthorized()

    except InvalidTokenError:
        return raise_unauthorized()

    user = get_user(db, id)
    if user is None:
        return raise_unauthorized()

    return user
