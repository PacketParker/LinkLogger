import uvicorn

import config
from app.main import app


if __name__ == "__main__":
    config.load_config()
    uvicorn.run(app, port=5252)
