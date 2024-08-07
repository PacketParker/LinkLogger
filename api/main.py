from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import string
import random

from api.routes.links_route import router as links_router
from api.util.db_dependency import get_db
from api.util.check_api_key import check_api_key
from models import User


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

# Regenerate the API key for the user
@app.post("/regenerate")
async def regenerate(api_key: str = Security(check_api_key), db = Depends(get_db)):
    """Regenerate the API key for the user. Requires the current API key."""
    user = db.query(User).filter(User.api_key == api_key['value']).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Generate a new API key
    new_api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    user.api_key = new_api_key
    db.commit()

    return {"status": "success", "new_api_key": new_api_key}

# Redirect /api -> /api/docs
@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/api/docs")