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
def generate_link(request, owner):
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        try:
            redirect_link = request.json['redirect_link']
        except KeyError:
            return 'Redirect link not provided', 400

        if not validators.url(redirect_link):
            return 'Redirect link is malformed. Please try again', 400
    else:
        return 'Content-Type not supported', 400

    with engine.begin() as conn:
        choices = string.ascii_uppercase + '1234567890'
        while True:
            try:
                link = ''.join(random.choices(choices, k=5))
                conn.execute(sqlalchemy.text('INSERT INTO links(owner, link, redirect_link, expire_date) VALUES (:owner, :link, :redirect_link, :expire_date)'), [{'owner': owner, 'link': link, 'redirect_link': redirect_link, 'expire_date': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%d/%m/%Y')}])
                conn.commit()
                break
            except exc.IntegrityError:
                continue

    return link, 200
