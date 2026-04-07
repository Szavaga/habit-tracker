import json
import os
from datetime import date

FILE = "habits.json"
# Loads all data from the JSON file. Returns an empty dict if the file doesn't exist yet.
def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE) as f:
        return json.load(f)
# Saves the given data to JSON file.
def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
# Adds a new habit with the given name to the data if it doesn't already exist.
def add_habit(data, name):
    if not name:
        print("Habit name cannot be empty.")
        return
    if name not in data:
        data[name] = []
        print(f"Added habit: {name}")
    else:
        print("Habit already exists.")
# Marks the habit with the given name as done for today if it exists and hasn't been marked yet.
def mark_done(data, name):
    if not name:
        print("Habit name cannot be empty.")
        return
    today = str(date.today())
    if name not in data:
        print("Habit not found.")
        return
    if today not in data[name]:
        data[name].append(today)
        print(f"✓ Marked '{name}' as done today!")
    else:
        print("Already marked today.")
# Displays all habits with their completion status for today and total days logged.
def show_habits(data):
    if not data:
        print("No habits yet.")
        return
    today = str(date.today())
    for habit, days in data.items():
        done_today = "✓" if today in days else "✗"
        print(f"  {done_today} {habit} — 🔥 {calculate_streak(days)} day streak ({len(days)} total)")

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
# The main function runs the command-line interface for the habit tracker, allowing users to add habits, mark them as done, view their habits, or quit the program.
def main():
    data = load()
    while True:
        print("\n1. Add habit\n2. Mark done\n3. View habits\n4. Delete habit\n5. Quit")
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
            delete_habit(data, input("Habit name to delete: ").strip())
            save(data)
        elif choice == "5":
            break

def delete_habit(data, name):
    if name in data:
        del data[name]
        print(f"Deleted habit: {name}")
    else:
        print("Habit not found.")
main()