from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

# 仮ユーザーデータ（DBの代わり）
users = {
    "admin": {"password": "adminn", "points": 0, "is_admin": True},
    "alice": {"password": "alice", "points": 100, "is_admin": False},
    "bob":   {"password": "bob",   "points": 50,  "is_admin": False},
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["username"] = user["username"]
            return redirect("/dashboard")

    return """
    <h2>ログイン</h2>
    <form method="post">
        <input name="username">
        <input name="password">
        <button>ログイン</button>
    </form>
    """

@app.route("/dashboard")
def dashboard():
    username = session.get("username")
    if not username:
        return redirect("/")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()

    users = conn.execute(
        "SELECT username FROM users"
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        username=user["username"],
        points=user["points"],
        is_admin=user["is_admin"],
        users=[u["username"] for u in users]
    )


@app.route("/send", methods=["POST"])
def send():
    username = session.get("username")
    to = request.form["to"]
    amount = int(request.form["amount"])

    conn = get_db()
    cur = conn.cursor()

    sender = cur.execute(
        "SELECT points FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if sender["points"] < amount or amount <= 0:
        conn.close()
        return "エラー"

    cur.execute(
        "UPDATE users SET points = points - ? WHERE username=?",
        (amount, username)
    )
    cur.execute(
        "UPDATE users SET points = points + ? WHERE username=?",
        (amount, to)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/add", methods=["POST"])
def add():
    username = session.get("username")
    to = request.form["to"]
    amount = int(request.form["amount"])

    conn = get_db()
    cur = conn.cursor()

    admin = cur.execute(
        "SELECT is_admin FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if not admin["is_admin"]:
        conn.close()
        return "権限なし"

    cur.execute(
        "UPDATE users SET points = points + ? WHERE username=?",
        (amount, to)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


def get_db():
    conn = sqlite3.connect("point.db")
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

