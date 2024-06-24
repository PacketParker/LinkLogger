from pydantic import BaseModel


class URLSchema(BaseModel):
    url: str
