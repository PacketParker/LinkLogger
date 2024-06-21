from db import init_db
import uvicorn

from routes import app


if __name__ == '__main__':
    init_db()
    server = uvicorn.run(app=app, host="0.0.0.0", port=5252)
