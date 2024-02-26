import sqlalchemy
from sqlalchemy import exc
import random
import string

from db import engine

"""
Generate and return a randomized account string for the user
Account strings function as API authenticaton keys and are composed
of 20 uppercase ASCII characters
"""
def generate_account():
    with engine.begin() as conn:
        while True:
            try:
                account_string = ''.join(random.choices(string.ascii_uppercase, k=20))
                conn.execute(sqlalchemy.text('INSERT INTO accounts(api_key) VALUES(:api_key)'), [{'api_key': account_string}])
                conn.commit()
                break
            except exc.IntegrityError:
                continue

    return account_string