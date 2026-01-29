import sqlite3

conn = sqlite3.connect("point.db")
c = conn.cursor()

c.execute("""
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT,
    points INTEGER,
    is_admin INTEGER
)
""")

# 初期データ
users = [
    ("admin", "admin", 0, 1),
    ("alice", "alice", 100, 0),
    ("bob",   "bob",   50, 0),
]

c.executemany(
    "INSERT INTO users VALUES (?, ?, ?, ?)",
    users
)

conn.commit()
conn.close()

print("DB initialized")

