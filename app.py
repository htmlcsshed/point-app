from flask import Flask, request, redirect, session, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = "point-app-secret"

def get_db():
    conn = sqlite3.connect("point.db")
    conn.row_factory = sqlite3.Row
    return conn

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
            session["user"] = user["username"]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users VALUES (?, ?, 100, 0)",
                (username, password)
            )
            conn.commit()
        except:
            return "既に存在します"
        finally:
            conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    username = session.get("user")
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
    frm = session.get("user")
    to = request.form["to"]
    amount = int(request.form["amount"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET points = points - ? WHERE username=?", (amount, frm))
    cur.execute("UPDATE users SET points = points + ? WHERE username=?", (amount, to))

    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/add", methods=["POST"])
def add():
    username = session.get("user")
    if not username:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    me = cur.execute(
        "SELECT is_admin FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if me["is_admin"] != 1:
        conn.close()
        return "権限なし"

    to = request.form["to"]
    amount = int(request.form["amount"])

    cur.execute(
        "UPDATE users SET points = points + ? WHERE username=?",
        (amount, to)
    )

    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/admin")
def admin():
    username = session.get("user")
    if not username:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    me = cur.execute(
        "SELECT is_admin FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if me["is_admin"] != 1:
        conn.close()
        return "管理者専用"

    users = cur.execute(
        "SELECT username, points, is_admin FROM users"
    ).fetchall()
    conn.close()

    return render_template("admin.html", users=users)

@app.route("/delete/<username>")
def delete(username):
    me = session.get("user")
    if not me:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    admin = cur.execute(
        "SELECT is_admin FROM users WHERE username=?",
        (me,)
    ).fetchone()

    if admin["is_admin"] != 1:
        conn.close()
        return "権限なし"

    cur.execute(
        "DELETE FROM users WHERE username=? AND is_admin=0",
        (username,)
    )
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    me = session.get("user")
    if not me:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    admin = cur.execute(
        "SELECT is_admin FROM users WHERE username=?",
        (me,)
    ).fetchone()

    if admin["is_admin"] != 1:
        conn.close()
        return "管理者のみ"

    if request.method == "POST":
        pw = request.form["password"]
        cur.execute(
            "UPDATE users SET password=? WHERE username=?",
            (pw, me)
        )
        conn.commit()
        conn.close()
        return redirect("/admin")

    conn.close()
    return render_template("change_password.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin/add_user", methods=["POST"])
def admin_add_user():
    me = session.get("user")
    if not me:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    # 管理者チェック
    admin = cur.execute(
        "SELECT is_admin FROM users WHERE username=?",
        (me,)
    ).fetchone()

    if admin["is_admin"] != 1:
        conn.close()
        return "権限がありません"

    username = request.form["username"]
    password = request.form["password"]
    points = int(request.form["points"])

    try:
        cur.execute(
            "INSERT INTO users VALUES (?, ?, ?, 0)",
            (username, password, points)
        )
        conn.commit()
    except:
        conn.close()
        return "そのユーザー名は既に存在します"

    conn.close()
    return redirect("/admin")


if __name__=="__main__":
    app.run()
