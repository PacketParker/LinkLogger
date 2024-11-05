from pydantic import BaseModel


class LoginDataSchema(BaseModel):
    username: str
    password: str


class UpdatePasswordSchema(BaseModel):
    password: str
    new_password: str
