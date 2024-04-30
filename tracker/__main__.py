import threading

from tracker.database import create_db_table
from tracker.mouse_tracker import main

if __name__ == "__main__":
    create_db_table()
    try:
        server = threading.Thread(target=main)
        server.start()
        print("process started")
        server.join()
    except KeyboardInterrupt:
        print("process finished")
