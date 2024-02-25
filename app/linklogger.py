from routes import app
from db import init_db
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio

if __name__ == '__main__':
    init_db()
    config = Config()
    config.bind =["0.0.0.0:5252"]
    asyncio.run(serve(app, config))