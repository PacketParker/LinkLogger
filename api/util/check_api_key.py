from fastapi import Security, HTTPException, Depends, status
from fastapi.security import APIKeyHeader

from models import User
from api.util.db_dependency import get_db

"""
Make sure the provided API key is valid, then return the user's ID
"""
api_key_header = APIKeyHeader(name="X-API-Key")


def check_api_key(
    api_key_header: str = Security(api_key_header), db=Depends(get_db)
) -> str:
    response = db.query(User).filter(User.api_key == api_key_header).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    return {"value": api_key_header, "owner": response.id}
