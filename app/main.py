from flask_login import (
    current_user,
    login_user,
    login_required,
    logout_user,
    LoginManager,
    UserMixin,
)
from flask import Flask, redirect, render_template, request, url_for, Request
import bcrypt
import os
import string
import random

from models import User
from database import *
from app.util.log import log
from var import BASE_URL 


class FlaskUser(UserMixin):
    pass


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(username):
    user = FlaskUser()
    user.id = username
    return user


"""
Handle login requests from the web UI
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Get database session
        db = SessionLocal()

        user = db.query(User).filter(User.username == username).first()
        db.close()
        if not user:
            return {"status": "Invalid username or password"}

        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            flask_user = FlaskUser()
            flask_user.id = username
            login_user(flask_user)
            return {"status": "success"}

        return {"status": "Invalid username or password"}
    return render_template("login.html")


"""
Handle signup requests from the web UI
"""


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Get database session
        db = SessionLocal()

        user = db.query(User).filter(User.username == username).first()
        if user:
            db.close()
            return {"status": "User already exists"}
        # Add information to the database
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        api_key = "".join(random.choices(string.ascii_letters + string.digits, k=20))
        new_user = User(username=username, password=hashed_password, api_key=api_key)
        db.add(new_user)
        db.commit()
        db.close()
        # Log in the newly created user
        flask_user = FlaskUser()
        flask_user.id = username
        login_user(flask_user)

        return {"status": "success"}
    return render_template("signup.html")


"""
Load the 'dashboard' page for logged in users
"""


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # Get database session
    db = SessionLocal()

    # Get the API key for the current user
    user = db.query(User).filter(User.username == current_user.id).first()
    db.close()
    api_key = user.api_key

    return render_template("dashboard.html", api_key=api_key)


"""
Log users out of their account
"""


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


"""
Log all records for visits to shortened links
"""


@app.route("/<link>", methods=["GET"])
def log_redirect(link):
    # If the `link` is more than 5 characters, ignore
    if len(link) > 5:
        return redirect(BASE_URL)

    # If the `link` is one of the registered routes, ignore
    if link in ["login", "signup", "dashboard", "logout", "api"]:
        return

    ip = request.remote_addr
    user_agent = request.headers.get("user-agent")
    redirect_link = log(link, ip, user_agent)
    return redirect(redirect_link)


@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for("login"))


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for("login"))
