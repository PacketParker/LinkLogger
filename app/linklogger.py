from routes import app
from db import init_db
import waitress
import threading
import schedule
import time

from func.remove_old_data import remove_old_data

if __name__ == '__main__':
    init_db()
    thread = threading.Thread(target=waitress.serve, args=(app,), kwargs={'port': 5252})
    thread.start()
    print('Server running on port 5252. Healthy.')

    schedule.every().day.at('00:01').do(remove_old_data)
    while True:
        schedule.run_pending()
        time.sleep(1)