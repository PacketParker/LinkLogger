import bcrypt
from fastapi import Depends

from api.util.db_dependency import get_db
from models import User

"""
Validate the login information provided by the user
"""


def validate_login_information(
    username: str, password: str, db=Depends(get_db)
) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return True
    return False
