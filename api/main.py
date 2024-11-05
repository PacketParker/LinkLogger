import random
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from api.util.authentication import (
    authenticate_user,
    create_access_token,
    refresh_get_current_user,
)
from api.routes.links_route import router as links_router
from api.util.db_dependency import get_db
from api.schemas.auth_schemas import Token, User


metadata_tags = [
    {"name": "links", "description": "Operations for managing links"},
]

app = FastAPI(
    title="LinkLogger API",
    version="1.0",
    summary="Public API for a combined link shortener and IP logger",
    license_info={
        "name": "The Unlicense",
        "identifier": "Unlicense",
        "url": "https://unlicense.org",
    },
    openapi_tags=metadata_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

secret_key = random.randbytes(32)
algorithm = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Import routes
app.include_router(links_router)


"""
Authentication
"""


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
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
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# Full native JWT support is not complete in FastAPI yet :(
# Part of that is token refresh, so we must implement it ourselves
@app.post("/refresh")
async def refresh_access_token(
    current_user: Annotated[User, Depends(refresh_get_current_user)],
) -> Token:
    """
    Return a new access token if the refresh token is valid
    """
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
    )


# Redirect /api -> /api/docs
@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/api/docs")
