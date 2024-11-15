from fastapi import APIRouter, status, Path, Depends
from fastapi.exception_handlers import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import string
import bcrypt
import random

from api.util.db_dependency import get_db
from api.util.check_password_reqs import check_password_reqs
from api.schemas.auth_schemas import User
from api.schemas.user_schemas import *
from models import User as UserModel
from models import Link as LinkModel
from models import Log as LogModel
from api.util.authentication import (
    verify_password,
    get_current_user,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", summary="Get your username")
async def get_username(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get the username of the current user
    """
    return {"username": current_user.username}


@router.delete("/{user_id}", summary="Delete your account")
async def delete_user(
    user_id: Annotated[int, Path(title="ID of user to delete")],
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    """
    Delete the user account associated with the current user
    """
    # No editing others accounts
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    # Get the user and delete them
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete all links and logs associated with the user
    links = (
        db.query(LinkModel).filter(LinkModel.owner == current_user.id).all()
    )
    for link in links:
        db.delete(link)
        logs = db.query(LogModel).filter(LogModel.link == link.link).all()
        for log in logs:
            db.delete(log)

    db.delete(user)
    db.commit()
    return status.HTTP_204_NO_CONTENT


@router.post("/{user_id}/password", summary="Update your account password")
async def update_pass(
    user_id: Annotated[int, Path(title="ID of user to update")],
    update_data: UpdatePasswordSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    """
    Update the pass of the current user account
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own account",
        )

    # Make sure that they entered the correct current password
    if not verify_password(
        update_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password",
        )

    # Make sure the password meets all of the requirements
    check_password_reqs(update_data.new_password)

    # Get the user and update the password
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.hashed_password = bcrypt.hashpw(
        update_data.new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    db.commit()
    return status.HTTP_204_NO_CONTENT


@router.post("/register", summary="Register a new user")
async def get_links(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db),
):
    """
    Given the login data (username, password) process the registration of a new
    user account and return either the user or an error message
    """
    username = form_data.username
    password = form_data.password

    # Make sure the password meets all of the requirements
    check_password_reqs(password)

    # Make sure the username isn't taken
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username not available",
        )
    # Otherwise, hash the password, create the api key, and add the new user
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    api_key = "".join(
        random.choices(string.ascii_letters + string.digits, k=20)
    )
    new_user = UserModel(
        username=username, hashed_password=hashed_password, api_key=api_key
    )
    db.add(new_user)
    db.commit()

    return status.HTTP_201_CREATED
