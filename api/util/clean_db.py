import datetime

from api.util.db_dependency import get_db
from models import Link, Log

"""
Remove expired short links and their associated logs
"""


def clean_db():
    db = next(get_db())
    # Get all expired short links
    expired_links = (
        db.query(Link)
        .filter(Link.expire_date < datetime.datetime.today())
        .all()
    )

    # Delete all expired short links and their logs
    for link in expired_links:
        logs = db.query(Log).filter(Log.link == link.link).all()
        for log in logs:
            db.delete(log)
        db.delete(link)
