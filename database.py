import sqlite3

DB_NAME = "eglise.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS eglise (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        church_id TEXT UNIQUE NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT NOT NULL,
        telephone TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        actif INTEGER DEFAULT 1
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS presence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        heure TEXT NOT NULL,
        type TEXT NOT NULL
    )
    """)

    # ---- SEED (création admin + église démo si base vide) ----
    c.execute("SELECT COUNT(*) FROM users")
    nb_users = c.fetchone()[0]

    if nb_users == 0:
        church_id = "EGLISE001"
        c.execute(
            "INSERT OR IGNORE INTO eglise (nom, church_id) VALUES (?, ?)",
            ("Église Démo", church_id)
        )

        c.execute("""
        INSERT INTO users (church_id, telephone, password, role, actif)
        VALUES (?, ?, ?, ?, 1)
        """, (church_id, "0990000000", "1234", "Admin"))

    conn.commit()
    conn.close()
