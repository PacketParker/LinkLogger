import fastapi
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
import sqlalchemy

from db import engine

"""
Make sure the provided API key is valid
"""
api_key_header = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key_header: str = Security(api_key_header)) -> str:
    with engine.begin() as conn:
        response = conn.execute(sqlalchemy.text("SELECT api_key FROM keys WHERE api_key = :api_key"), {'api_key': api_key_header}).fetchone()
    if response:
        return response[0]
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
