import ip2locationio
import sqlalchemy
import datetime
import validators
from ua_parser import user_agent_parser
from dotenv import load_dotenv
import os
from ip2locationio.ipgeolocation import IP2LocationIOAPIError

from db import engine

load_dotenv()
try:
    ip_to_location = os.getenv('IP_TO_LOCATION').upper().replace('"', '')
    if ip_to_location == 'TRUE':
        api_key = os.getenv('API_KEY').replace('"', '')
    else:
        api_key = "NO_API_KEY"

    base_url = os.getenv('BASE_URL').replace('"', '')
# .env File does not exist - likely a docker run
except AttributeError:
    ip_to_location = str(os.environ['IP_TO_LOCATION']).upper().replace('"', '')
    if ip_to_location == 'TRUE':
        api_key = str(os.environ('API_KEY')).replace('"', '')
    else:
        api_key = "NO_API_KEY"

    base_url = str(os.environ('BASE_URL')).replace('"', '')

if not validators.url(base_url):
    print(base_url)
    print('BASE_URL varaible is malformed.')
    exit()

configuration = ip2locationio.Configuration(api_key)
ipgeolocation = ip2locationio.IPGeolocation(configuration)

"""
Create a new log record whenever a link is visited
"""
def log(link, ip, user_agent):
    with engine.begin() as conn:
        try:
            redirect_link, owner = conn.execute(sqlalchemy.text('SELECT redirect_link, owner FROM links WHERE link = :link'), [{'link': link}]).fetchone()
        except TypeError:
            return base_url

    with engine.begin() as conn:
        if ip_to_location == 'TRUE':
            # Get IP to GEO via IP2Location.io
            try:
                data = ipgeolocation.lookup(ip)
                location = f'{data["country_name"]}, {data["city_name"]}'
                isp = data['as']
            # Fatal error, API key is invalid or out of requests, quit
            except IP2LocationIOAPIError:
                print('Invalid API key or insifficient credit. Change .env file if you do not need IP to location feature.')
                location = '-, -'
                isp = '-'
        else:
            location = '-, -'
            isp = '-'

        timestamp = datetime.datetime.now()
        ua_string = user_agent_parser.Parse(user_agent)
        browser = ua_string['user_agent']['family']
        os = f'{ua_string["os"]["family"]} {ua_string["os"]["major"]}'

        conn.execute(sqlalchemy.text('INSERT INTO records (owner, link, timestamp, ip, location, browser, os, user_agent, isp) VALUES (:owner, :link, :timestamp, :ip, :location, :browser, :os, :user_agent, :isp)'), [{'owner': owner, 'link': link, 'timestamp': timestamp, 'ip': ip, 'location': location, 'browser': browser, 'os': os, 'user_agent': user_agent, 'isp': isp}])

    return redirect_link