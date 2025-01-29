import sqlite3

# При первом запуске создадим таблицу с новым полем
def init_db():
    conn = sqlite3.connect('bot_stats.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            username TEXT,
            chat_id INTEGER,
            request TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Вызовите эту функцию при старте бота
init_db()
