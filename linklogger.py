import uvicorn

import config


if __name__ == "__main__":
    if config.load_config():
        from api.main import app
        from database import Base, engine

        Base.metadata.create_all(bind=engine)
        uvicorn.run(app, port=5252)
