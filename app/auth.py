from flask_httpauth import HTTPTokenAuth
import sqlalchemy

from db import engine


auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    try:
        with engine.begin() as conn:
            token = conn.execute(sqlalchemy.text('SELECT * FROM accounts WHERE account_name = :account_name'), [{'account_name': token}]).fetchone()
            return token[0]
    except TypeError:
        return False