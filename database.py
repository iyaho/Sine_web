import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')

def get_db():
    connection = sqlite3.connect(DB_PATH)
    return connection
def init_db():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT
        )"""
    )
    connection.commit()

if __name__ == '__main__':
    init_db()
    print('DB 초기화 완료')
