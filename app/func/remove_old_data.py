import sqlalchemy
import datetime

from db import engine

"""
Remove all links and associated records when the expire date has passed
"""
def remove_old_data():
    with engine.begin() as conn:
        today = datetime.datetime.date(datetime.datetime.now())
        old_links = conn.execute(sqlalchemy.text('SELECT link FROM links WHERE expire_date < :today'), [{'today': today}])

    delete_links = []

    for row in old_links:
        link = row.link
        delete_links.append({'link': link})

    if delete_links:
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text('DELETE FROM links WHERE link = :link'), delete_links)
            conn.execute(sqlalchemy.text('DELETE FROM records WHERE link = :link'), delete_links)
            conn.commit()
