from fastapi import APIRouter, status, Path, Depends
from fastapi.exception_handlers import HTTPException
from typing import Annotated
import string
import random
import datetime
import validators

from app.util.db_dependency import get_db
from models import Link, Record
from app.schemas.links_schemas import URLSchema
from app.schemas.auth_schemas import User
from app.util.authentication import get_current_user_from_token


router = APIRouter(prefix="/links", tags=["links"])


@router.get("/", summary="Get all of the links associated with your account")
async def get_links(
    current_user: Annotated[User, Depends(get_current_user_from_token)],
    db=Depends(get_db),
):
    links = db.query(Link).filter(Link.owner == current_user.id).all()
    if not links:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No links found"
        )
    return links


@router.post("/", summary="Create a new link")
async def create_link(
    url: URLSchema,
    current_user: Annotated[User, Depends(get_current_user_from_token)],
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
                expire_date=datetime.datetime.now()
                + datetime.timedelta(days=30),
            )
            db.add(new_link)
            db.commit()
            break
        except:
            continue

    return {
        "response": "Link successfully created",
        "expire_date": new_link.expire_date,
        "link": new_link.link,
    }


@router.delete("/{link}", summary="Delete a link")
async def delete_link(
    link: Annotated[str, Path(title="Link to delete")],
    current_user: Annotated[User, Depends(get_current_user_from_token)],
    db=Depends(get_db),
):
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

    # Get and delete all records associated with the link
    records = db.query(Record).filter(Record.link == link.link).all()
    for record in records:
        db.delete(record)
    # Delete the link
    db.delete(link)
    db.commit()

    return {"response": "Link successfully deleted", "link": link.link}


@router.get(
    "/{link}/records",
    summary="Get all of the IP log records associated with a link",
)
async def get_link_records(
    link: Annotated[str, Path(title="Link to get records for")],
    current_user: Annotated[User, Depends(get_current_user_from_token)],
    db=Depends(get_db),
):
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

    # Get and return all of the records associated with the link
    records = db.query(Record).filter(Record.link == link.link).all()
    return records


@router.delete(
    "/{link}/records",
    summary="Delete all of the IP log records associated with a link",
)
async def delete_link_records(
    link: Annotated[str, Path(title="Link to delete records for")],
    current_user: Annotated[User, Depends(get_current_user_from_token)],
    db=Depends(get_db),
):
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

    # Get all of the records associated with the link and delete them
    records = db.query(Record).filter(Record.link == link.link).all()
    for record in records:
        db.delete(record)
    db.commit()

    return {"response": "Records successfully deleted", "link": link.link}
