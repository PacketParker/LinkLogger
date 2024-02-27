import sqlalchemy
from sqlalchemy import exc
import random
import string

from db import engine

"""
Generate and return a randomized API key string for the user
Keys are composed of 20 uppercase ASCII characters
"""
def generate_api_key():
    with engine.begin() as conn:
        while True:
            try:
                api_key_string = ''.join(random.choices(string.ascii_uppercase, k=20))
                conn.execute(sqlalchemy.text('INSERT INTO keys(api_key) VALUES(:api_key)'), [{'api_key': api_key_string}])
                conn.commit()
                break
            except exc.IntegrityError:
                continue

    return api_key_string