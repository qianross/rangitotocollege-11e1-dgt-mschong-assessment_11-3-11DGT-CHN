import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import subprocess
import os

def save_username(name):
    # Only add username if not already present
    usernames = []
    if os.path.exists("Python/username.txt"):
        with open("Python/username.txt", "r") as f:
            for line in f:
                if ":" in line:
                    usernames.append(line.split(":")[0].strip())
                else:
                    usernames.append(line.strip())
    if name not in usernames:
        with open("Python/username.txt", "a") as f:
            f.write(f"{name}:\n")

def get_username():
    # Return the last entered username (current session)
    if os.path.exists("Python/username.txt"):
        with open("Python/username.txt", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                if ":" in last_line:
                    return last_line.split(":")[0]
                return last_line
    return None

def ask_username():
    # Check if username already exists
    name = simpledialog.askstring("Enter Name", "Please enter your name:")
    if name:
        save_username(name)
        return name
    else:
        messagebox.showerror("Error", "Name is required!")
        root.destroy()

def parse_leaderboard():
    # Parse the username.txt file to extract scores and times
    leaderboard = {"game1": [], "game2": [], "game3": []}
    times = {"game1": {}, "game2": {}, "game3": {}}
    grids = {"game2": {}}
    mines = {"game2": {}}  # Add mines storage for game2
    if os.path.exists("Python/username.txt"):
        with open("Python/username.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                user, games = line.split(":", 1)
                scores = {}
                for pair in games.split(","):
                    if "=" in pair:
                        g, s = pair.split("=")
                        scores[g.strip()] = s.strip()
                for game in ["game1", "game2", "game3"]:
                    if game in scores:
                        try:
                            leaderboard[game].append((user, int(scores[game])))
                        except ValueError:
                            leaderboard[game].append((user, 0))
                    time_key = f"{game}_time"
                    if time_key in scores:
                        times[game][user] = scores[time_key]
                if "game2_grid" in scores:
                    grids["game2"][user] = scores["game2_grid"]
                if "game2_mines" in scores:
                    mines["game2"][user] = scores["game2_mines"]
    for game in leaderboard:
        leaderboard[game].sort(key=lambda x: x[1], reverse=True)
    return leaderboard, times, grids, mines

def open_leaderboard():
    # Create a new window for the leaderboard
    leaderboard_win = tk.Toplevel(root)
    leaderboard_win.title("Leaderboard")
    leaderboard_win.geometry("400x350")

    notebook = ttk.Notebook(leaderboard_win)
    notebook.pack(fill="both", expand=True)

    leaderboard, times, grids, mines = parse_leaderboard()

    # Game 1 tab
    frame1 = tk.Frame(notebook)
    notebook.add(frame1, text="Game1")
    tk.Label(frame1, text="Game1 Leaderboard", font=("Arial", 14, "bold")).pack(pady=10)
    if leaderboard["game1"]:
        for idx, (user, score) in enumerate(leaderboard["game1"][:10], start=1):
            time_str = times["game1"].get(user, "N/A")
            tk.Label(
                frame1,
                text=f"{idx}. {user} | score: {score} | time: {time_str}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=20)
    else:
        tk.Label(frame1, text="No scores yet.", font=("Arial", 12)).pack(pady=20)

    # Game 2 tab
    frame2 = tk.Frame(notebook)
    notebook.add(frame2, text="Game2")
    tk.Label(frame2, text="Game2 Leaderboard", font=("Arial", 14, "bold")).pack(pady=10)
    if times["game2"]:
        sorted_times = sorted(times["game2"].items(), key=lambda x: int(x[1]) if x[1].isdigit() else 0)
        for idx, (user, time_val) in enumerate(sorted_times[:10], start=1):
            grid_val = grids["game2"].get(user, "N/A")
            mines_val = mines["game2"].get(user, "N/A")
            tk.Label(
                frame2,
                text=f"{idx}. {user} | time: {time_val} | grid: {grid_val} | mines: {mines_val}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=20)
    else:
        tk.Label(frame2, text="No times yet.", font=("Arial", 12)).pack(pady=20)

    # Game 3 tab
    frame3 = tk.Frame(notebook)
    notebook.add(frame3, text="Game3")
    tk.Label(frame3, text="Game3 Leaderboard", font=("Arial", 14, "bold")).pack(pady=10)
    if leaderboard["game3"]:
        for idx, (user, score) in enumerate(leaderboard["game3"][:10], start=1):
            tk.Label(
                frame3,
                text=f"{idx}. {user} - {score}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=20)
    else:
        tk.Label(frame3, text="No scores yet.", font=("Arial", 12)).pack(pady=20)

def launch_game(filename):
    subprocess.Popen(["python", filename])

root = tk.Tk()
root.title("Main Menu")
root.geometry("400x300")

username = ask_username()

tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 16)).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=30)

btn1 = tk.Button(frame, text="Leaderboard", width=20, height=3, command=open_leaderboard)
btn1.grid(row=0, column=0, padx=10, pady=10)

btn2 = tk.Button(frame, text="Game 1", width=20, height=3, command=lambda: launch_game("Python\game1.py"))
btn2.grid(row=0, column=1, padx=10, pady=10)

btn3 = tk.Button(frame, text="Game 2", width=20, height=3, command=lambda: launch_game("Python\game2.py"))
btn3.grid(row=1, column=0, padx=10, pady=10)

btn4 = tk.Button(frame, text="Game 3", width=20, height=3, command=lambda: launch_game("Python\game3.py"))
btn4.grid(row=1, column=1, padx=10, pady=10)

root.mainloop()