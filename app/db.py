import sqlalchemy

engine = sqlalchemy.create_engine('sqlite:///data.db')

def init_db():
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text(
            '''
            CREATE TABLE IF NOT EXISTS accounts (
                account_name, PRIMARY KEY (account_name)
            )
            '''
        ))
        conn.execute(sqlalchemy.text(
            '''
            CREATE TABLE IF NOT EXISTS links (
                owner, link, redirect_link, expire_date,
                FOREIGN KEY (owner) REFERENCES accounts(account_name), PRIMARY KEY (link)
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