import validators
import random
import string
import datetime
import sqlalchemy
from sqlalchemy import exc

from db import engine

"""
Generate and return a new randomized link that is connected to the user
Links are composed of 5 uppercase ASCII characters + numbers
"""
def generate_link(redirect_link, owner):
    if not validators.url(redirect_link):
        return None

    with engine.begin() as conn:
        choices = string.ascii_uppercase + '1234567890'
        while True:
            try:
                link = ''.join(random.choices(choices, k=5))
                expire_date = datetime.datetime.date(datetime.datetime.now()) + datetime.timedelta(days=7)
                conn.execute(sqlalchemy.text('INSERT INTO links(owner, link, redirect_link, expire_date) VALUES (:owner, :link, :redirect_link, :expire_date)'), [{'owner': owner, 'link': link, 'redirect_link': redirect_link, 'expire_date': expire_date}])
                conn.commit()
                break
            except exc.IntegrityError:
                continue

    return link, expire_date
