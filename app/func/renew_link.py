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
            return 'Link does not exist', 200

    if owner == link_owner:
        with engine.begin() as conn:
            expire_date = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%d/%m/%Y')
            expire_date = datetime.datetime.strptime(expire_date, '%d/%m/%Y')
            conn.execute(sqlalchemy.text('UPDATE links SET expire_date = :expire_date WHERE link = :link'), [{'expire_date': expire_date, 'link': link}])
            return f'Link renewed, now expires on {expire_date}', 200
    else:
        return 'You are not the owner of this link', 401