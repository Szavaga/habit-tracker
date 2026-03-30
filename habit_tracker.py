import json
import os
from datetime import date

FILE = "habits.json"

def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE) as f:
        return json.load(f)

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_habit(data, name):
    if name not in data:
        data[name] = []
        print(f"Added habit: {name}")
    else:
        print("Habit already exists.")

def mark_done(data, name):
    today = str(date.today())
    if name not in data:
        print("Habit not found.")
        return
    if today not in data[name]:
        data[name].append(today)
        print(f"✓ Marked '{name}' as done today!")
    else:
        print("Already marked today.")

def show_habits(data):
    if not data:
        print("No habits yet.")
        return
    today = str(date.today())
    for habit, days in data.items():
        done_today = "✓" if today in days else "✗"
        print(f"  {done_today} {habit} — {len(days)} day(s) logged")

def main():
    data = load()
    while True:
        print("\n1. Add habit\n2. Mark done\n3. View habits\n4. Quit")
        choice = input("> ").strip()
        if choice == "1":
            add_habit(data, input("Habit name: ").strip())
            save(data)
        elif choice == "2":
            mark_done(data, input("Habit name: ").strip())
            save(data)
        elif choice == "3":
            show_habits(data)
        elif choice == "4":
            break

main()