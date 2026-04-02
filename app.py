from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey123"

HABITS_FILE = "habits.json"
USERS_FILE = "users.json"

def load_habits():
    if not os.path.exists(HABITS_FILE):
        return {}
    with open(HABITS_FILE) as f:
        return json.load(f)

def save_habits(data):
    with open(HABITS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calculate_streak(days):
    if not days:
        return 0
    sorted_days = sorted(days, reverse=True)
    streak = 0
    check_date = date.today()
    for day in sorted_days:
        if str(check_date) == day:
            streak += 1
            check_date = date.fromordinal(check_date.toordinal() - 1)
        else:
            break
    return streak

@app.route("/leaderboard")
def leaderboard():
    if "username" not in session:
        return redirect("/login")
    all_habits = load_habits()
    rankings = []
    for username, habits in all_habits.items():
        total_streak = sum(calculate_streak(days) for days in habits.values())
        total_days = sum(len(days) for days in habits.values())
        rankings.append({
            "username": username,
            "total_streak": total_streak,
            "total_days": total_days,
            "habit_count": len(habits)
        })
    rankings.sort(key=lambda x: x["total_streak"], reverse=True)
    return render_template("leaderboard.html", rankings=rankings, current_user=session["username"])
    
@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    all_habits = load_habits()
    habits = all_habits.get(username, {})
    today = str(date.today())
    streaks = {habit: calculate_streak(days) for habit, days in habits.items()}
    return render_template("index.html", habits=habits, today=today, username=username, streaks=streaks)

@app.route("/add", methods=["POST"])
def add():
    if "username" not in session:
        return redirect("/login")
    name = request.form.get("name", "").strip()
    username = session["username"]
    all_habits = load_habits()
    if username not in all_habits:
        all_habits[username] = {}
    if name and name not in all_habits[username]:
        all_habits[username][name] = []
        save_habits(all_habits)
    return redirect("/")

@app.route("/done/<name>")
def mark_done(name):
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    today = str(date.today())
    all_habits = load_habits()
    if username in all_habits and name in all_habits[username]:
        if today not in all_habits[username][name]:
            all_habits[username][name].append(today)
            save_habits(all_habits)
    return redirect("/")

@app.route("/delete/<name>")
def delete(name):
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    all_habits = load_habits()
    if username in all_habits and name in all_habits[username]:
        del all_habits[username][name]
        save_habits(all_habits)
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()
        if username in users:
            error = "Username already exists."
        elif not username or not password:
            error = "Please fill in all fields."
        else:
            users[username] = generate_password_hash(password)
            save_users(users)
            return redirect("/login")
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()
        if username not in users or not check_password_hash(users[username], password):
            error = "Invalid username or password."
        else:
            session["username"] = username
            return redirect("/")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)