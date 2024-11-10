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


router = APIRouter(prefix="/links", tags=["links"])


@router.get("", summary="Get all of the links associated with your account")
async def get_links(
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    # Get and sort links by expiration date descending
    links = (
        db.query(Link)
        .filter(Link.owner == current_user.id)
        .order_by(Link.expire_date.desc())
        .all()
    )
    if not links:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No links found"
        )
    return links


@router.post("", summary="Create a new link")
async def create_link(
    url: URLSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    # Check if the URL is valid
    if not validators.url(url.url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid URL",
        )
    # Create the new link and add it to the database
    while True:
        try:
            link_path = "".join(
                random.choices(string.ascii_uppercase + "1234567890", k=5)
            ).upper()
            new_link = Link(
                link=link_path,
                owner=current_user.id,
                redirect_link=url.url,
                expire_date=datetime.datetime.utcnow()
                + datetime.timedelta(days=30),
            )
            db.add(new_link)
            db.commit()
            break
        except:
            continue

    return {"link": link_path, "expire_date": new_link.expire_date}


@router.delete("/{link}", summary="Delete a link and all associated logs")
async def delete_link(
    link: Annotated[str, Path(title="Link to delete")],
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    """
    Delete a link and all of the logs associated with it
    """
    link = link.upper()
    # Get the link and check the owner
    link = db.query(Link).filter(Link.link == link).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    if link.owner != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with your account",
        )

    # Get and delete all logsk
    logs = db.query(Log).filter(Log.link == link.link).all()
    for log in logs:
        db.delete(log)
    # Delete the link
    db.delete(link)
    db.commit()

    return status.HTTP_204_NO_CONTENT


@router.get("/{link}/logs", summary="Get all logs associated with a link")
async def get_link_logs(
    link: Annotated[str, Path(title="Link to get logs for")],
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    """
    Get all of the IP logs associated with a link
    """
    link = link.upper()
    # Get the link and check the owner
    link = db.query(Link).filter(Link.link == link).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    if link.owner != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with your account",
        )

    # Get and return all of the logs - ordered by timestamp
    logs = (
        db.query(Log)
        .filter(Log.link == link.link)
        .order_by(Log.timestamp.desc())
        .all()
    )
    return logs


@router.delete(
    "/{link}/logs/{log_id}",
    summary="Delete a specific log associated with a link",
)
async def delete_single_log(
    link: Annotated[str, Path(title="Link associated with the log to delete")],
    log_id: Annotated[int, Path(title="Log ID to delete")],
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    """
    Delete the specified log associated with a link
    """
    link = link.upper()
    # Get the link and check the owner
    link = db.query(Link).filter(Link.link == link).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    if link.owner != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with your account",
        )

    # Get the log and delete it
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )
    db.delete(log)
    db.commit()

    return status.HTTP_204_NO_CONTENT
