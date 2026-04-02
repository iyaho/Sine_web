import sqlite3

def get_db():
    connection = sqlite3.connect('users.db')
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
