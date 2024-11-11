from fastapi import APIRouter, status, Path, Depends
from fastapi.exception_handlers import HTTPException
from typing import Annotated
import string
import random
import datetime
import validators

from api.util.db_dependency import get_db
from models import Link, Log
from api.schemas.links_schemas import URLSchema
from api.schemas.auth_schemas import User
from api.util.authentication import get_current_user


router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", summary="Get all of the logs associated with your account")
async def get_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    logs = (
        db.query(Log)
        .filter(Log.owner == current_user.id)
        .order_by(Log.timestamp.desc())
        .all()
    )
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No logs found"
        )
    return logs


@router.get("/{log_id}", summary="Get a specific log")
async def get_log(
    log_id: Annotated[int, Path(title="ID of log to delete")],
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    log = (
        db.query(Log)
        .filter(Log.id == log_id, Log.owner == current_user.id)
        .first()
    )
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )
    return log


@router.delete("/{log_id}", summary="Delete a log")
async def delete_log(
    log_id: Annotated[int, Path(title="ID of log to delete")],
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    log = (
        db.query(Log)
        .filter(Log.id == log_id, Log.owner == current_user.id)
        .first()
    )
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )
    db.delete(log)
    db.commit()
    return status.HTTP_204_NO_CONTENT
