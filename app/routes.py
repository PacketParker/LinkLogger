import flask
import tabulate
import sqlalchemy

from db import engine
from auth import auth
from func.signup import generate_account
from func.newlink import generate_link
from func.log import log
from func.delete_link import delete_link
from func.renew_link import renew_link
from func.link_records import link_records


app = flask.Flask(__name__)

@app.route('/signup', methods=['GET'])
def signup():
    account_name = generate_account()
    return flask.jsonify({'account_name': account_name})


@app.route('/newlink', methods=['POST'])
@auth.login_required
def newlink():
    response = generate_link(flask.request, auth.current_user())
    return flask.jsonify(msg=response[0]), response[1]


"""
Return all links associated with an account
"""
@app.route('/links', methods=['POST'])
@auth.login_required
def links():
    with engine.begin() as conn:
        links = conn.execute(sqlalchemy.text('SELECT link, expire_date FROM links WHERE owner = :owner'), [{'owner': auth.current_user()}]).fetchall()

    string = ""
    i = 1
    for link, expire_date in links:
        string += f"{i}. {link} - Expires on {expire_date}\n"
        i += 1
    return string


"""
Return all records associated with an account, no matter the link
"""
@app.route('/records', methods=['POST'])
@auth.login_required
def records():
    with engine.begin() as conn:
        records = conn.execute(sqlalchemy.text('SELECT timestamp, ip, location, browser, os, user_agent, isp FROM records WHERE owner = :owner'), [{'owner': auth.current_user()}]).fetchall()

    if not records:
        return flask.jsonify('No records found'), 200

    return tabulate.tabulate(records, headers=['Timestamp', 'IP', 'Location', 'Browser', 'OS', 'User Agent', 'ISP']), 200


@app.route('/<link>', methods=['GET'])
def link(link):
    redirect_link = log(link, flask.request)
    return flask.redirect(redirect_link)


@app.route('/<link>/delete', methods=['POST'])
@auth.login_required
def link_delete(link):
    response = delete_link(link, auth.current_user())
    return flask.jsonify(msg=response[0]), response[1]


@app.route('/<link>/renew', methods=['POST'])
@auth.login_required
def renew_link(link):
    response = renew_link(link, auth.current_user())
    return flask.jsonify(msg=response[0]), response[1]


@app.route('/<link>/records', methods=['POST'])
@auth.login_required
def records_link(link):
    response = link_records(link, auth.current_user())
    # If we jsonify the tabulate string it fucks it up, so we have to return
    # it normally, this check does that
    if response[0].startswith('Timestamp'):
        return response[0], response[1]
    else:
        return flask.jsonify(msg=response[0]), response[1]