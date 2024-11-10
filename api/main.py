from fastapi import FastAPI, Depends, Request, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from api.routes.auth_routes import router as auth_router
from api.routes.links_routes import router as links_router
from api.routes.user_routes import router as user_router
from typing import Annotated
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from api.util.db_dependency import get_db
from api.util.log import log
from models import Link


app = FastAPI(
    title="LinkLogger API",
    version="2.0",
    summary="Public API for a combined link shortener and IP logger",
    license_info={
        "name": "The Unlicense",
        "identifier": "Unlicense",
        "url": "https://unlicense.org",
    },
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "localhost:3000",
    "127.0.0.1:3000",
    # f"{CUSTOM_DOMAIN}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
app.include_router(auth_router, prefix="/api")
app.include_router(links_router, prefix="/api")
app.include_router(user_router, prefix="/api")


@app.get("/c/{link}")
async def log_redirect(
    link: Annotated[str, Path(title="Redirect link")],
    request: Request,
    db=Depends(get_db),
):
    link = link.upper()
    # Links must be 5 characters long
    if len(link) != 5:
        return RedirectResponse(url="/login")

    # Make sure the link exists in the database
    link_record: Link = db.query(Link).filter(Link.link == link).first()
    if not link_record:
        db.close()
        return RedirectResponse(url="/login")
    else:
        # Get the IP and log the request
        if request.headers.get("X-Real-IP"):
            ip = request.headers.get("X-Real-IP").split(",")[0]
        else:
            ip = request.client.host
        user_agent = request.headers.get("User-Agent")
        log(link, ip, user_agent)
        db.close()
        return RedirectResponse(url=link_record.redirect_link)


# Redirect /api -> /api/docs
@app.get("/api")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


# Custom handler for 404 errors
@app.exception_handler(HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, exc: HTTPException):
    # If the request is from /api, return a JSON response
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=404,
            content={"message": "Resource not found"},
        )
    # Otherwise, redirect to the login page
    return RedirectResponse(url="/login")
