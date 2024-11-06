import requests
import datetime
from ua_parser import user_agent_parser

from database import SessionLocal
import config
from models import Link, Log

"""
Create a new log whenever a link is visited
"""


def ip_to_location(ip):
    if not config.IP_TO_LOCATION:
        return "-, -", "-"

    url = f"https://api.ip2location.io/?key={config.API_KEY}&ip={ip}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        config.LOG.error(
            "Error with IP2Location API. Perhaps the API is down."
        )
        return "-, -", "-"

    if "error" in data:
        config.LOG.error(
            "Error with IP2Location API. Likely wrong API key or insufficient"
            " funds."
        )
        return "-, -", "-"

    location = ""
    # Sometimes a certain name may not be present, so always check
    if "city_name" in data:
        location += data["city_name"]

    if "region_name" in data:
        location += f', {data["region_name"]}'

    if "country_name" in data:
        location += f', {data["country_name"]}'

    isp = data["as"]
    return location, isp


def log(link, ip, user_agent):
    db = SessionLocal()

    # Get the redirect link and owner of the link
    redirect_link, owner = (
        db.query(Link.redirect_link, Link.owner)
        .filter(Link.link == link)
        .first()
    )

    # Get the location and ISP of the user
    location, isp = ip_to_location(ip)

    ua_string = user_agent_parser.Parse(user_agent)
    browser = ua_string["user_agent"]["family"]
    os = f'{ua_string["os"]["family"]} {ua_string["os"]["major"]}'

    # Create the log and commit it to the database
    new_log = Log(
        owner=owner,
        link=link,
        ip=ip,
        location=location,
        browser=browser,
        os=os,
        user_agent=user_agent,
        isp=isp,
    )
    db.add(new_log)
    db.commit()
    db.close()

    # Return the redirect link in order to properly redirect the user
    return redirect_link
