# setup_initial_data.py
from datetime import datetime
import sqlite3
import db_init


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def seed_demo_if_empty():
    db_init.ensure_tables()
    conn = db_init.connect()
    try:
        c = conn.cursor()

        # UNIT par défaut
        c.execute("SELECT COUNT(*) AS n FROM units")
        if c.fetchone()["n"] == 0:
            c.execute(
                "INSERT INTO units(unit_id, unit_name, active, created_at, updated_at) VALUES(?,?,?,?,?)",
                ("U001", "Eglise Démo", 1, now_str(), now_str())
            )

        # USERS démo (pasteur)
        c.execute("SELECT COUNT(*) AS n FROM users")
        if c.fetchone()["n"] == 0:
            # login: 0990000003 / 1234
            c.execute(
                "INSERT INTO users(phone, role, password, created_at, updated_at) VALUES(?,?,?,?,?)",
                ("0990000003", "PASTEUR", "1234", now_str(), now_str())
            )

        # RELATIONS démo
        c.execute("SELECT COUNT(*) AS n FROM relations")
        if c.fetchone()["n"] == 0:
            c.execute("""
                INSERT INTO relations(
                    rel_id, unit_id, boy_name, girl_name, boy_code, girl_code,
                    counselor, notes, status, start_date, open_date,
                    created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                "R001", "U001", "Jean", "Marie", "M012", "F034",
                "Pasteur", "Suivi initial", "OPEN", "2025-12-01", "2025-12-10",
                now_str(), now_str()
            ))
            c.execute("""
                INSERT INTO relations(
                    rel_id, unit_id, boy_name, girl_name, counselor, notes, status,
                    start_date, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                "R002", "U001", "Paul", "Sarah", "Pasteur",
                "Déclaration reçue", "DECLARATION",
                "2025-12-20", now_str(), now_str()
            ))

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    seed_demo_if_empty()
    print("OK: données démo prêtes.")
