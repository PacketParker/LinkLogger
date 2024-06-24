from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create 'data' directory at root if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

engine = create_engine("sqlite:///data/data.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
