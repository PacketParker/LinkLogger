from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.routes.auth_routes import router as auth_router
from app.routes.links_routes import router as links_router
from app.routes.user_routes import router as user_router
from typing import Annotated
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.util.authentication import get_current_user_from_cookie
from app.schemas.auth_schemas import User

app = FastAPI(
    title="LinkLogger API",
    version="1.0",
    summary="Public API for a combined link shortener and IP logger",
    license_info={
        "name": "The Unlicense",
        "identifier": "Unlicense",
        "url": "https://unlicense.org",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

templates = Jinja2Templates(directory="app/templates")

# Import routes
app.include_router(auth_router, prefix="/api")
app.include_router(links_router, prefix="/api")
app.include_router(user_router, prefix="/api")


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# TODO: Create users routes
# User - register/create
# User - delete
# User - update

# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         # Verify the password meets requirements
#         if len(password) < 8:
#             return {"status": "Password must be at least 8 characters"}
#         if not any(char.isdigit() for char in password):
#             return {"status": "Password must contain at least one digit"}
#         if not any(char.isupper() for char in password):
#             return {
#                 "status": "Password must contain at least one uppercase letter"
#             }

#         # Get database session
#         db = SessionLocal()

#         user = db.query(User).filter(User.username == username).first()
#         if user:
#             db.close()
#             return {"status": "Username not available"}
#         # Add information to the database
#         hashed_password = bcrypt.hashpw(
#             password.encode("utf-8"), bcrypt.gensalt()
#         ).decode("utf-8")
#         api_key = "".join(
#             random.choices(string.ascii_letters + string.digits, k=20)
#         )
#         new_user = User(
#             username=username, password=hashed_password, api_key=api_key
#         )
#         db.add(new_user)
#         db.commit()
#         db.close()
#         # Log in the newly created user
#         flask_user = FlaskUser()
#         flask_user.id = username
#         login_user(flask_user)

#         return {"status": "success"}
#     return render_template("signup.html")


@app.get("/dashboard")
async def dashboard(
    response: Annotated[
        User, RedirectResponse, Depends(get_current_user_from_cookie)
    ],
    request: Request,
):
    if isinstance(response, RedirectResponse):
        return response
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": response.username}
    )


# @app.get("/{link}")
# async def log_redirect(
#     link: Annotated[str, Path(title="Redirect link")],
#     request: Request,
#     db=Depends(get_db),
# ):
#     link = link.upper()
#     # If `link` is not exactly 5 characters, return redirect to base url
#     if len(link) != 5:
#         return RedirectResponse(url="/login")

#     # Make sure the link exists in the database
#     link_record: Link = db.query(Link).filter(Link.link == link).first()
#     if not link_record:
#         db.close()
#         return RedirectResponse(url="/login")
#     else:
#         # Log the visit
#         if request.headers.get("X-Real-IP"):
#             ip = request.headers.get("X-Real-IP").split(",")[0]
#         else:
#             ip = request.client.host
#         user_agent = request.headers.get("User-Agent")
#         log(link, ip, user_agent)
#         db.close()
#         return RedirectResponse(url=link_record.redirect_link)


# Redirect /api -> /api/docs
@app.get("/api")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


# Custom handler for 404 errors
@app.exception_handler(HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")
