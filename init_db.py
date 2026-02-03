import sqlite3

conn = sqlite3.connect("point.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    points INTEGER NOT NULL,
    is_admin INTEGER NOT NULL
)
""")

# 初期管理者（存在しなければ作成）
admin_user = "admin"
admin_pass = "admin"

cur.execute(
    "SELECT * FROM users WHERE username=?",
    (admin_user,)
)

if not cur.fetchone():
    cur.execute(
        "INSERT INTO users VALUES (?, ?, 1000, 1)",
        (admin_user, admin_pass)
    )

conn.commit()
conn.close()

print("DB初期化完了")

