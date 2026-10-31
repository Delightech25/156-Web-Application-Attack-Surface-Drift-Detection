from flask import Flask, render_template, request, redirect, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secure_driveby_key"

USERS_FILE = "users.json"

# Create file if not exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)


def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ---------------- Login ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and check_password_hash(users[username]["password"], password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# ---------------- Register ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            return render_template("register.html", error="User already exists")

        hashed_password = generate_password_hash(password)

        users[username] = {
            "password": hashed_password,
            "history": []
        }

        save_users(users)
        return redirect("/")

    return render_template("register.html")


# ---------------- Dashboard ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    users = load_users()
    username = session["user"]
    result = None

    if request.method == "POST":
        popups = int(request.form["popups"])
        auto_download = int(request.form["auto_download"])
        redirects = int(request.form["redirects"])
        suspicious_scripts = int(request.form["suspicious_scripts"])
        hidden_iframe = int(request.form["hidden_iframe"])

        score = (popups * 2) + (auto_download * 5) + \
                (redirects * 3) + (suspicious_scripts * 4) + \
                (hidden_iframe * 5)

        if score <= 10:
            risk = "Low Risk"
        elif score <= 20:
            risk = "Medium Risk"
        else:
            risk = "High Risk"

        result = {"score": score, "risk": risk}
        users[username]["history"].append(result)
        save_users(users)

    history = users[username]["history"]

    scores = [item["score"] for item in history]

    # 🔥 Pie Chart Data
    low = len([i for i in history if i["risk"] == "Low Risk"])
    medium = len([i for i in history if i["risk"] == "Medium Risk"])
    high = len([i for i in history if i["risk"] == "High Risk"])

    return render_template("dashboard.html",
                           user=username,
                           result=result,
                           history=history,
                           scores=scores,
                           low=low,
                           medium=medium,
                           high=high)


    


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)