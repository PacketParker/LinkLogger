from pydantic import BaseModel


class LoginDataSchema(BaseModel):
    username: str
    password: str


class UpdatePasswordSchema(BaseModel):
    current_password: str
    new_password: str
