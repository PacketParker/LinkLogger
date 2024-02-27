import sqlalchemy
import os

try:
    os.mkdir('data')
except FileExistsError:
    pass
engine = sqlalchemy.create_engine('sqlite:///data/data.db')


def init_db():
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text(
            '''
            CREATE TABLE IF NOT EXISTS keys (
                api_key, PRIMARY KEY (api_key)
            )
            '''
        ))
        conn.execute(sqlalchemy.text(
            '''
            CREATE TABLE IF NOT EXISTS links (
                owner, link, redirect_link, expire_date,
                FOREIGN KEY (owner) REFERENCES keys(api_key), PRIMARY KEY (link)
            )
            '''
        ))
        conn.execute(sqlalchemy.text(
            '''
            CREATE TABLE IF NOT EXISTS records (
                owner, link, timestamp, ip, location, browser, os, user_agent, isp,
                FOREIGN KEY (owner) REFERENCES links(owner),
                FOREIGN KEY (link) REFERENCES links(link))
            '''
        ))

        conn.commit()