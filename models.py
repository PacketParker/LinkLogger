from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
import datetime

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    api_key = Column(String(20), unique=True, nullable=False)


class Link(Base):
    __tablename__ = "links"
    link = Column(String, primary_key=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    redirect_link = Column(String, nullable=False)
    expire_date = Column(DateTime, nullable=False)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    link = Column(String, ForeignKey("links.link"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    ip = Column(String, nullable=False)
    location = Column(String, nullable=False)
    browser = Column(String, nullable=False)
    os = Column(String, nullable=False)
    user_agent = Column(String, nullable=False)
    isp = Column(String, nullable=False)
