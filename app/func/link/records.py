import sqlalchemy

from db import engine

"""
Retrieve all records associated with a specific link
"""
def get_link_records(link, owner):
    with engine.begin() as conn:
        try:
            link_owner = conn.execute(sqlalchemy.text('SELECT owner FROM links WHERE link = :link'), [{'link': link}]).fetchone()[0]
        except TypeError:
            return 404

    if owner == link_owner:
        with engine.begin() as conn:
            records = conn.execute(sqlalchemy.text('SELECT timestamp, ip, location, browser, os, user_agent, isp FROM records WHERE owner = :owner and link = :link'), [{'owner': owner, 'link': link}]).fetchall()
        if not records:
            return 204
    else:
        return 401

    return records