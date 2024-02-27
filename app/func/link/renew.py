import sqlalchemy
import datetime

from db import engine

"""
Renew a specified link so that the user can continue logging through that URL
Adds 7 days from the current date
"""
def renew_link(link, owner):
    with engine.begin() as conn:
        try:
            link_owner = conn.execute(sqlalchemy.text('SELECT owner FROM links WHERE link = :link'), [{'link': link}]).fetchone()[0]
        except TypeError:
            return 404

    if owner == link_owner:
        with engine.begin() as conn:
            expire_date = datetime.datetime.date(datetime.datetime.now()) + datetime.timedelta(days=7)
            conn.execute(sqlalchemy.text('UPDATE links SET expire_date = :expire_date WHERE link = :link'), [{'expire_date': expire_date, 'link': link}])
            return link, expire_date
    else:
        return 401