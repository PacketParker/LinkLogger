import fastapi
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
import tabulate
import pydantic
import sqlalchemy

from db import engine
from auth import auth
from func.signup import generate_account
from func.newlink import generate_link
from func.log import log
from func.delete_link import delete_link
from func.renew_link import renew_link
from func.link_records import link_records
from func.del_link_records import del_link_records

class Newlink(pydantic.BaseModel):
    redirect_link: str

app = fastapi.FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key_header: str = Security(api_key_header)) -> str:
    with engine.begin() as conn:
        response = conn.execute(sqlalchemy.text("SELECT api_key FROM accounts WHERE api_key = :api_key"), {'api_key': api_key_header}).fetchone()
    if response:
        return response[0]
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )


@app.get("/signup")
async def signup():
    api_key = generate_account()
    return {"api_key": api_key}


@app.post("/newlink")
async def newlink(newlink: Newlink, api_key: str = Security(check_api_key)):
    data = generate_link(newlink.redirect_link, api_key)
    if data:
        return {"link": data[0], "expire_date": data[1]}
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Malformed redirect link provided"
        )


@app.post("/links")
async def links(api_key: str = Security(check_api_key)):
    with engine.begin() as conn:
        links = conn.execute(sqlalchemy.text("SELECT link, expire_date FROM links WHERE owner = :owner"), [{"owner": api_key}]).fetchall()

    response = []
    for link, expire_date in links:
        response.append({"link": link, "expire_date": expire_date})
    return response


@app.post("/records")
async def records(api_key: str = Security(check_api_key)):
    with engine.begin() as conn:
        records = conn.execute(sqlalchemy.text("SELECT timestamp, ip, location, browser, os, user_agent, isp FROM records WHERE owner = :owner"), [{"owner": api_key}]).fetchall()

    if not records:
        return flask.jsonify('No records found'), 200

    return tabulate.tabulate(records, headers=['Timestamp', 'IP', 'Location', 'Browser', 'OS', 'User Agent', 'ISP']), 200


# """
# Return all records associated with an account, no matter the link
# """
# @app.route('/records', methods=['POST'])
# @auth.login_required
# def records():


# @app.route('/<link>', methods=['GET'])
# def link(link):
#     redirect_link = log(link, flask.request)
#     return flask.redirect(redirect_link)


# @app.route('/<link>/delete', methods=['POST'])
# @auth.login_required
# def link_delete(link):
#     response = delete_link(link, auth.current_user())
#     return flask.jsonify(msg=response[0]), response[1]


# @app.route('/<link>/renew', methods=['POST'])
# @auth.login_required
# def renew_link(link):
#     response = renew_link(link, auth.current_user())
#     return flask.jsonify(msg=response[0]), response[1]


# @app.route('/<link>/records', methods=['POST'])
# @auth.login_required
# def records_link(link):
#     response = link_records(link, auth.current_user())
#     # If we jsonify the tabulate string it fucks it up, so we have to return
#     # it normally, this check does that
#     if response[0].startswith('Timestamp'):
#         return response[0], response[1]
#     else:
#         return flask.jsonify(msg=response[0]), response[1]


# @app.route('/<link>/delrecords', methods=['POST'])
# @auth.login_required
# def records_delete(link):
#     response = del_link_records(link, auth.current_user())
#     return flask.jsonify(msg=response[0]), response[1]