from werkzeug.middleware.dispatcher import DispatcherMiddleware
from a2wsgi import ASGIMiddleware

from config import load_config
from app.main import app as flask_app
from api.main import app as fastapi_app
from database import Base, engine

Base.metadata.create_all(bind=engine)

flask_app.wsgi_app = DispatcherMiddleware(
    flask_app.wsgi_app,
    {
        "/": flask_app,
        "/api": ASGIMiddleware(fastapi_app),
    },
)

if __name__ == "__main__":
    load_config()
    flask_app.run(port=5252)
