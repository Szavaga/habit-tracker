from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import date

app = Flask(__name__)
# new (add this import at the top with the others)
from dotenv import load_dotenv
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

HABITS_FILE = "habits.json"
USERS_FILE = "users.json"
# Loads all habits from the JSON file. Returns an empty dict if the file doesn't exist yet.
def load_habits(): 
    if not os.path.exists(HABITS_FILE):
        return {}
    with open(HABITS_FILE) as f:
        return json.load(f)
# Saves the given habits data to JSON file.
def save_habits(data):
    with open(HABITS_FILE, "w") as f:
        json.dump(data, f, indent=2)
# Loads all users from the JSON file. Returns an empty dict if the file doesn't exist yet.  
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)
# Saves the given users data to JSON file.
def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)
# Calculates the current streak of consecutive days for a habit based on the list of days it was completed. 
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
#szóval az @app.route decorator. A .append egy elemet ad a lista végére. az utolsó két sor sort sorba rendezi a listát key=labda x: "" ez mondja meg mi alapján döntsön revers=true pedig fordított sorrendben rendezi. A render_template pedig megjeleníti a leaderboard.html oldalt a rankings és current_user változókkal.
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
# The index route checks if the user is logged in, loads their habits, calculates streaks, and renders the main page. The add route allows users to add new habits. The mark_done route marks a habit as completed for today. The delete route removes a habit. The register and login routes handle user authentication, and the logout route clears the session.
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
# The add route checks if the user is logged in, gets the habit name from the form, and adds it to the user's habits if it doesn't already exist. It then redirects back to the main page.
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
# The mark_done route checks if the user is logged in, gets the habit name from the URL, and marks it as completed for today if it exists. It then redirects back to the main page.
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
# The delete route checks if the user is logged in, gets the habit name from the URL, and deletes it from the user's habits if it exists. It then redirects back to the main page.
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
# The register route handles user registration. It checks if the username already exists, validates the input, and saves the new user with a hashed password. If registration is successful, it redirects to the login page.
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
# The login route handles user authentication. It checks if the username exists and if the password is correct. If authentication is successful, it stores the username in the session and redirects to the main page. If authentication fails, it shows an error message.
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
# The logout route clears the user's session and redirects to the login page.
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)