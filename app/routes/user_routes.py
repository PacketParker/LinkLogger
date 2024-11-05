from fastapi import APIRouter, status, Path, Depends
from fastapi.exception_handlers import HTTPException
from typing import Annotated
import string
import bcrypt
import random
import datetime
import validators

from app.util.db_dependency import get_db
from app.schemas.auth_schemas import User
from app.schemas.user_schemas import *
from models import User as UserModel
from app.util.authentication import get_current_user_from_token


router = APIRouter(prefix="/users", tags=["users"])


@router.delete("/{user_id}", summary="Delete your account")
async def delete_user(
    user_id: Annotated[int, Path(title="Link to delete")],
    current_user: Annotated[User, Depends(get_current_user_from_token)],
    db=Depends(get_db),
):
    """
    Delete the user account associated with the current user
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(user)
    db.commit()
    return status.HTTP_204_NO_CONTENT


@router.post("/{user_id}", summary="Update your account password")
async def update_pass(
    user_id: Annotated[int, Path(title="Link to update")],
    update_data: UpdatePasswordSchema,
    current_user: Annotated[User, Depends(get_current_user_from_token)],
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
    # Make sure the password meets all of the requirements
    # if len(update_data.new_password) < 8:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Password must be at least 8 characters",
    #     )
    # if not any(char.isdigit() for char in update_data.new_password):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Password must contain at least one digit",
    #     )
    # if not any(char.isupper() for char in update_data.new_password):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Password must contain at least one uppercase letter",
    #     )
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
    login_data: LoginDataSchema,
    db=Depends(get_db),
):
    """
    Given the login data (username, password) process the registration of a new
    user account and return either the user or an error message
    """
    username = login_data.username
    password = login_data.password
    print(username)
    print(password)
    # Make sure the password meets all of the requirements
    # if len(password) < 8:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Password must be at least 8 characters",
    #     )
    # if not any(char.isdigit() for char in password):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Password must contain at least one digit",
    #     )
    # if not any(char.isupper() for char in password):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Password must contain at least one uppercase letter",
    #     )
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
