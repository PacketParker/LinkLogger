import fastapi
from fastapi import Security, HTTPException, Request
from starlette.responses import RedirectResponse
import pydantic
import sqlalchemy

from db import engine
from check_api_key import check_api_key
from func.generate_api_key import generate_api_key
from func.newlink import generate_link
from func.log import log
from func.link.delete import delete_link
from func.link.renew import renew_link
from func.link.records import get_link_records
from func.link.delrecords import delete_link_records
from func.remove_old_data import remove_old_data

from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    # Create the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(remove_old_data, "cron", hour="0", minute="01")
    scheduler.start()
    yield

class Newlink(pydantic.BaseModel):
    redirect_link: str

app = fastapi.FastAPI(lifespan=lifespan)


@app.post("/api/getapikey")
async def get_api_key():
    """
    Create a new API key
    """
    api_key = generate_api_key()
    return {"api_key": api_key}


@app.post("/api/genlink")
async def newlink(newlink: Newlink, api_key: str = Security(check_api_key)):
    """
    Generate a new link that will redirect to the specified URL and log IPs in the middle
    """
    data = generate_link(newlink.redirect_link, api_key)
    if data == 422:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Malformed redirect link provided"
        )

    return {"link": data[0], "expire_date": data[1]}


"""
Return all records associated with an API key, no matter the link
"""
@app.get("/api/records")
async def records(api_key: str = Security(check_api_key)):
    """
    Get ALL IP logs records for every link tied to your API key
    """
    with engine.begin() as conn:
        records = conn.execute(sqlalchemy.text("SELECT timestamp, ip, location, browser, os, user_agent, isp FROM records WHERE owner = :owner"), [{"owner": api_key}]).fetchall()

    if not records:
        return {"records": "No records are associated with this API key"}

    response = []
    for timestamp, ip, location, browser, os, user_agent, isp in records:
        response.append({"timestamp": timestamp, "ip": ip, "location": location, "browser": browser, "os": os, "user_agent": user_agent, "isp": isp})

    return response


@app.get("/{link}")
def link(link, request: Request):
    ip = request.client.host
    user_agent = request.headers.get("user-agent")
    redirect_link = log(link, ip, user_agent)
    return fastapi.responses.RedirectResponse(url=redirect_link)


"""
Return all links associated with an API key
"""
@app.get("/api/links")
async def links(api_key: str = Security(check_api_key)):
    """
    Retrieve all links that are currently tied to your API key
    """
    with engine.begin() as conn:
        links = conn.execute(sqlalchemy.text("SELECT link, expire_date FROM links WHERE owner = :owner"), [{"owner": api_key}]).fetchall()

    if not links:
        return {"links": "No links are associated with this API key"}

    response = []
    for link, expire_date in links:
        response.append({"link": link, "expire_date": expire_date})
    return response


@app.post("/api/{link}/delete")
async def link_delete(link: str, api_key: str = Security(check_api_key)):
    """
    Delete the specified link and all records associated with it
    """
    data = delete_link(link, api_key)
    if data == 404:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Link does not exist"
        )
    if data == 401:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with given API key"
        )
    else:
        return {"link": f"The link {data} has been deleted"}


@app.post("/api/{link}/renew")
async def link_renew(link: str, api_key: str = Security(check_api_key)):
    """
    Renew a specifiec link (adds 7 more days from the current date)
    """
    data = renew_link(link, api_key)
    if data == 404:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Link does not exist"
        )
    if data == 401:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with given API key"
        )
    else:
        return {"link": f"The link {data[0]} has been renewed and will expire on {data[1]}"}


@app.get("/api/{link}/records")
async def link_records(link: str, api_key: str = Security(check_api_key)):
    """
    Retrieve all IP log records for the specified link
    """
    data = get_link_records(link, api_key)
    if data == 404:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Link does not exist"
        )
    if data == 401:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with given API key"
        )
    if data == 204:
        raise HTTPException(
            status_code=fastapi.status.HTTP_204_NO_CONTENT,
            detail="No records found"
        )
    else:
        response = []
        for timestamp, ip, location, browser, os, user_agent, isp in data:
            response.append({"timestamp": timestamp, "ip": ip, "location": location, "browser": browser, "os": os, "user_agent": user_agent, "isp": isp})

        return response


@app.post("/api/{link}/delrecords")
async def link_delrecords(link: str, api_key: str = Security(check_api_key)):
    """
    Delete all IP log records for the specified link
    """
    data = delete_link_records(link, api_key)
    if data == 404:
        raise HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Link does not exist"
        )
    if data == 401:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Link not associated with given API key"
        )
    else:
        return {"link": f"The records for link {data} have been deleted"}


# Redirect / -> /docs
@app.get("/", summary="Redirect to the Swagger UI documentation")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")