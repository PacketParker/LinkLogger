import requests
import datetime
from ua_parser import user_agent_parser

from database import SessionLocal
import config
from models import Link, Record

"""
Create a new log record whenever a link is visited
"""


def log(link, ip, user_agent):
    db = SessionLocal()

    # Get the redirect link and owner of the link
    redirect_link, owner = (
        db.query(Link.redirect_link, Link.owner)
        .filter(Link.link == link)
        .first()
    )

    if not config.IP_TO_LOCATION:
        location = "-, -"
        isp = "-"
    # Get IP to GEO via IPGeolocation.io
    else:
        url = f"https://api.ip2location.io/?key={config.API_KEY}&ip={ip}"
        data = requests.get(url).json()
        print(data)
        if "error" in data:
            config.LOG.error(
                "Error with IP2Location API. Likely wrong API key or"
                " insufficient funds."
            )
            location = "-, -"
            isp = "-"
        else:
            location = f'{data["country_name"]}, {data["city"]}'
            isp = data["as"]

    timestamp = datetime.datetime.now()
    ua_string = user_agent_parser.Parse(user_agent)
    browser = ua_string["user_agent"]["family"]
    os = f'{ua_string["os"]["family"]} {ua_string["os"]["major"]}'

    # Create the log record and commit it to the database
    link_record = Record(
        owner=owner,
        link=link,
        timestamp=timestamp,
        ip=ip,
        location=location,
        browser=browser,
        os=os,
        user_agent=user_agent,
        isp=isp,
    )
    db.add(link_record)
    db.commit()
    db.close()

    # Return the redirect link in order to properly redirect the user
    return redirect_link
