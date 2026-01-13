# db_init.py
import os
import sqlite3
from datetime import datetime

DB_NAME = "eglise.db"


def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def connect(db_path=DB_NAME):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path=DB_NAME):
    conn = connect(db_path)
    cur = conn.cursor()

    # --- churches ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS churches (
        id TEXT PRIMARY KEY,
        name TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE',   -- ACTIVE | BANNED | DISABLED
        activation_code TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # --- users (per church) ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT,                          -- NULL for SUPER_ADMIN
        phone TEXT NOT NULL,
        fullname TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,                      -- SUPER_ADMIN | ADMIN | PASTEUR | PROTOCOLE | FINANCE | SECRETARIAT | MEMBRE
        status TEXT NOT NULL DEFAULT 'ACTIVE',   -- ACTIVE | DISABLED
        is_superadmin INTEGER NOT NULL DEFAULT 0,
        can_publish INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        UNIQUE(church_id, phone),
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE
    );
    """)

    # --- audit log ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # --- settings (per church) ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS church_settings (
        church_id TEXT PRIMARY KEY,
        culte_open INTEGER NOT NULL DEFAULT 0,
        allow_self_register INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE
    );
    """)

    # --- members ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT NOT NULL,
        code TEXT NOT NULL,
        fullname TEXT NOT NULL,
        phone TEXT NOT NULL,
        quartier TEXT,
        address TEXT,
        statut TEXT NOT NULL DEFAULT 'ACTIF', -- ACTIF, INACTIF, JEUNES, CHORALE, ...
        created_at TEXT NOT NULL,
        UNIQUE(church_id, code),
        UNIQUE(church_id, phone),
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE
    );
    """)

    # --- guests entries (protocol) ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT NOT NULL,
        created_by_user_id INTEGER NOT NULL,
        member_id INTEGER,                   -- if guest is linked to an existing member (optional)
        member_code TEXT,                    -- stored for quick lookup (optional)
        guest_name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE,
        FOREIGN KEY(created_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE SET NULL
    );
    """)

    # --- finance donations ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT NOT NULL,
        created_by_user_id INTEGER NOT NULL,
        donor_name TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL DEFAULT 'DON',     -- DON, OFFRANDE, DIME, DEPENSE
        message TEXT,
        published INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE,
        FOREIGN KEY(created_by_user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # --- announcements/notifications ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT NOT NULL,
        created_by_user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        target_statut TEXT DEFAULT 'ALL',      -- ALL or JEUNES, ACTIF, etc.
        created_at TEXT NOT NULL,
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE,
        FOREIGN KEY(created_by_user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # --- relations (pastor only) ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        church_id TEXT NOT NULL,
        created_by_user_id INTEGER NOT NULL,
        type TEXT NOT NULL DEFAULT 'FIANCAILLES', -- FIANCAILLES | MARIAGE
        statut TEXT NOT NULL DEFAULT 'OPEN',      -- OPEN | CLOSED
        garcon_member_id INTEGER,
        fille_member_id INTEGER,
        garcon_name TEXT,                         -- if manual
        fille_name TEXT,                          -- if manual
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(church_id) REFERENCES churches(id) ON DELETE CASCADE,
        FOREIGN KEY(created_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(garcon_member_id) REFERENCES members(id) ON DELETE SET NULL,
        FOREIGN KEY(fille_member_id) REFERENCES members(id) ON DELETE SET NULL
    );
    """)

    conn.commit()
    conn.close()


def audit_log(db_path, church_id, user_id, action, details=""):
    conn = connect(db_path)
    conn.execute(
        "INSERT INTO audit (church_id, user_id, action, details, created_at) VALUES (?,?,?,?,?)",
        (church_id, user_id, action, details, now_iso())
    )
    conn.commit()
    conn.close()


def ensure_db(db_path=DB_NAME):
    init_db(db_path)
    seed_defaults(db_path)


def seed_defaults(db_path=DB_NAME):
    conn = connect(db_path)
    cur = conn.cursor()

    # create CH001 if not exists
    cur.execute("SELECT id FROM churches WHERE id=?", ("CH001",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO churches (id, name, status, activation_code, created_at) VALUES (?,?,?,?,?)",
            ("CH001", "Eglise Démo CH001", "ACTIVE", "0000", now_iso())
        )
        cur.execute(
            "INSERT INTO church_settings (church_id, culte_open, allow_self_register, created_at) VALUES (?,?,?,?)",
            ("CH001", 0, 0, now_iso())
        )

    # SUPER ADMIN (no church_id)
    cur.execute("SELECT id FROM users WHERE is_superadmin=1 LIMIT 1")
    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO users (church_id, phone, fullname, password, role, status, is_superadmin, can_publish, created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (None, "0990000000", "SUPER ADMIN", "1234", "SUPER_ADMIN", "ACTIVE", 1, 1, now_iso()))

    # Default users for CH001
    defaults = [
        ("CH001", "0811111111", "ADMIN CH001", "1111", "ADMIN", 1),
        ("CH001", "0822222222", "PASTEUR CH001", "2222", "PASTEUR", 1),
        ("CH001", "0833333333", "PROTOCOLE CH001", "3333", "PROTOCOLE", 0),
        ("CH001", "0844444444", "FINANCE CH001", "4444", "FINANCE", 1),
        ("CH001", "0855555555", "SECRETARIAT CH001", "5555", "SECRETARIAT", 0),
        ("CH001", "0866666666", "MEMBRE DEMO", "6666", "MEMBRE", 0),
    ]
    for church_id, phone, fullname, pwd, role, can_publish in defaults:
        cur.execute("SELECT id FROM users WHERE church_id=? AND phone=?", (church_id, phone))
        if cur.fetchone() is None:
            cur.execute("""
                INSERT INTO users (church_id, phone, fullname, password, role, status, is_superadmin, can_publish, created_at)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (church_id, phone, fullname, pwd, role, "ACTIVE", 0, can_publish, now_iso()))

    conn.commit()
    conn.close()
