import random
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from typing import Annotated
import jwt

from api.util.db_dependency import get_db
from api.schemas.auth_schemas import *
from models import User as UserDB

secret_key = random.randbytes(32)
algorithm = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

"""
Helper functions for authentication
"""


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_user(db, username: str):
    """
    Get the user object from the database
    """
    user = db.query(UserDB).filter(UserDB.username == username).first()
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


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    is_refresh: bool = False,
    db=Depends(get_db),
):
    """
    Return the current user based on the token, or raise a 401 error
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        refresh: bool = payload.get("refresh")
        if username is None:
            raise credentials_exception
        # For some reason, an access token was passed when a refresh
        # token was expected - some likely malicious activity
        if not refresh and is_refresh:
            raise credentials_exception
        # If the token passed is a refresh token and the function
        # is not expecting a refresh token, raise an error
        if refresh and not is_refresh:
            raise credentials_exception

        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
