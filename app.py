from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb

app = Flask(__name__)
app.secret_key = "secret123"

db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="5399",
    db="phonepe_splitwise"
)

cursor = db.cursor()

# ---------------- ROOT (REDIRECT ONLY) ----------------
@app.route("/")
def root():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]

        cur = db.cursor()
        cur.execute(
            "SELECT id, password FROM users WHERE mobile=%s",
            (mobile,)
        )
        user = cur.fetchone()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        password = generate_password_hash(request.form["password"])

        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO users(name, mobile, password) VALUES (%s,%s,%s)",
                (name, mobile, password)
            )
            db.commit()
        except:
            return "Mobile already exists"

        return redirect("/login")

    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]

    cursor.execute("SELECT * FROM split_group")
    split_group = cursor.fetchall()

    cursor.execute("""
        SELECT COALESCE(SUM(balance),0)
        FROM expense_splits
        WHERE user_id=%s
    """, (uid,))
    balance = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        split_group=split_group,
        balance=balance
    )

# ---------------- CREATE GROUP ----------------
@app.route("/create_group", methods=["POST"])
def create_group():
    if "user_id" not in session:
        return redirect("/login")

    name = request.form["name"]
    members = request.form.getlist("members")

    if len(members) < 2:
        return "Group must have more than 1 member"
                
    cursor.execute(
        "INSERT INTO split_group(name,created_by) VALUES(%s,%s)",
        (name, session["user_id"])
    )
    db.commit()

    gid = cursor.lastrowid

    for m in members:
        cursor.execute(
            "INSERT INTO group_members VALUES(%s,%s)",
            (gid, m)
        )

    db.commit()
    return redirect("/dashboard")

# ---------------- ADD EXPENSE ----------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    if "user_id" not in session:
        return redirect("/login")

    gid = request.form["group_id"]
    desc = request.form["desc"]
    total = float(request.form["amount"])

    if total <= 0:
        return "Amount must be greater than zero"

    cursor.execute(
        "SELECT user_id FROM group_members WHERE group_id=%s",
        (gid,)
    )
    members = cursor.fetchall()

    share = round(total / len(members), 2)
    paid_by = session["user_id"]

    cursor.execute(
        """INSERT INTO expenses
           (group_id, description, total_amount, paid_by)
           VALUES (%s,%s,%s,%s)""",
        (gid, desc, total, paid_by)
    )
    db.commit()

    eid = cursor.lastrowid

    for m in members:
        uid = m[0]
        paid = total if uid == paid_by else 0
        balance = paid - share

        cursor.execute(
            "INSERT INTO expense_splits VALUES(%s,%s,%s,%s,%s)",
            (eid, uid, share, paid, balance)
        )

    db.commit()
    return redirect("/dashboard")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
