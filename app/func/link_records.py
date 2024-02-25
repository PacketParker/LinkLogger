import sqlalchemy
import tabulate

from db import engine

"""
Retrieve all records associated with a specific link
"""
def link_records(link, owner):
    with engine.begin() as conn:
        try:
            link_owner = conn.execute(sqlalchemy.text('SELECT owner FROM links WHERE link = :link'), [{'link': link}]).fetchone()[0]
        except TypeError:
            return 'Link does not exist', 200

    if owner == link_owner:
        with engine.begin() as conn:
            records = conn.execute(sqlalchemy.text('SELECT timestamp, ip, location, browser, os, user_agent, isp FROM records WHERE owner = :owner and link = :link'), [{'owner': owner, 'link': link}]).fetchall()
        if not records:
            return 'No records are associated with this link', 200
    else:
        return 'You are not the owner of this link', 401

    return tabulate.tabulate(records, headers=['Timestamp', 'IP', 'Location', 'Browser', 'OS', 'User Agent', 'ISP']), 200