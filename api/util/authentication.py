import random
import bcrypt
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import Response
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta
import jwt

from api.util.db_dependency import get_db
from sqlalchemy.orm import Session
from api.schemas.auth_schemas import *
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


def get_user(db, username: str):
    """
    Get the user object from the database
    """
    user = db.query(UserModel).filter(UserModel.username == username).first()
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
        print("WHY")
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


def raise_unauthorized():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    request: Request,
    db=Depends(get_db),
):
    """
    Return the current user object if the access token is valid

    All failed attempts will return a 401
    """
    token = request.cookies.get("access_token")

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        id: int = payload.get("sub")
        username: str = payload.get("username")
        if not id or not username:
            return raise_unauthorized()

    except InvalidTokenError:
        return raise_unauthorized()

    user = get_user(db, username)
    if user is None:
        return raise_unauthorized()

    return user
