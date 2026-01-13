import sqlite3
from datetime import datetime

DB_NAME = "eglise.db"


def marquer_presence(user_id: int, type_presence: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    now = datetime.now()
    c.execute("""
    INSERT INTO presence (user_id, date, heure, type)
    VALUES (?, ?, ?, ?)
    """, (user_id, str(now.date()), now.strftime("%H:%M:%S"), type_presence))

    conn.commit()
    conn.close()
