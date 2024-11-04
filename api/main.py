from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
import string
import random

from api.util.authentication import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from api.routes.links_route import router as links_router
from api.util.db_dependency import get_db
from api.schemas.auth_schemas import User, Token


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
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# Redirect /api -> /api/docs
@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/api/docs")
