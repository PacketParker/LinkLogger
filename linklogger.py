import uvicorn

import config
from app.main import app
from database import Base, engine


Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    config.load_config()
    uvicorn.run(app, port=5252)
