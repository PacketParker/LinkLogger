import ip2locationio
import datetime
from ua_parser import user_agent_parser
from ip2locationio.ipgeolocation import IP2LocationIOAPIError

from database import SessionLocal
import config
from models import Link, Record

configuration = ip2locationio.Configuration(config.API_KEY)
ipgeolocation = ip2locationio.IPGeolocation(configuration)

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

    if config.IP_TO_LOCATION:
        # Get IP to GEO via IP2Location.io
        try:
            data = ipgeolocation.lookup(ip)
            location = f'{data["country_name"]}, {data["city_name"]}'
            isp = data["as"]
        # Fatal error, API key is invalid or out of requests, quit
        except IP2LocationIOAPIError:
            config.LOG.error(
                "Invalid API key or insufficient credits. Change the"
                " `config.ini` file if you no longer need IP geolocation."
            )
            location = "-, -"
            isp = "-"
    else:
        location = "-, -"
        isp = "-"

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
