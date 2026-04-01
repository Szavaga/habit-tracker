from flask import Flask, render_template, request, redirect
import json
import os
from datetime import date

app = Flask(__name__)
FILE = "habits.json"

def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE) as f:
        return json.load(f)

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/delete/<name>")
def delete(name):
    data = load()
    if name in data:
        del data[name]
        save(data)
    return redirect("/")
    
@app.route("/")
def index():
    data = load()
    today = str(date.today())
    return render_template("index.html", habits=data, today=today)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    data = load()
    if name and name not in data:
        data[name] = []
        save(data)
    return redirect("/")

@app.route("/done/<name>")
def mark_done(name):
    data = load()
    today = str(date.today())
    if name in data and today not in data[name]:
        data[name].append(today)
        save(data)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)