import sqlalchemy

from db import engine

"""
Delete the specified link from the users associated links
"""
def delete_link(link, owner):
    with engine.begin() as conn:
        try:
            link_owner = conn.execute(sqlalchemy.text('SELECT owner FROM links WHERE link = :link'), [{'link': link}]).fetchone()[0]
        except TypeError:
            return 'Link does not exist', 200

    if owner == link_owner:
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text('DELETE FROM links WHERE link = :link'), [{'link': link}])
            return 'Link has been deleted', 200
    else:
        return 'You are not the owner of this link', 401